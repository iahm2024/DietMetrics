import json
from pathlib import Path

# ultralytics kurulumu bitince bu import aktif olacak
try:
    from ultralytics import YOLO
    YOLO_HAZIR = True
except ImportError:
    YOLO_HAZIR = False

# food_db yükle
def veritabani_yukle():
    db_yolu = Path(__file__).parent.parent / "data" / "food_db.json"
    with open(db_yolu, "r", encoding="utf-8") as f:
        return json.load(f)

# COCO sınıf isimleri (bize lazım olanlar)
COCO_REFERANS = {
    42: "fork",
    44: "spoon",
    45: "bowl",
    47: "cup",
}

COCO_YEMEK = {
    46: "banana",
    47: "apple",
    49: "orange",
    51: "carrot",
    52: "hot dog",
    53: "pizza",
    54: "donut",
    55: "cake",
    56: "sandwich",
}

def coco_modeli_yukle():
    if not YOLO_HAZIR:
        return None
    try:
        # YOLOv8n en küçük model, hızlı çalışır
        model = YOLO("yolov8n.pt")
        return model
    except Exception as e:
        print(f"Model yüklenemedi: {e}")
        return None

def fotografi_analiz_et(fotograf_yolu, model):
    if model is None or not YOLO_HAZIR:
        # model hazır değil, mock sonuç döndür
        return {
            "basarili": False,
            "hata": "Model henüz yüklenmedi",
            "referans": None,
            "coco_tespit": None,
        }

    try:
        sonuclar = model(fotograf_yolu, verbose=False)
        tespit_listesi = []

        for sonuc in sonuclar:
            for kutu in sonuc.boxes:
                sinif_id = int(kutu.cls[0])
                confidence = float(kutu.conf[0])
                sinif_adi = sonuc.names[sinif_id]

                tespit_listesi.append({
                    "sinif_id": sinif_id,
                    "sinif_adi": sinif_adi,
                    "confidence": confidence,
                    "bbox": kutu.xyxy[0].tolist(),
                })

        # referans nesne bul (çatal > kaşık > kase)
        referans = None
        for tespit in sorted(tespit_listesi,
                             key=lambda x: x["confidence"],
                             reverse=True):
            if tespit["sinif_id"] in COCO_REFERANS:
                referans = tespit
                break

        # yemek benzeri nesne bul
        coco_yemek = None
        for tespit in sorted(tespit_listesi,
                             key=lambda x: x["confidence"],
                             reverse=True):
            if tespit["sinif_id"] in COCO_YEMEK:
                coco_yemek = tespit
                break

        return {
            "basarili": True,
            "tum_tespitler": tespit_listesi,
            "referans": referans,
            "coco_tespit": coco_yemek,
        }

    except Exception as e:
        return {
            "basarili": False,
            "hata": str(e),
            "referans": None,
            "coco_tespit": None,
        }

def kalori_hesapla(yemek_adi, gram, db):
    if yemek_adi in db["turkish_classes"]:
        y = db["turkish_classes"][yemek_adi]
        return {
            "kalori": (y["calories_per_100g"] * gram) / 100,
            "protein": (y["protein_per_100g"] * gram) / 100,
            "yag": (y["fat_per_100g"] * gram) / 100,
            "karb": (y["carbs_per_100g"] * gram) / 100,
            "bilgi": y,
        }
    elif yemek_adi in db["coco_fallback_classes"]:
        y = db["coco_fallback_classes"][yemek_adi]
        kalori = (y["calories_per_100g"] * gram) / 100
        return {
            "kalori": kalori,
            "protein": 0,
            "yag": 0,
            "karb": 0,
            "bilgi": y,
        }
    return None