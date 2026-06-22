import os
from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm
 
# Bizim 4 sinifimiz, dataset'teki etiket numaralari ile
HEDEF_SINIFLAR = {
    1: "baklava",
    14: "kebap",
    17: "lahmacun",
    21: "pirinc_pilavi"
}
 
# Cikti klasoru (proje yapisina uygun)
CIKTI_KLASORU = Path("data/raw_images")
 
def main():
    print("=" * 60)
    print("TurkishFoods-25 indirme islemi basliyor")
    print("=" * 60)
    
    # Cikti klasorlerini olustur
    for sinif_adi in HEDEF_SINIFLAR.values():
        klasor = CIKTI_KLASORU / sinif_adi
        klasor.mkdir(parents=True, exist_ok=True)
        print(f"  Klasor hazir: {klasor}")
    
    print("\nDataset indiriliyor (~116 MB, ilk seferde 2-3 dk)...")
    # Hugging Face cache'ine indirilir, ikinci calistirmada hizli
    ds = load_dataset("yunusserhat/TurkishFoods-25")
    
    print(f"\nDataset yuklendi:")
    print(f"  Train: {len(ds['train'])} gorsel")
    print(f"  Eval:  {len(ds['eval'])} gorsel")
    print(f"  Test:  {len(ds['test'])} gorsel")
    
    # Train + Eval + Test hepsini birlestir, hepsinden gorseller alalim
    sayaclar = {sinif: 0 for sinif in HEDEF_SINIFLAR.values()}
    
    for split_adi in ["train", "eval", "test"]:
        print(f"\n{split_adi} split isleniyor...")
        split = ds[split_adi]
        
        for ornek in tqdm(split, desc=split_adi):
            etiket = ornek["label"]
            
            # Sadece bizim siniflarimiz
            if etiket not in HEDEF_SINIFLAR:
                continue
            
            sinif_adi = HEDEF_SINIFLAR[etiket]
            sayaclar[sinif_adi] += 1
            
            # Goruntu PIL Image olarak gelir
            gorsel = ornek["image"]
            
            # Numarali dosya adi
            dosya_adi = f"{sinif_adi}_{sayaclar[sinif_adi]:04d}.jpg"
            cikti_yolu = CIKTI_KLASORU / sinif_adi / dosya_adi
            
            # RGB'ye cevir (bazi gorseller RGBA olabilir)
            if gorsel.mode != "RGB":
                gorsel = gorsel.convert("RGB")
            
            # JPEG olarak kaydet, kaliteyi yuksek tut
            gorsel.save(cikti_yolu, "JPEG", quality=92)
    
    print("\n" + "=" * 60)
    print("INDIRME TAMAMLANDI")
    print("=" * 60)
    
    toplam = 0
    for sinif_adi, sayi in sayaclar.items():
        klasor = CIKTI_KLASORU / sinif_adi
        boyut_mb = sum(f.stat().st_size for f in klasor.glob("*.jpg")) / (1024 * 1024)
        print(f"  {sinif_adi:20s}: {sayi:4d} gorsel ({boyut_mb:.1f} MB)")
        toplam += sayi
    print(f"  {'TOPLAM':20s}: {toplam:4d} gorsel")
    print(f"\nKlasor: {CIKTI_KLASORU.absolute()}")
 
if __name__ == "__main__":
    main()