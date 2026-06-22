import re
from pathlib import Path
import numpy as np


# Modeller singleton olarak cachelenir
_embedder = None
_index = None
_tarifler = None
_tarif_malzemeleri = None


# Kullanicinin "yok / olmadan / yerine" gibi kisit ifadeleri
KISIT_KEYWORDS = [
    "yok", "olmadan", "olmasın", "haricinde", "hariç", "değiştir",
    "yerine", "vegan", "vejetaryen", "glütensiz", "şekersiz", "tuzsuz",
    "alerjim", "alerjisi", "sevmem", "sevmiyorum", "yiyemem", "kullanmıyorum"
]


def kisit_var_mi(metin):
    metin_kucuk = metin.lower()
    return any(kw in metin_kucuk for kw in KISIT_KEYWORDS)


def tarif_parse(tarif_metni):
    # Tek bir tarif blogunu yapilandirilmis sozluge donustur
    try:
        # Yemek adi
        ad_match = re.search(r"Yemek Adı:\s*(.+?)(?:\n|$)", tarif_metni)
        ad = ad_match.group(1).strip() if ad_match else "İsimsiz Tarif"

        # Malzemeler
        malz_kismi = tarif_metni.split("Malzemeler:")[1].split("Yapılış:")[0].strip()

        # Yapilis
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


def sistem_hazirla():
    # Tum modelleri ve indeksi bir kere yukle, sonra cacheden don
    global _embedder, _index, _tarifler, _tarif_malzemeleri

    if _embedder is not None and _index is not None:
        return _embedder, _index, _tarifler, _tarif_malzemeleri

    from sentence_transformers import SentenceTransformer
    import faiss

    # Lokal embedder modelini yukle (internetsiz)
    model_yolu = Path(__file__).parent.parent / "models" / "sentence_embedder"
    if not model_yolu.exists():
        raise FileNotFoundError(
            f"Sentence embedder modeli bulunamadi: {model_yolu}\n"
            "Once kurulum komutunu calistir."
        )
    _embedder = SentenceTransformer(str(model_yolu))

    # Tarif dosyasini oku ve parse et
    tarif_yolu = Path(__file__).parent.parent / "data" / "tarifler.txt"
    if not tarif_yolu.exists():
        raise FileNotFoundError(f"Tarif dosyasi bulunamadi: {tarif_yolu}")

    with open(tarif_yolu, "r", encoding="utf-8") as f:
        icerik = f.read()

    # --- ile ayir, ilk fihrist kismini at (eger varsa)
    parcalar = [t.strip() for t in icerik.split("---") if t.strip()]

    # Sadece "Yemek Adı:" iceren bloklari al (fihrist parcasini ele)
    _tarifler = []
    _tarif_malzemeleri = []

    for parca in parcalar:
        if "Yemek Adı:" not in parca or "Malzemeler:" not in parca:
            continue
        parsed = tarif_parse(parca)
        if parsed is None:
            continue
        _tarifler.append(parsed)
        _tarif_malzemeleri.append(parsed["malzemeler_metin"])

    if not _tarifler:
        raise ValueError("Hicbir tarif parse edilemedi, TXT formatini kontrol et.")

    # Sadece malzemeleri vektorize et (FAISS index)
    print(f"FAISS index olusturuluyor ({len(_tarifler)} tarif)...")
    embeddings = _embedder.encode(_tarif_malzemeleri, show_progress_bar=False)
    embeddings = embeddings.astype("float32")

    _index = faiss.IndexFlatL2(embeddings.shape[1])
    _index.add(embeddings)

    return _embedder, _index, _tarifler, _tarif_malzemeleri


def _malzeme_kelimelerini_cikar(metin):
    # Metinden anlamlı malzeme kelimelerini cikar
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

    # Stopword'leri at, 2 harften kisalari at
    sonuc = [k for k in kelimeler if k not in stopwords and len(k) > 2]
    return sonuc


def _keyword_skoru(istenen_kelimeler, olmayan_kelimeler, tarif_malzemeleri):
    # Tarifin malzeme metnine bakip skor hesapla
    # +1 her istenen kelime icin (tarifte varsa)
    # -2 her olmayan kelime icin (tarifte varsa) - ceza

    malzeme_kucuk = tarif_malzemeleri.lower()
    skor = 0

    for k in istenen_kelimeler:
        if k in malzeme_kucuk:
            skor += 1

    for k in olmayan_kelimeler:
        if k in malzeme_kucuk:
            skor -= 2  # Olmamasi gerekene ceza

    return skor


