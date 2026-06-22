import cv2
import numpy as np
from pathlib import Path

# referans nesnelerin gerçek boyutları (cm)
REFERANS_BOYUTLAR = {
    "fork": 20.0,
    "spoon": 17.0,
    "knife": 22.0,
}

TABAK_CAPI_CM = 26.0

def piksel_basina_cm(referans_tespit, goruntu_genisligi):
    if referans_tespit is None:
        # referans yoksa tabak şablonuna göre tahmin
        return TABAK_CAPI_CM / goruntu_genisligi

    sinif = referans_tespit["sinif_adi"]
    bbox = referans_tespit["bbox"]

    # bbox uzunluğu (en uzun kenar)
    genislik = bbox[2] - bbox[0]
    yukseklik = bbox[3] - bbox[1]
    piksel_uzunluk = max(genislik, yukseklik)

    if sinif in REFERANS_BOYUTLAR and piksel_uzunluk > 0:
        gercek_uzunluk = REFERANS_BOYUTLAR[sinif]
        return gercek_uzunluk / piksel_uzunluk

    return TABAK_CAPI_CM / goruntu_genisligi

def gramaj_hesapla(yemek_adi, porsiyon_carpani, referans_tespit,
                   goruntu_genisligi, db):
    # ortalama porsiyon ağırlığını al
    if yemek_adi in db["turkish_classes"]:
        ort_gram = db["turkish_classes"][yemek_adi]["avg_portion_g"]
    elif yemek_adi in db["coco_fallback_classes"]:
        ort_gram = db["coco_fallback_classes"][yemek_adi]["avg_portion_g"]
    else:
        ort_gram = 150

    # porsiyon çarpanını uygula
    return ort_gram * porsiyon_carpani

def glisemik_yuk_hesapla(gi, karb_gram):
    # WHO/FAO standardı: GL = (GI x karb) / 100
    # GI 0 ise (et, balik vs) GL de 0
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