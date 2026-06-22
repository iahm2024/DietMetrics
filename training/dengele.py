import random
import sys
from pathlib import Path
 
HEDEF_SAYI = 250
RAW_KLASOR = Path("data/raw_images")
SINIFLAR = ["baklava", "kebap", "lahmacun", "pirinc_pilavi"]
 
def dengele(hedef):
    # Seed sabit, herkes ayni sonucu alir (tekrar uretilebilirlik)
    random.seed(42)
    
    print("=" * 60)
    print(f"Hedef: her sinif {hedef} foto")
    print("=" * 60)
    
    # Once durumu goster
    print("\nMevcut durum:")
    for sinif in SINIFLAR:
        klasor = RAW_KLASOR / sinif
        if not klasor.exists():
            print(f"  HATA: {klasor} bulunamadi")
            return
        sayim = len(list(klasor.glob("*.jpg")))
        print(f"  {sinif:20s}: {sayim} foto")
    
    # Onay sor
    cevap = input(f"\nDevam edilsin mi? Fazla fotolar SILINECEK (e/h): ").strip().lower()
    if cevap not in ("e", "evet", "y", "yes"):
        print("Iptal edildi")
        return
    
    print("\nDengeleme basliyor...")
    
    for sinif in SINIFLAR:
        klasor = RAW_KLASOR / sinif
        fotolar = sorted(klasor.glob("*.jpg"))
        mevcut = len(fotolar)
        
        if mevcut <= hedef:
            print(f"  {sinif:20s}: {mevcut} foto, hedefin altinda, dokunulmadi")
            continue
        
        # Rastgele hedef kadar foto sec
        secilenler = random.sample(fotolar, hedef)
        secilen_set = set(secilenler)
        
        # Secilmeyenler silinecek
        silinecek = [f for f in fotolar if f not in secilen_set]
        
        print(f"  {sinif:20s}: {mevcut} -> {hedef} ({len(silinecek)} silinecek)")
        
        for f in silinecek:
            f.unlink()
    
    # Sonuc goster
    print("\nSonuc:")
    toplam = 0
    for sinif in SINIFLAR:
        klasor = RAW_KLASOR / sinif
        sayim = len(list(klasor.glob("*.jpg")))
        print(f"  {sinif:20s}: {sayim} foto")
        toplam += sayim
    print(f"  {'TOPLAM':20s}: {toplam} foto")
 
if __name__ == "__main__":
    hedef = HEDEF_SAYI
    if len(sys.argv) > 1:
        try:
            hedef = int(sys.argv[1])
        except ValueError:
            print(f"Gecersiz sayi: {sys.argv[1]}")
            sys.exit(1)
    
    dengele(hedef)