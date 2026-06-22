import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_ADI = "qwen2.5:7b"

def sistem_promptu_hazirla(yemek_bilgisi=None):
    # system_prompt.txt oku
    from pathlib import Path
    prompt_dosyasi = Path(__file__).parent.parent / "data" / "system_prompt.txt"
    with open(prompt_dosyasi, "r", encoding="utf-8") as f:
        sistem_promptu = f.read()

    # eğer yemek analiz edildiyse bağlamı ekle
    if yemek_bilgisi:
        baglam = f"""
Kullanıcı az önce şu yemeği yedi:
- Yemek: {yemek_bilgisi.get('display_name', '')}
- Kalori: {yemek_bilgisi.get('kalori', 0):.0f} kcal
- Protein: {yemek_bilgisi.get('protein', 0):.1f} g
- Yağ: {yemek_bilgisi.get('yag', 0):.1f} g
- Karbonhidrat: {yemek_bilgisi.get('karb', 0):.1f} g
- Malzemeler: {', '.join(yemek_bilgisi.get('ingredients', []))}
"""
        sistem_promptu += baglam

    return sistem_promptu

def mesaj_gonder(kullanici_mesaji, sohbet_gecmisi=None, yemek_bilgisi=None):
    sistem_promptu = sistem_promptu_hazirla(yemek_bilgisi)

    # sohbet geçmişini prompt'a ekle
    gecmis_metni = ""
    if sohbet_gecmisi:
        for mesaj in sohbet_gecmisi[-6:]:  # son 6 mesajı al
            if mesaj["rol"] == "kullanici":
                gecmis_metni += f"Kullanıcı: {mesaj['icerik']}\n"
            else:
                gecmis_metni += f"Asistan: {mesaj['icerik']}\n"

    tam_prompt = f"{sistem_promptu}\n\nÖNEMLİ: Sadece Türkçe cevap ver!\n\n{gecmis_metni}Kullanıcı: {kullanici_mesaji}\nAsistan (Türkçe):"

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_ADI,
                "prompt": tam_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 200,
                }
            },
            timeout=120
        )

        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return "Bağlantı hatası, tekrar dene."

    except requests.exceptions.ConnectionError:
        return "Ollama bağlantısı kurulamadı. 'ollama serve' çalışıyor mu?"
    except requests.exceptions.Timeout:
        return "Cevap geç geldi, tekrar dene."
    except Exception as e:
        return f"Hata: {str(e)}"

def tarif_uyarla(tarif, kullanici_metni, olmayan_malzemeler=None):
    olmayan_metin = ""
    if olmayan_malzemeler:
        olmayan_metin = "\nKULLANICIDA OLMAYAN: " + ", ".join(olmayan_malzemeler)

    sistem_prompt = """Sen bir mutfak şefisin. Tarifte BULUNAN ama kullanıcıda OLMAYAN malzemeler için alternatif öneriyorsun.
KURALLAR (KATI):
1. SADECE TEK CÜMLE yaz.
2. Format: "X yerine Y kullanabilirsiniz."
3. Sadece kullanıcıda OLMAYAN malzemeler için öneri yap.
4. Olmayan malzeme bu tarifte yoksa, "Bu tarifte zaten X yok, olduğu gibi yapabilirsiniz." de.
5. ASLA emoji, ASLA liste, ASLA iki cümle.
6. Türkçe imla kurallarına uy.

DOĞRU ÖRNEKLER:
- "Sarımsak yerine yarım çay kaşığı zencefil tozu kullanabilirsiniz."
- "Süt yerine badem sütü veya yulaf sütü kullanabilirsiniz."
- "Bu tarifte zaten sarımsak yok, olduğu gibi yapabilirsiniz."

YANLIŞ ÖRNEKLER (BÖYLE YAPMA):
- "1 adet soğan yerine 1 adet soğan parçalı kullanabilirsiniz." (mantıksız)
- "💡 X yerine Y." (emoji yok)
- İki satırlı cevap (tek satır olmalı)"""

    kullanici_prompt = f"""TARİF: {tarif['ad']}
TARİFTEKİ MALZEMELER: {tarif['malzemeler_metin']}
{olmayan_metin}

Kullanıcıda olmayan malzeme için tarifte ne kullanılabilir? TEK CÜMLE yaz."""

    import requests
    try:
        cevap = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen2.5:7b",
                "messages": [
                    {"role": "system", "content": sistem_prompt},
                    {"role": "user", "content": kullanici_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 100,
                    "top_p": 0.8,
                }
            },
            timeout=45
        )
        if cevap.status_code == 200:
            metin = cevap.json().get("message", {}).get("content", "").strip()
            # Post-process: Birden fazla ampul, satır başı işaretleri vs temizle
            import re
            # Tum ampul emojilerini temizle (UI tarafinda kendi ekleyecegiz)
            metin = re.sub(r"💡\s*", "", metin)
            metin = re.sub(r"^[-*•]\s*", "", metin, flags=re.MULTILINE)
            # Cok satirliysa ilk anlamli satiri al
            satirlar = [s.strip() for s in metin.split("\n") if s.strip()]
            if satirlar:
                # Tum satirlari tek cumle olarak birlestir (en fazla 2)
                metin = " ".join(satirlar[:2])
            return metin.strip()
    except Exception as e:
        return f"(Uyarlama yapılamadı: {e})"

    return None

def ollama_calisiyor_mu():
    try:
        r = requests.get("http://localhost:11434/", timeout=3)
        return r.status_code == 200
    except:
        return False