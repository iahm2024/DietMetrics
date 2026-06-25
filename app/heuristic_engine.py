# Referans nesnelerin gerçek dünyadaki ortalama boyutları (cm)
# Kaynak: standart sofra takımı ölçüleri
REFERANS_BOYUTLAR = {
    "fork": 20.0,
    "spoon": 17.0,
    "knife": 22.0,
    "bowl": 15.0,
    "cup": 8.0,
}
 
# Referans nesnenin fotoğraftaki beklenen oranı
BEKLENEN_PIKSEL_ORANI = {
    "fork": 0.20,
    "spoon": 0.18,
    "knife": 0.22,
    "bowl": 0.30,
    "cup": 0.15,
}
 
# Çarpan sınırları - aşırı sapma olmaması için clamp aralığı
MIN_CARPAN = 0.85
MAX_CARPAN = 1.15
 
def referans_carpani_hesapla(referans_tespit, goruntu_genisligi):
    # Referans nesnenin piksel boyutuna göre yemek miktarı çarpanı üretir
    # Nesne beklenenden büyükse fotoğraf yakın çekim, fazla yemek var
    # Beklenenden küçükse uzak çekim, az yemek var
    if referans_tespit is None or goruntu_genisligi <= 0:
        return 1.0
 
    sinif = referans_tespit.get("sinif")
    if sinif not in REFERANS_BOYUTLAR or sinif not in BEKLENEN_PIKSEL_ORANI:
        return 1.0
 
    bbox = referans_tespit.get("bbox", [0, 0, 0, 0])
    genislik = bbox[2] - bbox[0]
    yukseklik = bbox[3] - bbox[1]
    piksel_uzunluk = max(genislik, yukseklik)
 
    if piksel_uzunluk <= 0:
        return 1.0
 
    # Bu referans nesnenin fotoğrafta beklenen piksel uzunluğu
    beklenen_piksel = goruntu_genisligi * BEKLENEN_PIKSEL_ORANI[sinif]
 
    # Gerçek piksel / beklenen piksel oranı
    oran = piksel_uzunluk / beklenen_piksel
 
    # 0.7-1.3 aralığına clamp et, aşırı değerleri kırp
    if oran < MIN_CARPAN:
        return MIN_CARPAN
    if oran > MAX_CARPAN:
        return MAX_CARPAN
    return oran
 
 
def gramaj_hesapla(yemek_adi, porsiyon_carpani, referans_tespit, goruntu_genisligi, db):
    # Ortalama porsiyon ağırlığını al
    if yemek_adi in db["turkish_classes"]:
        ort_gram = db["turkish_classes"][yemek_adi]["avg_portion_g"]
    else:
        ort_gram = 150
 
    # Referans nesneden gelen ölçek çarpanı
    ref_carpan = referans_carpani_hesapla(referans_tespit, goruntu_genisligi)
 
    # Hem porsiyon çarpanı hem referans çarpanı uygulanır
    return ort_gram * porsiyon_carpani * ref_carpan
 
 
def glisemik_yuk_hesapla(gi, karb_gram):
    # WHO/FAO standardı: GL = (GI x karb) / 100
    if gi == 0 or karb_gram == 0:
        return 0.0
    return (gi * karb_gram) / 100
 
 
def glisemik_yuk_siniflandir(gl):
    # WHO sınıflandırması
    # GL <= 10  : düşük
    # GL 11-19  : orta
    # GL >= 20  : yüksek
    if gl == 0:
        return {
            "etiket": "Yok",
            "renk": "#888888",
            "aciklama": "Bu yemekte kayda değer karbonhidrat yok"
        }
    elif gl <= 10:
        return {
            "etiket": "Düşük",
            "renk": "#4ade80",
            "aciklama": "Kan şekerini yavaş yükseltir"
        }
    elif gl <= 19:
        return {
            "etiket": "Orta",
            "renk": "#D4700A",
            "aciklama": "Dengeli, ölçülü tüket"
        }
    else:
        return {
            "etiket": "Yüksek",
            "renk": "#ef4444",
            "aciklama": "Kan şekerini hızlı yükseltir, yürüyüş öneririm"
        }
 
