import random
import shutil
import yaml
import zipfile
from pathlib import Path
 
# Reproducible olsun
random.seed(42)
 
DATASET = Path("data/yolo_dataset")
IMG_KLASOR = DATASET / "images"
LBL_KLASOR = DATASET / "labels"
 
# Yeni alt klasor isimleri
IMG_TRAIN = IMG_KLASOR / "train"
IMG_VAL   = IMG_KLASOR / "val"
LBL_TRAIN = LBL_KLASOR / "train"
LBL_VAL   = LBL_KLASOR / "val"
 
YAML_PATH = DATASET / "data.yaml"
ZIP_PATH = Path("yolo_dataset.zip")
 
# YOLO sinif id'leri (auto_label scriptlerinden ayni sira)
SINIF_ADLARI = ["baklava", "kebap", "lahmacun", "pirinc_pilavi"]
 
VAL_ORANI = 0.2
 
def split_yap():
    # Mevcut etiketli fotolar (her sinif icin)
    print("Etiketli fotolar taraniyor...")
    
    # Onceden split yapilmis mi kontrol et
    if IMG_TRAIN.exists() and any(IMG_TRAIN.iterdir()):
        cevap = input("Zaten train/val ayrilmis. Sifirdan yapilsin mi? (e/h): ").strip().lower()
        if cevap not in ("e", "evet", "y", "yes"):
            print("Iptal")
            return False
        # Temizle
        for k in [IMG_TRAIN, IMG_VAL, LBL_TRAIN, LBL_VAL]:
            if k.exists():
                shutil.rmtree(k)
    
    # Klasor yapisi
    for k in [IMG_TRAIN, IMG_VAL, LBL_TRAIN, LBL_VAL]:
        k.mkdir(parents=True, exist_ok=True)
    
    # Tum etiketli fotolari topla, sinifa gore grupla
    sinif_fotolari = {s: [] for s in SINIF_ADLARI}
    
    for lbl_path in LBL_KLASOR.glob("*.txt"):
        # Sinif adini dosya isminden bul
        base = lbl_path.stem
        sinif_bulundu = None
        for s in SINIF_ADLARI:
            if base.startswith(s):
                sinif_bulundu = s
                break
        
        if sinif_bulundu is None:
            print(f"  UYARI: {base} icin sinif bulunamadi, atlandi")
            continue
        
        img_path = IMG_KLASOR / f"{base}.jpg"
        if not img_path.exists():
            print(f"  UYARI: {img_path.name} bulunamadi, label atlandi")
            continue
        
        sinif_fotolari[sinif_bulundu].append((img_path, lbl_path))
    
    print("\nSinif dagilimi:")
    for s, fotos in sinif_fotolari.items():
        print(f"  {s:20s}: {len(fotos)} foto")
    
    # Her sinif icin %80 train, %20 val ayir
    train_sayim = 0
    val_sayim = 0
    
    for sinif, fotos in sinif_fotolari.items():
        random.shuffle(fotos)
        val_sayisi = int(len(fotos) * VAL_ORANI)
        train_fotos = fotos[val_sayisi:]
        val_fotos = fotos[:val_sayisi]
        
        for img, lbl in train_fotos:
            shutil.copy(img, IMG_TRAIN / img.name)
            shutil.copy(lbl, LBL_TRAIN / lbl.name)
        
        for img, lbl in val_fotos:
            shutil.copy(img, IMG_VAL / img.name)
            shutil.copy(lbl, LBL_VAL / lbl.name)
        
        train_sayim += len(train_fotos)
        val_sayim += len(val_fotos)
        print(f"  {sinif:20s}: train={len(train_fotos)}, val={len(val_fotos)}")
    
    print(f"\nToplam: train={train_sayim}, val={val_sayim}")
    return True
 
def yaml_olustur():
    # YOLO icin data.yaml
    # Colab'da klasor yolu farkli olacak, relative path kullaniyoruz
    data = {
        "path": ".",  # Colab'da datasetin koku
        "train": "images/train",
        "val": "images/val",
        "nc": len(SINIF_ADLARI),
        "names": SINIF_ADLARI
    }
    
    with open(YAML_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"\ndata.yaml olusturuldu: {YAML_PATH}")
    with open(YAML_PATH) as f:
        print(f.read())
 
def zip_hazirla():
    print("Zip hazirlaniyor...")
    
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # data.yaml'i koke koy
        zf.write(YAML_PATH, "data.yaml")
        
        # images ve labels altklasorlerini ekle
        for split in ["train", "val"]:
            img_dir = IMG_KLASOR / split
            lbl_dir = LBL_KLASOR / split
            
            for f in img_dir.glob("*.jpg"):
                zf.write(f, f"images/{split}/{f.name}")
            for f in lbl_dir.glob("*.txt"):
                zf.write(f, f"labels/{split}/{f.name}")
    
    boyut_mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f"Zip olusturuldu: {ZIP_PATH.absolute()}")
    print(f"Boyut: {boyut_mb:.1f} MB")
 
def main():
    print("=" * 60)
    print("YOLO Dataset Hazirligi")
    print("=" * 60)
    
    if not split_yap():
        return
    
    yaml_olustur()
    zip_hazirla()
    
    print("\n" + "=" * 60)
    print("TAMAMLANDI")
    print("=" * 60)
    print(f"\nColab'a yuklenecek dosya: {ZIP_PATH.absolute()}")
 
if __name__ == "__main__":
    main()
