import re
from pathlib import Path
import numpy as np
import streamlit as st
import faiss
from sentence_transformers import SentenceTransformer

# kullanıcının "yok / olmadan / yerine" gibi kısıt ifadeleri
KISIT_KEYWORDS = [
    "yok", "olmadan", "olmasın", "haricinde", "hariç", "değiştir",
    "yerine", "vegan", "vejetaryen", "glütensiz", "şekersiz", "tuzsuz",
    "alerjim", "alerjisi", "sevmem", "sevmiyorum", "yiyemem", "kullanmıyorum"
]


def kisit_var_mi(metin):
    metin_kucuk = metin.lower()
    return any(kw in metin_kucuk for kw in KISIT_KEYWORDS)


def tarif_parse(tarif_metni):
    # Tek bir tarif bloğunu yapılandırılmış sözlüğe dönüştür
    try:
        # Yemek adı
        ad_match = re.search(r"Yemek Adı:\s*(.+?)(?:\n|$)", tarif_metni)
        ad = ad_match.group(1).strip() if ad_match else "İsimsiz Tarif"

        # Malzemeler
        malz_kismi = tarif_metni.split("Malzemeler:")[1].split("Yapılış:")[0].strip()

        # Yapılış
        yapi_kismi = tarif_metni.split("Yapılış:")[1].split("Kalori:")[0].strip()

        # Kalori
        kal_match = re.search(r"Kalori:\s*([\d.]+)", tarif_metni)
        kalori = float(kal_match.group(1)) if kal_match else 0

        return {
            "ad": ad,
            "malzemeler_metin": malz_kismi,
            "yapilis_metin": yapi_kismi,
            "kalori": kalori,
            "ham": tarif_metni,
        }
    except (IndexError, AttributeError, ValueError):
        return None


# Modellerin Streamlit tarafından cachelenmesi
@st.cache_resource(show_spinner="Tarif motoru ve AI modelleri yükleniyor...")
def sistem_hazirla():
    # Lokal embedder modelini yükle
    model_yolu = Path(__file__).parent.parent / "models" / "sentence_embedder"
    if not model_yolu.exists():
        raise FileNotFoundError(
            f"Sentence embedder modeli bulunamadı: {model_yolu}\n"
            "Önce kurulum komutunu çalıştır."
        )
    
    embedder = SentenceTransformer(str(model_yolu))

    # Tarif dosyasını oku ve parse et
    tarif_yolu = Path(__file__).parent.parent / "data" / "tarifler.txt"
    if not tarif_yolu.exists():
        raise FileNotFoundError(f"Tarif dosyası bulunamadı: {tarif_yolu}")

    with open(tarif_yolu, "r", encoding="utf-8") as f:
        icerik = f.read()

    parcalar = [t.strip() for t in icerik.split("---") if t.strip()]

    tarifler = []
    tarif_malzemeleri = []

    for parca in parcalar:
        if "Yemek Adı:" not in parca or "Malzemeler:" not in parca:
            continue
        parsed = tarif_parse(parca)
        if parsed is None:
            continue
        tarifler.append(parsed)
        tarif_malzemeleri.append(parsed["malzemeler_metin"])

    if not tarifler:
        raise ValueError("Hiçbir tarif parse edilemedi, TXT formatını kontrol et.")

    # Sadece malzemeleri vektörize et (FAISS index)
    embeddings = embedder.encode(tarif_malzemeleri, show_progress_bar=False)
    embeddings = embeddings.astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return embedder, index, tarifler, tarif_malzemeleri


def _malzeme_kelimelerini_cikar(metin):
    # Metinden anlamlı malzeme kelimelerini çıkar
    # Stopword (yok, var, de, ve vs) temizle
    stopwords = {
        "ve", "veya", "ile", "de", "da", "ya", "var", "yok", "olmadan",
        "olmasın", "haricinde", "hariç", "yerine", "sevmem", "sevmiyorum",
        "bir", "iki", "üç", "biraz", "az", "çok", "için", "ki", "ile",
        "tane", "adet", "kilo", "gram", "kg", "g", "ml", "litre",
        "bende", "bizde", "benim", "var", "bulunuyor", "lazım",
        "the", "a", "an"
    }

    # Noktalama temizle
    metin_temiz = re.sub(r"[^\w\sçğıöşüÇĞİÖŞÜ]", " ", metin.lower())
    kelimeler = metin_temiz.split()

    # Stopword'leri at, 2 harften kısaları at
    sonuc = [k for k in kelimeler if k not in stopwords and len(k) > 2]
    return sonuc


def _keyword_skoru(istenen_kelimeler, olmayan_kelimeler, tarif_malzemeleri):
    # Tarifin malzeme metnine bakıp skor hesapla
    # +1 her istenen kelime için (tarifte varsa)
    # -2 her olmayan kelime için (tarifte varsa)

    malzeme_kucuk = tarif_malzemeleri.lower()
    skor = 0

    for k in istenen_kelimeler:
        if k in malzeme_kucuk:
            skor += 1

    for k in olmayan_kelimeler:
        if k in malzeme_kucuk:
            skor -= 2

    return skor


