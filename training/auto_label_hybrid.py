import shutil
from pathlib import Path
import numpy as np
import cv2
from ultralytics import YOLO, SAM
from tqdm import tqdm
 
RAW_KLASOR = Path("data/raw_images")
CIKTI_IMG = Path("data/yolo_dataset/images")
CIKTI_LBL = Path("data/yolo_dataset/labels")
PREVIEW = Path("data/preview")
 
SINIFLAR = {
    "baklava": 0,
    "kebap": 1,
    "lahmacun": 2,
    "pirinc_pilavi": 3
}
 
RENKLER = {
    "baklava":       (10, 112, 212),
    "kebap":         (60, 90, 200),
    "lahmacun":      (50, 170, 240),
    "pirinc_pilavi": (180, 180, 180)
}
 
# COCO food sinif id'leri (her sinif kendi yemegine yakin coco sinifini kullanir)
# bowl (45) cogu zaman tabak gibi davranir, dikkatli kullanilmali
FOOD_COCO_IDS = {
    "baklava":       [55, 56, 49],          # donut, cake, sandwich
    "kebap":         [53, 49, 55],          # hot dog, sandwich, donut
    "lahmacun":      [54, 49, 56],          # pizza, sandwich, cake
    "pirinc_pilavi": [45, 51, 52, 50, 56]   # bowl, broccoli, carrot, orange, cake
}
 
# Genel food id'ler (fallback bbox toplama icin)
TUM_FOOD_IDS = list(range(46, 57)) + [45]  # 45-56 araliginda yemekler + bowl
 
def temizle():
    for k in [CIKTI_IMG, CIKTI_LBL, PREVIEW]:
        if k.exists():
            shutil.rmtree(k)
    CIKTI_IMG.mkdir(parents=True)
    CIKTI_LBL.mkdir(parents=True)
    PREVIEW.mkdir(parents=True)
    for sinif in SINIFLAR:
        (PREVIEW / sinif).mkdir()
 
def renk_varyansi(img, mask):
    if mask.sum() < 100:
        return 0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    pikseller = hsv[mask]
    return pikseller[:, 1].std() + pikseller[:, 2].std()
 
def doku_skoru(img, mask):
    if mask.sum() < 100:
        return 0
    gri = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gri[mask].std()
 
def yolo_food_bbox_bul(yolo_model, img, sinif_adi):
    # YOLO ile food bbox'lari bul
    # Sinifa ozel ve genel food id'leri dene
    
    results = yolo_model(img, verbose=False, conf=0.20, iou=0.5)
    
    if not results or results[0].boxes is None:
        return []
    
    boxes = results[0].boxes
    cls_ids = boxes.cls.cpu().numpy().astype(int)
    xyxys = boxes.xyxy.cpu().numpy()
    confs = boxes.conf.cpu().numpy()
    
    # Sinifimiza ozel food id'lerini onceliklendir
    ozel_ids = set(FOOD_COCO_IDS[sinif_adi])
    
    secilenler = []
    for i, cid in enumerate(cls_ids):
        if cid in ozel_ids:
            secilenler.append({"bbox": xyxys[i], "conf": confs[i], "ozel": True})
    
    # Yeterli ozel yoksa genel food id'lerine bak
    if len(secilenler) < 2:
        for i, cid in enumerate(cls_ids):
            if cid in TUM_FOOD_IDS and cid not in ozel_ids:
                secilenler.append({"bbox": xyxys[i], "conf": confs[i], "ozel": False})
    
    # Confidence sirala
    secilenler.sort(key=lambda x: x["conf"], reverse=True)
    
    # Maksimum 8 bbox
    return [s["bbox"] for s in secilenler[:8]]
 
def sam2_prompt_ile_maskele(sam_model, foto_path, bboxes):
    # SAM2'yi bbox prompt ile cagir
    if not bboxes:
        return None
    
    bbox_list = [b.tolist() for b in bboxes]
    results = sam_model(foto_path, bboxes=bbox_list, verbose=False)
    
    if not results or results[0].masks is None:
        return None
    
    return results[0].masks.data.cpu().numpy().astype(bool)
 
