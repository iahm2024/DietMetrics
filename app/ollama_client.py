import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_ADI = "qwen2.5:7b"

def sistem_promptu_hazirla(yemek_bilgisi=None, kullanici_profili=None, gunluk_durum=None):
    # system_prompt.txt oku
    from pathlib import Path
    prompt_dosyasi = Path(__file__).parent.parent / "data" / "system_prompt.txt"
    with open(prompt_dosyasi, "r", encoding="utf-8") as f:
        sistem_promptu = f.read()

    # Kullanici profil bilgisi (varsa)
    if kullanici_profili:
        profil_satirlari = []
        ad = kullanici_profili.get("ad")
        if ad:
            profil_satirlari.append(f"- İsim: {ad}")

        yas = kullanici_profili.get("yas")
        if yas:
            profil_satirlari.append(f"- Yaş: {yas}")

        cinsiyet = kullanici_profili.get("cinsiyet")
        if cinsiyet:
            profil_satirlari.append(f"- Cinsiyet: {cinsiyet}")

        boy = kullanici_profili.get("boy_cm")
        if boy:
            profil_satirlari.append(f"- Boy: {boy} cm")

        kilo = kullanici_profili.get("kilo_kg")
        if kilo:
            profil_satirlari.append(f"- Kilo: {kilo} kg")

        hedef_kal = kullanici_profili.get("gunluk_hedef")
        if hedef_kal:
            profil_satirlari.append(f"- Günlük kalori hedefi: {hedef_kal} kcal")

        hedef_pro = kullanici_profili.get("hedef_protein_g")
        if hedef_pro:
            profil_satirlari.append(f"- Günlük protein hedefi: {hedef_pro} g")

        if profil_satirlari:
            sistem_promptu += "\n\nKULLANICI PROFİLİ (sana bu bilgi verildi, kullanıcı yeniden yazmana gerek yok):\n"
            sistem_promptu += "\n".join(profil_satirlari)
            sistem_promptu += "\n\nKalori hesabı yapman gerekirse bu bilgileri kullan, kullanıcıdan tekrar isteme."

    # Bugunun durumu (varsa)
    if gunluk_durum:
        toplam_kal = gunluk_durum.get("toplam_kalori", 0)
        hedef = gunluk_durum.get("hedef", 0)
        kalan = max(hedef - toplam_kal, 0) if hedef else 0
        ogunler = gunluk_durum.get("ogunler", [])

        sistem_promptu += f"\n\nBUGÜNÜN DURUMU:\n"
        sistem_promptu += f"- Toplam alınan kalori: {toplam_kal:.0f} kcal\n"
        if hedef:
            sistem_promptu += f"- Hedef: {hedef} kcal\n"
            sistem_promptu += f"- Kalan: {kalan:.0f} kcal\n"
        sistem_promptu += f"- Bugün yenen öğün sayısı: {len(ogunler)}\n"

        if ogunler:
            sistem_promptu += "\nBugün yedikleri (saat sırasıyla):\n"
            for o in ogunler:
                adet_txt = f" × {o.get('adet', 1)}" if o.get("adet", 1) > 1 else ""
                sistem_promptu += (
                    f"- {o.get('saat', '?')} · {o.get('yemek', '?')}{adet_txt} "
                    f"({o.get('gram', 0):.0f} g, {o.get('kalori', 0):.0f} kcal)\n"
                )

        sistem_promptu += "\nKullanıcı 'bugün ne yedim', 'kaç kalori aldım', 'ne yiyebilirim' gibi sorular sorarsa bu bilgilere göre cevap ver."

    # Eger yemek analiz edildiyse baglam
    if yemek_bilgisi:
        baglam = f"""

KULLANICININ AZ ÖNCE ANALİZ ETTİĞİ YEMEK:
- Yemek: {yemek_bilgisi.get('yemek', '')}
- Kalori: {yemek_bilgisi.get('kalori', 0):.0f} kcal
- Protein: {yemek_bilgisi.get('protein', 0):.1f} g
- Yağ: {yemek_bilgisi.get('yag', 0):.1f} g
- Karbonhidrat: {yemek_bilgisi.get('karb', 0):.1f} g
"""
        sistem_promptu += baglam

    return sistem_promptu

def mesaj_gonder(kullanici_mesaji, sohbet_gecmisi=None, yemek_bilgisi=None,
                 kullanici_profili=None, gunluk_durum=None):
    sistem_promptu = sistem_promptu_hazirla(
        yemek_bilgisi=yemek_bilgisi,
        kullanici_profili=kullanici_profili,
        gunluk_durum=gunluk_durum
    )

    # Sohbet gecmisi
    gecmis_metni = ""
    if sohbet_gecmisi:
        for mesaj in sohbet_gecmisi[-6:]:
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
                    "num_predict": 250,
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

    try:
        cevap = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": MODEL_ADI,
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
            import re
            metin = re.sub(r"💡\s*", "", metin)
            metin = re.sub(r"^[-*•]\s*", "", metin, flags=re.MULTILINE)
            satirlar = [s.strip() for s in metin.split("\n") if s.strip()]
            if satirlar:
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