def tarif_bul(kullanici_metni, kalori_limiti, top_k=20, olmayanlar=None):
    # HYBRID SEARCH: semantic + keyword
    embedder, index, tarifler, tarif_malzemeleri = sistem_hazirla()

    if olmayanlar is None:
        olmayanlar = []

    # 1) Semantic search - FAISS ile en yakin top_k tarifi al
    sorgu_vec = embedder.encode([kullanici_metni]).astype("float32")
    mesafeler, indeksler = index.search(sorgu_vec, min(top_k * 2, len(tarifler)))

    # 2) Istenen ve olmayan kelimeleri ayikla
    istenen_kelimeler = _malzeme_kelimelerini_cikar(kullanici_metni)
    # Olmayanlari istenenlerden cikar
    olmayanlar_set = set(o.lower() for o in olmayanlar)
    istenen_kelimeler = [k for k in istenen_kelimeler if k not in olmayanlar_set]

    # 3) Her aday icin hybrid skor hesapla
    adaylar_skorlu = []
    for idx in indeksler[0]:
        tarif = tarifler[idx]
        semantic_skor = 1.0 / (1.0 + float(mesafeler[0][list(indeksler[0]).index(idx)]))
        keyword_skor = _keyword_skoru(istenen_kelimeler, list(olmayanlar_set), tarif_malzemeleri[idx])

        # Normalize: keyword skoru ham, semantik 0-1 arasi
        # Hybrid: semantic %30, keyword %70 (keyword daha gercek bir esleştirme)
        hybrid_skor = (semantic_skor * 0.3) + (keyword_skor * 0.7)

        adaylar_skorlu.append({
            "tarif": tarif,
            "semantic_skor": semantic_skor,
            "keyword_skor": keyword_skor,
            "hybrid_skor": hybrid_skor,
        })

    # Hybrid skora gore sirala
    adaylar_skorlu.sort(key=lambda x: x["hybrid_skor"], reverse=True)

    # Kalori filtresi
    kalori_esnek_limit = kalori_limiti * 1.1
    aday_listesi = [a["tarif"] for a in adaylar_skorlu]

    secilen = None
    for a in adaylar_skorlu:
        if a["tarif"]["kalori"] <= kalori_esnek_limit:
            # Ayrica keyword skoru pozitif olmali (en az 1 istenen malzeme eslesmeli)
            if a["keyword_skor"] >= 1:
                secilen = a["tarif"]
                break

    # Hicbiri uymadiysa, kaloriye uyan ilk tarifi al
    if secilen is None:
        for a in adaylar_skorlu:
            if a["tarif"]["kalori"] <= kalori_esnek_limit:
                secilen = a["tarif"]
                break

    # Yine yoksa en yuksek skorlu tarifi al
    if secilen is None and aday_listesi:
        secilen = aday_listesi[0]

    return secilen, aday_listesi


def tarif_sun_template(tarif):
    # LLM olmadan sik bir sekilde tarif sun
    if tarif is None:
        return None
    return {
        "ad": tarif["ad"],
        "malzemeler_metin": tarif["malzemeler_metin"],
        "yapilis_metin": tarif["yapilis_metin"],
        "kalori": tarif["kalori"],
        "yontem": "template",
    }

def kisitlari_ayikla(metin):
    # Kullanicinin metninden "olmayan/istenmeyenleri" cikar
    # Basit kural tabanli: "X yok", "X olmadan", "X sevmem" gibi yapilari yakala

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

    # Tekrarsiz ve bos olmayan
    olmayanlar = list(set([o.strip() for o in olmayanlar if o.strip() and len(o) > 2]))

    return olmayanlar


def malzemeleri_ayikla(metin):
    # Kullanicinin yazdigi malzemeleri al ama kisit kelimelerini cikar
    # Cunku FAISS sorgusuna kisit kelimeleri girmemeli

    olmayanlar = kisitlari_ayikla(metin)
    metin_temiz = metin.lower()

    # Kisit ifadelerini metinden cikar (basit yaklasim)
    for kelime in KISIT_KEYWORDS:
        metin_temiz = re.sub(rf"\b\w*\s*{kelime}\b", "", metin_temiz)

    # Olmayan malzeme isimlerini de cikar
    for olmayan in olmayanlar:
        metin_temiz = re.sub(rf"\b{olmayan}\b", "", metin_temiz)

    return metin_temiz.strip(), olmayanlar