def sam2_auto_fallback(sam_model, foto_path):
    # SAM2 auto-everything modu (fallback)
    results = sam_model(foto_path, verbose=False)
    if not results or results[0].masks is None:
        return None
    return results[0].masks.data.cpu().numpy().astype(bool)
 
def maskeleri_filtrele(img, maskeler, h, w):
    if maskeler is None or len(maskeler) == 0:
        return []
    
    foto_alani = h * w
    foto_merkezi = np.array([w / 2, h / 2])
    foto_diag = np.sqrt(w*w + h*h)
    
    adaylar = []
    for mask in maskeler:
        # Boyut esitleme
        if mask.shape != (h, w):
            mask = cv2.resize(mask.astype(np.uint8), (w, h),
                            interpolation=cv2.INTER_NEAREST).astype(bool)
        
        if mask.sum() == 0:
            continue
        
        alan_orani = mask.sum() / foto_alani
        if alan_orani < 0.025 or alan_orani > 0.75:
            continue
        
        ys, xs = np.where(mask)
        merkez = np.array([xs.mean(), ys.mean()])
        uzaklik = np.linalg.norm(merkez - foto_merkezi) / foto_diag
        if uzaklik > 0.45:
            continue
        
        varyans = renk_varyansi(img, mask)
        if varyans < 22:
            continue
        
        doku = doku_skoru(img, mask)
        if doku < 15:
            continue
        
        adaylar.append({"mask": mask, "alan_orani": alan_orani})
    
    if not adaylar:
        return []
    
    # IoU ayiklama
    secilenler = []
    adaylar.sort(key=lambda a: a["alan_orani"], reverse=True)
    for aday in adaylar:
        cakisma = False
        for s in secilenler:
            kesisim = (aday["mask"] & s["mask"]).sum()
            birlesim = (aday["mask"] | s["mask"]).sum()
            iou = kesisim / max(birlesim, 1)
            if iou > 0.3:
                cakisma = True
                break
        if not cakisma:
            secilenler.append(aday)
    
    return [s["mask"] for s in secilenler[:8]]
 
def maske_to_polygon(mask):
    mask_uint8 = (mask.astype(np.uint8) * 255)
    h, w = mask_uint8.shape
    konturlar, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not konturlar:
        return None
    kontur = max(konturlar, key=cv2.contourArea)
    if len(kontur) < 3:
        return None
    epsilon = 0.002 * cv2.arcLength(kontur, True)
    kontur_basit = cv2.approxPolyDP(kontur, epsilon, True)
    if len(kontur_basit) < 3:
        kontur_basit = kontur
    points = kontur_basit.reshape(-1, 2).astype(np.float32)
    points[:, 0] /= w
    points[:, 1] /= h
    return points.flatten()
 
