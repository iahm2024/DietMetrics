import re
import json
import requests
from pathlib import Path
 
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_ADI = "qwen2.5:7b"
 
# Saçmalama tespiti için bilinen sorunlu kelimeler
BOZUK_ISARETLER = [
    "ovomalt", "tercümeyimiz", "kesildi", "sorry", "i don't",
    "i cannot", "as an ai", "i'm sorry", "i am unable"
]
 
# Çok kısa veya kapsam dışı cevaplarda kullanılan fallback
FALLBACK_CEVAP = (
    "Bu konuda yeterince emin değilim, yanlış bilgi vermek istemiyorum. "
    "Diyetisyeninize veya sağlık uzmanına danışmanızı öneririm."
)

BESLENME_KELIMELERI = {
    "kalori", "kilo", "yemek", "yiyecek", "besin", "diyet", "beslenme",
    "protein", "karbonhidrat", "yağ", "vitamin", "mineral", "glisemik",
    "baklava", "kebap", "lahmacun", "pilav", "tarif", "malzeme", "porsiyon",
    "öğün", "kahvaltı", "öğle", "akşam", "ara öğün", "acıktım", "tok",
    "sağlık", "obezite", "zayıflama", "kilo", "bmi", "metabolizma",
    "diyetisyen", "doktor", "hastane", "tahlil", "şeker", "tansiyon",
    "ne yedim", "ne yiyebilir", "kaç kalori", "gramı kaç"
}

TAVSIYE_GEREKTIREN = {
    "diyabet", "tansiyon", "kolesterol", "kalp", "böbrek", "karaciğer",
    "hamile", "hamilelik", "emzirme", "ameliyat", "ilaç", "hastalık",
    "kilo ver", "zayıfla", "obezite", "yeme bozukluğu", "anoreksiya",
    "bulimia", "alerji", "intolerans", "çölyak", "tiroid",
    "ne yapmalıyım", "zararlı mı", "tehlikeli mi", "sağlıklı mı"
}

def _tavsiye_ekle_mi(mesaj):
    mesaj_kucuk = mesaj.lower()
    return any(k in mesaj_kucuk for k in TAVSIYE_GEREKTIREN)

def _beslenme_konusu_mu(mesaj):
    mesaj_kucuk = mesaj.lower()
    return any(k in mesaj_kucuk for k in BESLENME_KELIMELERI)
 
def _qa_yukle():
    # Soru-cevapları oku
    qa_yolu = Path(__file__).parent.parent / "data" / "qa_pairs.json"
    if not qa_yolu.exists():
        return []
    with open(qa_yolu, "r", encoding="utf-8") as f:
        return json.load(f)
 
 
def _few_shot_sec(kullanici_mesaji, qa_pairs, k=2):
    # Kullanıcının mesajıyla en çok kelime ortaklığına sahip k örneği seç
    mesaj_kelimeleri = set(re.sub(r"[^\w\s]", "", kullanici_mesaji.lower()).split())
 
    skorlar = []
    for qa in qa_pairs:
        soru_kelimeleri = set(re.sub(r"[^\w\s]", "", qa["soru"].lower()).split())
        # Kaç kelime ortak
        overlap = len(mesaj_kelimeleri & soru_kelimeleri)
        skorlar.append((overlap, qa))
 
    skorlar.sort(key=lambda x: x[0], reverse=True)
 
    # En az 1 ortak kelimesi olan örnekleri al
    secilen = [qa for (skor, qa) in skorlar[:k] if skor >= 1]
    return secilen
 
 
def _cevap_kaliteli_mi(cevap):
    # Cevap çok kısaysa
    if len(cevap.strip()) < 20:
        return False
 
    # Bilinen saçmalama işaretleri var mı
    cevap_kucuk = cevap.lower()
    if any(isaret in cevap_kucuk for isaret in BOZUK_ISARETLER):
        return False
 
    # Hiçbir harf içermiyorsa
    if not any(c.isalpha() for c in cevap):
        return False
 
    return True
 
 
def sistem_promptu_hazirla(yemek_bilgisi=None, kullanici_profili=None, gunluk_durum=None):
    # system_prompt.txt oku
    prompt_dosyasi = Path(__file__).parent.parent / "data" / "system_prompt.txt"
    with open(prompt_dosyasi, "r", encoding="utf-8") as f:
        sistem_promptu = f.read()
 
    # Kullanıcı profil bilgisi
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
 
    # Bugünün Durumu
    if gunluk_durum:
        toplam_kal = gunluk_durum.get("toplam_kalori", 0)
        hedef = gunluk_durum.get("hedef", 0)
        kalan = max(hedef - toplam_kal, 0) if hedef else 0
        ogunler = gunluk_durum.get("ogunler", [])
 
        sistem_promptu += "\n\nBUGÜNÜN DURUMU:\n"
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
 
    # Az önce analiz edilen yemek
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
 
    # Soru-cevap örneklerini yükle ve mesaja göre en alakalılarını seç
    qa_pairs = _qa_yukle()
    ornekler = _few_shot_sec(kullanici_mesaji, qa_pairs, k=2)
 
    # Seçilen örnekleri sistem promptuna ekle
    if ornekler:
        ornek_blok = "\n\nBENZER SORU-CEVAP ÖRNEKLERİ (bu tarza cevap ver):\n"
        for ornek in ornekler:
            ornek_blok += f"S: {ornek['soru']}\nC: {ornek['cevap']}\n\n"
        sistem_promptu += ornek_blok
 
    # Sohbet geçmişi
    gecmis_metni = ""
    if sohbet_gecmisi:
        for mesaj in sohbet_gecmisi[-6:]:
            if mesaj["rol"] == "kullanici":
                gecmis_metni += f"Kullanıcı: {mesaj['icerik']}\n"
            else:
                gecmis_metni += f"Asistan: {mesaj['icerik']}\n"
 
    tam_prompt = (
        f"{sistem_promptu}\n\n"
        f"ÖNEMLİ: Sadece Türkçe cevap ver!\n\n"
        f"{gecmis_metni}"
        f"Kullanıcı: {kullanici_mesaji}\n"
        f"Asistan (Türkçe):"
    )

    if not _beslenme_konusu_mu(kullanici_mesaji):
        return (
            "Ben sadece beslenme, kalori takibi ve sağlıklı yaşam "
            "konularında yardımcı olabiliyorum. Bu konularda sormak "
            "istediğin bir şey var mı?"
        )
 
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
            cevap = response.json()["response"].strip()
            # Yetersiz Cevaplarda Fallback Döndür
            if not _cevap_kaliteli_mi(cevap):
                return FALLBACK_CEVAP

            if _cevap_kaliteli_mi(cevap) and _tavsiye_ekle_mi(kullanici_mesaji):
                cevap += "\n\n*Kişisel sağlık kararları için diyetisyenine veya doktora danışmanı öneririm.*"
                return cevap

            return cevap
        else:
            return "Bağlantı hatası, tekrar dene."
 
    except requests.exceptions.ConnectionError:
        return "Ollama bağlantısı kurulamadı.
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
    except Exception:
        return False