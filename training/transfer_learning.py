from ultralytics import YOLO
from pathlib import Path
 
MEVCUT_MODEL = "models/best1.pt"
DATA_YAML = "data/yolo_dataset/data.yaml"
 
def main():
    if not Path(MEVCUT_MODEL).exists():
        print(f"HATA: {MEVCUT_MODEL} bulunamadi.")
        return
    
    if not Path(DATA_YAML).exists():
        print(f"HATA: {DATA_YAML} bulunamadi.")
        return
    
    print("Mevcut model yukleniyor...")
    model = YOLO(MEVCUT_MODEL)
    
    print("Transfer learning basliyor...")
    results = model.train(
        data=DATA_YAML,
        epochs=25,
        imgsz=640,
        batch=4,
        workers=2,           
        patience=10,
        optimizer="SGD",
        lr0=0.001,         # Dusuk LR, ince ayar
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=2,
        freeze=10,         # Ilk 10 katman donduruldu
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
        # Cikti
        project="runs/transfer",
        name="baklava_fix",
        save=True,
        device=0,          # GPU
        verbose=True
    )
    
    print("\nEgitim tamamlandi")
    
    # Validation
    print("\nValidation metrikleri:")
    best_model = YOLO("CaloriProject/models")
    metrics = best_model.val(data=DATA_YAML)
    print(f"mAP50 (mask): {metrics.seg.map50:.3f}")
    print(f"mAP50-95 (mask): {metrics.seg.map:.3f}")
 
if __name__ == "__main__":
    main()