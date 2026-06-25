import tempfile
import os
import numpy as np
from pathlib import Path
from PIL import Image
 
try:
    from ultralytics import YOLO
    YOLO_HAZIR = True
except ImportError:
    YOLO_HAZIR = False
 
# Custom modelin tanidigi 4 sinif
CUSTOM_SINIFLAR = ["baklava", "kebap", "lahmacun", "pirinc_pilavi"]
 
COCO_REFERANS = ["fork", "spoon", "knife", "bowl", "cup"]
 
# Confidence esik degerleri
CUSTOM_CONF_ESIK = 0.40
COCO_CONF_ESIK = 0.35
 
# Model singleton'lari
_custom_model = None
_coco_model = None
 
def custom_model_yukle():
    global _custom_model
    if _custom_model is None and YOLO_HAZIR:
        model_yolu = Path(__file__).parent.parent / "models" / "yolo11m_food.pt"
        if model_yolu.exists():
            _custom_model = YOLO(str(model_yolu))
        else:
            print(f"UYARI: Custom model bulunamadi: {model_yolu}")
    return _custom_model
 
def coco_model_yukle():
    global _coco_model
    if _coco_model is None and YOLO_HAZIR:
        _coco_model = YOLO("yolov8n.pt")
    return _coco_model
 
def goruntu_analiz_et(fotograf_verisi):
    custom = custom_model_yukle()
    coco = coco_model_yukle()
    
    if custom is None and coco is None:
        return {
            "basarili": False,
            "hata": "Hicbir model yuklenemedi",
            "otomatik_tespit": None,
            "tespitler": [],
            "referans": None,
            "kullanilan_model": None,
            "maskeler": None,
        }
    
    try:
        # Fotoyu hazirla
        img = Image.open(fotograf_verisi).convert("RGB")
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(tmp.name)
        tmp.close()
        
        sonuc = {
            "basarili": True,
            "tespitler": [],
            "referans": None,
            "otomatik_tespit": None,
            "otomatik_confidence": 0,
            "kullanilan_model": None,
            "maskeler": None,
            "ham_genislik": img.width,
            "ham_yukseklik": img.height,
        }
        
        # 1) Custom model - yemek tespiti icin
        if custom is not None:
            sonuclar = custom(tmp.name, verbose=False, conf=CUSTOM_CONF_ESIK, iou=0.5)
            
            custom_tespitler = []
            maskeler = []
            
            for s in sonuclar:
                if s.boxes is None:
                    continue
                for i, kutu in enumerate(s.boxes):
                    sinif_id = int(kutu.cls[0])
                    sinif_adi = CUSTOM_SINIFLAR[sinif_id] if sinif_id < len(CUSTOM_SINIFLAR) else s.names[sinif_id]
                    confidence = float(kutu.conf[0])
                    
                    tespit = {
                        "sinif": sinif_adi,
                        "confidence": confidence,
                        "bbox": kutu.xyxy[0].tolist(),
                        "kaynak": "custom",
                    }
                    custom_tespitler.append(tespit)
                
                # Segmentation maskeleri varsa al
                if s.masks is not None:
                    maskeler = s.masks.data.cpu().numpy() if hasattr(s.masks.data, 'cpu') else s.masks.data
            
            custom_tespitler.sort(key=lambda x: x["confidence"], reverse=True)
            
            # En yuksek conf'lu tespiti otomatik tespit yap
            if custom_tespitler:
                en_iyi = custom_tespitler[0]
                sonuc["otomatik_tespit"] = en_iyi["sinif"]
                sonuc["otomatik_confidence"] = en_iyi["confidence"]
                sonuc["kullanilan_model"] = "custom"
                sonuc["tespitler"] = custom_tespitler
                if len(maskeler) > 0:
                    sonuc["maskeler"] = maskeler
        
        # 2) COCO modeli - hem referans nesne hem fallback yemek tespiti
        if coco is not None:
            coco_sonuc = coco(tmp.name, verbose=False, conf=COCO_CONF_ESIK)
            
            coco_tespitler = []
            for s in coco_sonuc:
                if s.boxes is None:
                    continue
                for kutu in s.boxes:
                    sinif_adi = s.names[int(kutu.cls[0])]
                    confidence = float(kutu.conf[0])
                    coco_tespitler.append({
                        "sinif": sinif_adi,
                        "confidence": confidence,
                        "bbox": kutu.xyxy[0].tolist(),
                        "kaynak": "coco",
                    })
            
            coco_tespitler.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Referans nesne (catal, kasik, tabak) hep COCO'dan gelir
            for t in coco_tespitler:
                if t["sinif"] in COCO_REFERANS:
                    sonuc["referans"] = t
                    break
            
        
        os.unlink(tmp.name)
        return sonuc
    
    except Exception as e:
        return {
            "basarili": False,
            "hata": str(e),
            "otomatik_tespit": None,
            "tespitler": [],
            "referans": None,
            "kullanilan_model": None,
            "maskeler": None,
        }