def tarif_bul(kullanici_metni, kalori_limiti, top_k=20, olmayanlar=None):
    # HYBRID SEARCH: semantic + keyword
    embedder, index, tarifler, tarif_malzemeleri = sistem_hazirla()

    if olmayanlar is None:
        olmayanlar = []

    # 1) Semantic search - FAISS ile en yakın top_k tarifi al
    sorgu_vec = embedder.encode([kullanici_metni]).astype("float32")
    mesafeler, indeksler = index.search(sorgu_vec, min(top_k * 2, len(tarifler)))

    # 2) İstenen ve olmayan kelimeleri ayıkla
    istenen_kelimeler = _malzeme_kelimelerini_cikar(kullanici_metni)
    # Olmayanları istenenlerden çıkar
    olmayanlar_set = set(o.lower() for o in olmayanlar)
    istenen_kelimeler = [k for k in istenen_kelimeler if k not in olmayanlar_set]

    # 3) Her aday için hybrid skor hesapla
    adaylar_skorlu = []
    for idx in indeksler[0]:
        tarif = tarifler[idx]
        semantic_skor = 1.0 / (1.0 + float(mesafeler[0][list(indeksler[0]).index(idx)]))
        keyword_skor = _keyword_skoru(istenen_kelimeler, list(olmayanlar_set), tarif_malzemeleri[idx])

        # Normalize: keyword skoru ham, semantik 0-1 arasi
        # Hybrid: semantic %30, keyword %70
        hybrid_skor = (semantic_skor * 0.3) + (keyword_skor * 0.7)

        adaylar_skorlu.append({
            "tarif": tarif,
            "semantic_skor": semantic_skor,
            "keyword_skor": keyword_skor,
            "hybrid_skor": hybrid_skor,
        })

    # Hybrid skora göre sırala
    adaylar_skorlu.sort(key=lambda x: x["hybrid_skor"], reverse=True)

    # Kalori filtresi
    kalori_esnek_limit = kalori_limiti * 1.1
    aday_listesi = [a["tarif"] for a in adaylar_skorlu]

    secilen = None
    for a in adaylar_skorlu:
        if a["tarif"]["kalori"] <= kalori_esnek_limit:
            # Ayrıca keyword skoru pozitif olmali (en az 1 istenen malzeme eşleşmeli)
            if a["keyword_skor"] >= 1:
                secilen = a["tarif"]
                break

    # Hiçbiri uymadıysa, kaloriye uyan ilk tarifi al
    if secilen is None:
        for a in adaylar_skorlu:
            if a["tarif"]["kalori"] <= kalori_esnek_limit:
                secilen = a["tarif"]
                break

    # Yine yoksa en yüksek skorlu tarifi al
    if secilen is None and aday_listesi:
        secilen = aday_listesi[0]

    return secilen, aday_listesi

def kisitlari_ayikla(metin):
    # Kullanıcının metninden "olmayan/istenmeyenleri" çıkar
    # "X yok", "X olmadan", "X sevmem" gibi yapıları yakala

    metin_kucuk = metin.lower()
    olmayanlar = []

    # "X yok" / "X'im yok"
    yok_pattern = re.findall(r"(\w+?)(?:'?[ıiuü]?m)?\s+yok", metin_kucuk)
    olmayanlar.extend(yok_pattern)

    # "X olmadan / olmasın"
    olmadan_pattern = re.findall(r"(\w+)\s+olma(?:dan|sın)", metin_kucuk)
    olmayanlar.extend(olmadan_pattern)

    # "X sevmem / sevmiyorum / yiyemem"
    sevmem_pattern = re.findall(r"(\w+)\s+(?:sevmem|sevmiyorum|yiyemem|sevmiyor)", metin_kucuk)
    olmayanlar.extend(sevmem_pattern)

    # "X yerine"
    yerine_pattern = re.findall(r"(\w+)\s+yerine", metin_kucuk)
    olmayanlar.extend(yerine_pattern)

    # Tekrarsız ve boş olmayan
    olmayanlar = list(set([o.strip() for o in olmayanlar if o.strip() and len(o) > 2]))

    return olmayanlar


def malzemeleri_ayikla(metin):
    # Kullanıcının yazdığı malzemeleri al ama kısıt kelimelerini çıkar
    # Çünkü FAISS sorgusuna kısıt kelimeleri girmemeli

    olmayanlar = kisitlari_ayikla(metin)
    metin_temiz = metin.lower()

    # Kısıt ifadelerini metinden çıkar (basit yaklasim)
    for kelime in KISIT_KEYWORDS:
        metin_temiz = re.sub(rf"\b\w*\s*{kelime}\b", "", metin_temiz)

    # Olmayan malzeme isimlerini de çıkar
    for olmayan in olmayanlar:
        metin_temiz = re.sub(rf"\b{olmayan}\b", "", metin_temiz)

    return metin_temiz.strip(), olmayanlar