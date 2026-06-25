from ultralytics import YOLO
from pathlib import Path
 
# Transfer learning - Eğitim 1 üzerinde ince ayar
 
MEVCUT_MODEL = "models/best1.pt"   # Egitim 1 sonucu
DATA_YAML = "data/yolo_dataset/data.yaml"
CIKTI_KLASOR = "runs/transfer"
CIKTI_ADI = "baklava_fix_final"
 
 
def main():
    if not Path(MEVCUT_MODEL).exists():
        print(f"HATA: {MEVCUT_MODEL} bulunamadı.")
        return
 
    if not Path(DATA_YAML).exists():
        print(f"HATA: {DATA_YAML} bulunamadı.")
        return
 
    print(f"Baseline model yükleniyor: {MEVCUT_MODEL}")
    model = YOLO(MEVCUT_MODEL)
 
    # Üst katmanlar Türk yemeği özelliklerini öğrenir, alt katmanlar korunur
    # lr0=0.001: düşük öğrenme hızı, mevcut ağırlıkları bozmadan ince ayar yapar
    print("Transfer learning başlıyor (freeze=10, lr=0.001, 25 epoch)...")
    results = model.train(
        data=DATA_YAML,
        epochs=25,
        imgsz=640,
        batch=4,
        workers=2,
        patience=10,
        optimizer="SGD",
        lr0=0.001,          # Düşük LR - mevcut ağırlıkları korur
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=2,
        freeze=10,          # Ilk 10 katman donduruldu
        # Augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=15,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        # Çıktı
        project=CIKTI_KLASOR,
        name=CIKTI_ADI,
        save=True,
        device=0,
        verbose=True
    )
 
    print("\nEğitim tamamlandı, validation başlıyor...")
    best_model = YOLO(f"{CIKTI_KLASOR}/{CIKTI_ADI}/weights/best.pt")
    metrics = best_model.val(data=DATA_YAML)
 
    print("\n--- SONUÇLAR ---")
    print(f"Genel mAP50 (mask):    {metrics.seg.map50:.3f}")
    print(f"Genel mAP50-95 (mask): {metrics.seg.map:.3f}")
    print(f"Model: {CIKTI_KLASOR}/{CIKTI_ADI}/weights/best.pt")
 
 
if __name__ == "__main__":
    main()