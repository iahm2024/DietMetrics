import json
import tempfile
import os
from pathlib import Path
from PIL import Image

try:
    from ultralytics import YOLO
    YOLO_HAZIR = True
except ImportError:
    YOLO_HAZIR = False

# COCO'da yemek benzeri sınıflar ve food_db karşılıkları
COCO_TÜRK_ESLESTIRME = {
    "cake": "baklava",
    "donut": "baklava",
    "sandwich": "kebap",
    "pizza": "lahmacun",
    "hot dog": "kebap",
    "bowl": "pirinc_pilavi",
    "rice": "pirinc_pilavi",
}

COCO_REFERANS = ["fork", "spoon", "knife", "bowl", "cup", "dining table"]

COCO_YEMEK = [
    "banana", "apple", "sandwich", "orange", "broccoli",
    "carrot", "hot dog", "pizza", "donut", "cake", "bowl"
]

_model = None

def model_yukle():
    global _model
    if _model is None and YOLO_HAZIR:
        _model = YOLO("yolov8n.pt")
    return _model

def goruntu_analiz_et(fotograf_verisi):
    model = model_yukle()

    if model is None:
        return {
            "basarili": False,
            "hata": "Model yüklenemedi",
            "otomatik_tespit": None,
            "tespitler": [],
            "referans": None,
        }

    try:
        img = Image.open(fotograf_verisi).convert("RGB")
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(tmp.name)
        tmp.close()

        sonuclar = model(tmp.name, verbose=False, conf=0.35)
        os.unlink(tmp.name)

        tespitler = []
        for s in sonuclar:
            for kutu in s.boxes:
                sinif_adi = s.names[int(kutu.cls[0])]
                confidence = float(kutu.conf[0])
                tespitler.append({
                    "sinif": sinif_adi,
                    "confidence": confidence,
                    "bbox": kutu.xyxy[0].tolist(),
                })

        tespitler.sort(key=lambda x: x["confidence"], reverse=True)

        # referans nesne bul
        referans = None
        for t in tespitler:
            if t["sinif"] in COCO_REFERANS:
                referans = t
                break

        # otomatik yemek tespiti
        otomatik_tespit = None
        otomatik_confidence = 0

        for t in tespitler:
            if t["sinif"] in COCO_TÜRK_ESLESTIRME:
                turkish_karsilik = COCO_TÜRK_ESLESTIRME[t["sinif"]]
                if t["confidence"] > otomatik_confidence:
                    otomatik_tespit = turkish_karsilik
                    otomatik_confidence = t["confidence"]

        return {
            "basarili": True,
            "tespitler": tespitler,
            "referans": referans,
            "otomatik_tespit": otomatik_tespit,
            "otomatik_confidence": otomatik_confidence,
        }

    except Exception as e:
        return {
            "basarili": False,
            "hata": str(e),
            "otomatik_tespit": None,
            "tespitler": [],
            "referans": None,
        }

def veritabani_yukle():
    db_yolu = Path(__file__).parent.parent / "data" / "food_db.json"
    with open(db_yolu, "r", encoding="utf-8") as f:
        return json.load(f)

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
    return None