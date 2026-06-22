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
                    "temperature": 0.7,
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

def ollama_calisiyor_mu():
    try:
        r = requests.get("http://localhost:11434/", timeout=3)
        return r.status_code == 200
    except:
        return False