def preview_olustur(img, maskeler, sinif, modu, cikti_path):
    overlay = img.copy()
    renk = RENKLER[sinif]
    for m in maskeler:
        overlay[m] = renk
    sonuc = cv2.addWeighted(img, 0.55, overlay, 0.45, 0)
    for m in maskeler:
        m_uint8 = (m.astype(np.uint8) * 255)
        konturlar, _ = cv2.findContours(m_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(sonuc, konturlar, -1, renk, 3)
    
    # Etiket: sinif + sayi + modu (YOLO bbox mi fallback mi)
    metin = f"{sinif} ({len(maskeler)}) [{modu}]"
    (tw, th), _ = cv2.getTextSize(metin, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv2.rectangle(sonuc, (5, 5), (15 + tw, 15 + th), (0, 0, 0), -1)
    cv2.putText(sonuc, metin, (10, 10 + th),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imwrite(str(cikti_path), sonuc, [cv2.IMWRITE_JPEG_QUALITY, 90])
 
def main():
    print("Eski ciktilar temizleniyor...")
    temizle()
    
    print("YOLOv8x (COCO pretrained) yukleniyor...")
    yolo = YOLO("yolov8x.pt")  # Buyuk model, ilk seferde ~130 MB iner
    
    print("SAM2 yukleniyor...")
    sam = SAM("sam2_b.pt")  # Zaten indi
    
    basarili = 0
    basarisiz = 0
    yolo_bulundu = 0
    fallback_kullanildi = 0
    toplam_maske = 0
    sinif_sayim = {s: 0 for s in SINIFLAR}
    
    for sinif, sinif_id in SINIFLAR.items():
        klasor = RAW_KLASOR / sinif
        fotolar = sorted(klasor.glob("*.jpg"))
        print(f"\n{sinif} ({len(fotolar)} foto)...")
        
        for foto_path in tqdm(fotolar, desc=sinif):
            try:
                img = cv2.imread(str(foto_path))
                if img is None:
                    basarisiz += 1
                    continue
                h, w = img.shape[:2]
                
                # 1) YOLO ile bbox dene
                bboxes = yolo_food_bbox_bul(yolo, img, sinif)
                
                modu = "fallback"
                maskeler_raw = None
                
                if bboxes:
                    # SAM2 prompt mode
                    maskeler_raw = sam2_prompt_ile_maskele(sam, str(foto_path), bboxes)
                    if maskeler_raw is not None and len(maskeler_raw) > 0:
                        modu = "yolo+sam"
                        yolo_bulundu += 1
                
                # Fallback: SAM2 auto
                if maskeler_raw is None or len(maskeler_raw) == 0:
                    maskeler_raw = sam2_auto_fallback(sam, str(foto_path))
                    fallback_kullanildi += 1
                
                if maskeler_raw is None:
                    basarisiz += 1
                    continue
                
                # Filtrele
                secilen_maskeler = maskeleri_filtrele(img, maskeler_raw, h, w)
                
                if not secilen_maskeler:
                    basarisiz += 1
                    continue
                
                # Polygon'a cevir, dosya yaz
                etiket_satirlari = []
                gecerli_maskeler = []
                for m in secilen_maskeler:
                    polygon = maske_to_polygon(m)
                    if polygon is None:
                        continue
                    satir = f"{sinif_id} " + " ".join(f"{c:.6f}" for c in polygon)
                    etiket_satirlari.append(satir)
                    gecerli_maskeler.append(m)
                
                if not etiket_satirlari:
                    basarisiz += 1
                    continue
                
                base = foto_path.stem
                shutil.copy(foto_path, CIKTI_IMG / f"{base}.jpg")
                with open(CIKTI_LBL / f"{base}.txt", "w") as f:
                    f.write("\n".join(etiket_satirlari) + "\n")
                preview_olustur(img, gecerli_maskeler, sinif, modu,
                              PREVIEW / sinif / f"{base}.jpg")
                
                basarili += 1
                toplam_maske += len(gecerli_maskeler)
                sinif_sayim[sinif] += 1
                
            except Exception as e:
                print(f"\nHata ({foto_path.name}): {e}")
                basarisiz += 1
    
    print("\n" + "=" * 60)
    print("HIBRIT AUTO-LABELING TAMAMLANDI")
    print(f"Basarili: {basarili}")
    print(f"Basarisiz: {basarisiz}")
    print(f"YOLO+SAM2 modu: {yolo_bulundu}")
    print(f"Fallback (SAM2 auto): {fallback_kullanildi}")
    print(f"Toplam maske: {toplam_maske}")
    print(f"Foto basina ortalama: {toplam_maske/max(basarili,1):.1f}")
    print("\nSinif dagilimi:")
    for sinif, sayi in sinif_sayim.items():
        print(f"  {sinif:20s}: {sayi} foto etiketli")
 
if __name__ == "__main__":
    main()