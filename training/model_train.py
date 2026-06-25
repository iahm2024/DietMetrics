from ultralytics import YOLO
from pathlib import Path
 
DATA_YAML = "data/yolo_dataset/data.yaml"
CIKTI_KLASOR = "runs/scratch"
CIKTI_ADI = "baseline_egitim1"
 
 
def main():
    if not Path(DATA_YAML).exists():
        print(f"HATA: {DATA_YAML} bulunamadı.")
        return
 
    # Pretrained YOLO11m-seg ağırlıklarından başlıyoruz (ImageNet)
    print("YOLO11m-seg pretrained model yükleniyor (Sıfırdan Eğitim)...")
    model = YOLO("yolo11m-seg.pt")
 
    print("Eğitim başlıyor (80 epoch, lr=0.01)...")
    results = model.train(
        data=DATA_YAML,
        epochs=80,
        imgsz=640,
        batch=16,
        workers=2,
        patience=15,
        optimizer="SGD",
        lr0=0.01,           # Standart baslangic ogrenme hizi
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
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
