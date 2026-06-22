import os
import shutil
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from ultralytics import FastSAM
from tqdm import tqdm
 
RAW_KLASOR = Path("data/raw_images")
CIKTI_IMG = Path("data/yolo_dataset/images")
CIKTI_LBL = Path("data/yolo_dataset/labels")
PREVIEW = Path("data/preview")
 
# Sinif isimlerini ve YOLO icin numara verecegiz
SINIFLAR = {
    "baklava": 0,
    "kebap": 1,
    "lahmacun": 2,
    "pirinc_pilavi": 3
}
 
# Renkler (preview icin) - BGR formatinda
RENKLER = {
    "baklava":       (10, 112, 212),    # turuncu
    "kebap":         (60, 90, 200),     # kirmizimsi
    "lahmacun":      (50, 170, 240),    # sari
    "pirinc_pilavi": (180, 180, 180)    # gri-beyaz
}
 
def merkez_yemek_maskesi_sec(maskeler, fotoh, fotow):
    # FastSAM birden cok maske doner, biz merkezdeki en buyuk olani isteriz
    # (yemek genelde fotograf merkezinde)
    
    if maskeler is None or len(maskeler) == 0:
        return None
    
    foto_merkezi = np.array([fotow / 2, fotoh / 2])
    foto_alani = fotoh * fotow
    
    en_iyi_skor = -1
    en_iyi_maske = None
    
    for mask in maskeler:
        # Mask numpy array, True/False
        if mask.sum() == 0:
            continue
        
        # Maske alani
        mask_alani = mask.sum()
        alan_orani = mask_alani / foto_alani
        
        # Cok kucuk (gurultu) veya cok buyuk (tum foto) maskeleri at
        if alan_orani < 0.05 or alan_orani > 0.85:
            continue
        
        # Maskenin merkez koordinati
        ys, xs = np.where(mask)
        mask_merkezi = np.array([xs.mean(), ys.mean()])
        
        # Foto merkezine uzaklik (normalize)
        uzaklik = np.linalg.norm(mask_merkezi - foto_merkezi)
        uzaklik_norm = uzaklik / np.linalg.norm([fotow, fotoh])
        
        # Skor: buyuk + merkeze yakin olsun
        # alan_orani 0.05-0.85 arasi normalize edelim
        alan_skor = min(alan_orani / 0.4, 1.0)  # 0.4'e kadar lineer artar, sonra doyar
        merkez_skor = 1.0 - uzaklik_norm
        
        skor = alan_skor * 0.6 + merkez_skor * 0.4
        
        if skor > en_iyi_skor:
            en_iyi_skor = skor
            en_iyi_maske = mask
    
    return en_iyi_maske
 
def maske_to_polygon(mask):
    # Boolean mask'i normalize edilmis polygon koordinatlarina cevirir
    # YOLO segmentation formati: class x1 y1 x2 y2 x3 y3 ...
    
    mask_uint8 = (mask.astype(np.uint8) * 255)
    h, w = mask_uint8.shape
    
    # Konturlari bul
    konturlar, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not konturlar:
        return None
    
    # En buyuk konturu al
    kontur = max(konturlar, key=cv2.contourArea)
    
    # Cok az nokta kalmissa atla (gecersiz polygon)
    if len(kontur) < 3:
        return None
    
    # Polygonu basitlestir (cok fazla nokta YOLO icin gereksiz)
    epsilon = 0.002 * cv2.arcLength(kontur, True)
    kontur_basit = cv2.approxPolyDP(kontur, epsilon, True)
    
    # Yine en az 3 noktasi olmali
    if len(kontur_basit) < 3:
        kontur_basit = kontur
    
    # Normalize et (0-1 araligi)
    points = kontur_basit.reshape(-1, 2).astype(np.float32)
    points[:, 0] /= w
    points[:, 1] /= h
    
    return points.flatten()
 
