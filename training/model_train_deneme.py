import csv
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
 
# Her deneyde yalnızca tek parametre değiştiriliyor, geri kalan her şey sabit.
 
DATA_YAML = "data/yolo_dataset/data.yaml"
SONUC_CSV = "training/ablation_sifirdan_sonuclari.csv"
 
# Tüm deneylerde sabit kalan parametreler
# Burada değişiklik yapılmamalı - kontrollü deney şartları için
SABIT = dict(
    epochs=80,
    imgsz=640,
    batch=16,
    workers=2,
    patience=15,
    lr0=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3,
    optimizer="SGD",
    # Augmentation - tam set
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=15,
    translate=0.1,
    scale=0.5,
    fliplr=0.5,
    mosaic=1.0,
    mixup=0.1,
    save=True,
    device=0,
    verbose=False,
    project="runs/ablation_scratch",
)
 
# Her deneyde sadece ilgili parametre override ediliyor
DENEYLER = [
    {
        "ad": "Deney_B_bizim_secim",
        "aciklama": "Referans: yolo11m-seg, 80 epoch, SGD, tam augmentation",
        "model": "yolo11m-seg.pt",
        "override": {},
    },
    {
        "ad": "Deney_M4_buyuk_model",
        "aciklama": "Büyük model (yolo11l-seg) - daha fazla parametre, daha uzun eğitim",
        "model": "yolo11l-seg.pt",
        "override": {},  # model dışında hiçbir şey değişmedi
    },
    {
        "ad": "Deney_A2_temel_augmentation",
        "aciklama": "Sadece temel augmentation (flip+HSV), mosaic ve mixup kapalı",
        "model": "yolo11m-seg.pt",
        "override": {
            "mosaic": 0.0,   # mosaic kapalı
            "mixup": 0.0,    # mixup kapalı
        },
    },
    {
        "ad": "Deney_E4_120_epoch",
        "aciklama": "Daha uzun eğitim (120 epoch) - overfit riski var mı kontrolü",
        "model": "yolo11m-seg.pt",
        "override": {
            "epochs": 120,
        },
    },
    {
        "ad": "Deney_O2_adam",
        "aciklama": "Adam optimizer (lr=0.001) - YOLO için SGD kadar stabil değil",
        "model": "yolo11m-seg.pt",
        "override": {
            "optimizer": "Adam",
            "lr0": 0.001,    # Adam için tipik başlangıç öğrenme hızı
        },
    },
]
 
 
def deney_calistir(deney):
    print(f"\n{'='*60}")
    print(f"DENEY : {deney['ad']}")
    print(f"NOT   : {deney['aciklama']}")
 
    # Sabit parametreler üzerine sadece override uygula
    parametreler = {**SABIT, **deney["override"]}
    parametreler["name"] = deney["ad"]
 
    epochs = parametreler.get("epochs", 80)
    print(
        f"MODEL : {deney['model']} | "
        f"epoch={epochs} | "
        f"opt={parametreler['optimizer']} | "
        f"lr={parametreler['lr0']} | "
        f"mosaic={parametreler['mosaic']} | "
        f"mixup={parametreler['mixup']}"
    )
    print(f"{'='*60}")
 
    model = YOLO(deney["model"])
    model.train(data=DATA_YAML, **parametreler)
 
    best_pt = Path(f"runs/ablation_scratch/{deney['ad']}/weights/best.pt")
    if not best_pt.exists():
        print(f"UYARI: best.pt bulunamadı -> {best_pt}")
        return None
 
    best_model = YOLO(str(best_pt))
    metrics = best_model.val(data=DATA_YAML, verbose=False)
 
    sinif_skorlari = {}
    if hasattr(metrics.seg, "ap_class_index"):
        sinif_adlari = ["baklava", "kebap", "lahmacun", "pirinc_pilavi"]
        for i, idx in enumerate(metrics.seg.ap_class_index):
            if i < len(metrics.seg.ap50):
                sinif_skorlari[sinif_adlari[idx]] = round(float(metrics.seg.ap50[i]), 4)
 
    sonuc = {
        "deney": deney["ad"],
        "aciklama": deney["aciklama"],
        "model": deney["model"],
        "epochs": epochs,
        "optimizer": parametreler["optimizer"],
        "lr0": parametreler["lr0"],
        "mosaic": parametreler["mosaic"],
        "mixup": parametreler["mixup"],
        "map50_mask": round(metrics.seg.map50, 4),
        "map50_95_mask": round(metrics.seg.map, 4),
        "baklava": sinif_skorlari.get("baklava", "-"),
        "kebap": sinif_skorlari.get("kebap", "-"),
        "lahmacun": sinif_skorlari.get("lahmacun", "-"),
        "pilav": sinif_skorlari.get("pirinc_pilavi", "-"),
        "model_yolu": str(best_pt),
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
 
    print(f"SONUÇ -> genel mAP50: {sonuc['map50_mask']:.4f}")
    print(
        f"         baklava={sonuc['baklava']} | "
        f"kebap={sonuc['kebap']} | "
        f"lahmacun={sonuc['lahmacun']} | "
        f"pilav={sonuc['pilav']}"
    )
    return sonuc
 
 
def _val_yukle(deney, best_pt):
    # Tamamlanmış deneyi yeniden eğitmeden sadece val sonucunu çeker
    best_model = YOLO(str(best_pt))
    metrics = best_model.val(data=DATA_YAML, verbose=False)
    params = {**SABIT, **deney["override"]}
    epochs = params.get("epochs", 80)
 
    sinif_skorlari = {}
    if hasattr(metrics.seg, "ap_class_index"):
        sinif_adlari = ["baklava", "kebap", "lahmacun", "pirinc_pilavi"]
        for i, idx in enumerate(metrics.seg.ap_class_index):
            if i < len(metrics.seg.ap50):
                sinif_skorlari[sinif_adlari[idx]] = round(float(metrics.seg.ap50[i]), 4)
 
    return {
        "deney": deney["ad"],
        "aciklama": deney["aciklama"],
        "model": deney["model"],
        "epochs": epochs,
        "optimizer": params["optimizer"],
        "lr0": params["lr0"],
        "mosaic": params["mosaic"],
        "mixup": params["mixup"],
        "map50_mask": round(metrics.seg.map50, 4),
        "map50_95_mask": round(metrics.seg.map, 4),
        "baklava": sinif_skorlari.get("baklava", "-"),
        "kebap": sinif_skorlari.get("kebap", "-"),
        "lahmacun": sinif_skorlari.get("lahmacun", "-"),
        "pilav": sinif_skorlari.get("pirinc_pilavi", "-"),
        "model_yolu": str(best_pt),
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
 
 
def sonuclari_yazdir(sonuclar):
    referans = next((s for s in sonuclar if "Deney_B" in s["deney"]), None)
    sirali = sorted(sonuclar, key=lambda x: x["map50_mask"], reverse=True)
 
    print("\n" + "="*75)
    print("ABLASYON SONUÇLARI - SIFIRDAN EĞİTİM")
    print("="*75)
    print(f"{'Sıra':<4} {'Deney':<32} {'mAP50':>6}  {'Fark':>7}  Açıklama")
    print("-"*75)
 
    for i, s in enumerate(sirali, 1):
        fark_str = "    -  "
        if referans and s["deney"] != referans["deney"]:
            fark = s["map50_mask"] - referans["map50_mask"]
            isaretli = f"+{fark*100:.1f}p" if fark >= 0 else f"{fark*100:.1f}p"
            fark_str = f"{isaretli:>7}"
 
        etiket = " <- REFERANS" if referans and s["deney"] == referans["deney"] else ""
        print(
            f"{i:<4} {s['deney']:<32} {s['map50_mask']:>6.4f}  "
            f"{fark_str}  {s['aciklama'][:28]}{etiket}"
        )
 
    print("="*75)
 
    print("\nSINIF BAZLI mAP50:")
    print(f"{'Deney':<32} {'baklava':>8} {'kebap':>7} {'lahmacun':>9} {'pilav':>7}")
    print("-"*65)
    for s in sirali:
        print(
            f"{s['deney']:<32} {str(s['baklava']):>8} {str(s['kebap']):>7} "
            f"{str(s['lahmacun']):>9} {str(s['pilav']):>7}"
        )
 
 
def sonuclari_csv_yaz(sonuclar):
    csv_yolu = Path(SONUC_CSV)
    csv_yolu.parent.mkdir(parents=True, exist_ok=True)
 
    alanlar = [
        "deney", "aciklama", "model", "epochs", "optimizer", "lr0",
        "mosaic", "mixup", "map50_mask", "map50_95_mask",
        "baklava", "kebap", "lahmacun", "pilav", "model_yolu", "tarih"
    ]
    with open(csv_yolu, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=alanlar)
        writer.writeheader()
        writer.writerows(sonuclar)
 
    print(f"\nCSV kaydedildi: {csv_yolu}")
 
 
def main():
    if not Path(DATA_YAML).exists():
        print(f"HATA: {DATA_YAML} bulunamadı.")
        return
 
    print(f"Ablasyon çalışması - {len(DENEYLER)} deney")
    print("Sabit: yolo11m-seg, 80 epoch, batch=16, SGD, lr=0.01, tam augmentation")
    print("Her deneyde yalnızca bir parametre değiştiriliyor.\n")
 
    sonuclar = []
    for deney in DENEYLER:
        best_pt = Path(f"runs/ablation_scratch/{deney['ad']}/weights/best.pt")
        if best_pt.exists():
            print(f"Atlıyor (tamamlanmış): {deney['ad']}")
            sonuclar.append(_val_yukle(deney, best_pt))
            continue
 
        sonuc = deney_calistir(deney)
        if sonuc:
            sonuclar.append(sonuc)
 
    if sonuclar:
        sonuclari_yazdir(sonuclar)
        sonuclari_csv_yaz(sonuclar)
 
 
if __name__ == "__main__":
    main()