def preview_olustur(foto_path, mask, sinif, cikti_path):
    # Foto uzerine maskeli yarı saydam katman koyar
    img = cv2.imread(str(foto_path))
    if img is None:
        return
    
    h, w = img.shape[:2]
    mask_resized = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)
    
    # Renkli overlay
    overlay = img.copy()
    renk = RENKLER[sinif]
    overlay[mask_resized > 0] = renk
    
    # Yari saydam birlestir
    sonuc = cv2.addWeighted(img, 0.6, overlay, 0.4, 0)
    
    # Sinif yazisi
    cv2.putText(sonuc, sinif, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    cv2.imwrite(str(cikti_path), sonuc)
 
def main():
    print("=" * 60)
    print("FastSAM Auto-Labeling Basliyor")
    print("=" * 60)
    
    # Cikti klasorlerini hazirla
    CIKTI_IMG.mkdir(parents=True, exist_ok=True)
    CIKTI_LBL.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    for sinif in SINIFLAR:
        (PREVIEW / sinif).mkdir(exist_ok=True)
    
    # FastSAM modelini yukle (ilk seferde indirir, ~23 MB)
    print("\nFastSAM modeli yukleniyor...")
    model = FastSAM("FastSAM-s.pt")
    print("Model hazir\n")
    
    # Istatistik
    basarili = 0
    basarisiz = 0
    sinif_sayim = {s: 0 for s in SINIFLAR}
    
    for sinif, sinif_id in SINIFLAR.items():
        klasor = RAW_KLASOR / sinif
        fotolar = sorted(klasor.glob("*.jpg"))
        
        print(f"\n{sinif} ({len(fotolar)} foto)...")
        
        for foto_path in tqdm(fotolar, desc=sinif):
            try:
                # FastSAM ile segmentle (her seyi)
                results = model(str(foto_path), device="cuda", verbose=False,
                               retina_masks=True, imgsz=640, conf=0.4, iou=0.7)
                
                if not results or results[0].masks is None:
                    basarisiz += 1
                    continue
                
                # Maskeleri numpy array olarak al
                maskeler = results[0].masks.data.cpu().numpy().astype(bool)
                
                # Orijinal foto boyutu
                img = cv2.imread(str(foto_path))
                if img is None:
                    basarisiz += 1
                    continue
                h, w = img.shape[:2]
                
                # Maskeleri orijinal boyuta resize et
                maskeler_resized = []
                for m in maskeler:
                    m_resized = cv2.resize(m.astype(np.uint8), (w, h), 
                                          interpolation=cv2.INTER_NEAREST).astype(bool)
                    maskeler_resized.append(m_resized)
                
                # Yemek maskesini sec
                yemek_maskesi = merkez_yemek_maskesi_sec(maskeler_resized, h, w)
                
                if yemek_maskesi is None:
                    basarisiz += 1
                    continue
                
                # Polygona cevir
                polygon = maske_to_polygon(yemek_maskesi)
                if polygon is None:
                    basarisiz += 1
                    continue
                
                # YOLO formatinda etiket yaz
                # Format: class_id x1 y1 x2 y2 x3 y3 ...
                label_str = f"{sinif_id} " + " ".join(f"{c:.6f}" for c in polygon)
                
                # Dosya isimleri
                base_name = foto_path.stem
                
                # Fotograf kopyala
                shutil.copy(foto_path, CIKTI_IMG / f"{base_name}.jpg")
                
                # Label yaz
                with open(CIKTI_LBL / f"{base_name}.txt", "w") as f:
                    f.write(label_str + "\n")
                
                # Preview
                preview_olustur(foto_path, yemek_maskesi, sinif,
                               PREVIEW / sinif / f"{base_name}.jpg")
                
                basarili += 1
                sinif_sayim[sinif] += 1
                
            except Exception as e:
                print(f"\nHata ({foto_path.name}): {e}")
                basarisiz += 1
    
    print("\n" + "=" * 60)
    print("AUTO-LABELING TAMAMLANDI")
    print("=" * 60)
    print(f"Basarili: {basarili}")
    print(f"Basarisiz: {basarisiz}")
    print(f"\nSinif dagilimi:")
    for sinif, sayi in sinif_sayim.items():
        print(f"  {sinif:20s}: {sayi} etiketli")
    
    print(f"\nCiktilar:")
    print(f"  Etiketli fotolar: {CIKTI_IMG.absolute()}")
    print(f"  YOLO labels:      {CIKTI_LBL.absolute()}")
    print(f"  Onizlemeler:      {PREVIEW.absolute()}")
 
if __name__ == "__main__":
    main()