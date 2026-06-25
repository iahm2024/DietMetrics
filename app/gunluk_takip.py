import json
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import secrets
import re


LOG_YOLU = Path(__file__).parent.parent / "data" / "gunluk_log.json"


def log_yukle():
    if not LOG_YOLU.exists():
        return {}
    try:
        with open(LOG_YOLU, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def log_kaydet(log):
    LOG_YOLU.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_YOLU, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def kullanicilari_getir():
    log = log_yukle()
    # Sadece kullanici objesi olanlari don (eski format dosyalar icin guvenli)
    return sorted([k for k, v in log.items() if isinstance(v, dict)])


def kullanici_ekle(kullanici_adi, gunluk_hedef=2000, rol="user",
                   yas=None, boy_cm=None, kilo_kg=None, cinsiyet=None,
                   hedef_protein_g=None, email=None):
    # Profil olustur veya guncelle
    log = log_yukle()

    profil_data = {
        "gunluk_hedef": int(gunluk_hedef),
        "rol": rol,
        "yas": yas,
        "boy_cm": boy_cm,
        "kilo_kg": kilo_kg,
        "cinsiyet": cinsiyet,
        "hedef_protein_g": hedef_protein_g,
        "email": email or f"{kullanici_adi.lower()}@example.com",
    }

    if kullanici_adi not in log:
        log[kullanici_adi] = {
            "_profil": profil_data,
            "gunler": {}
        }
    else:
        if "_profil" not in log[kullanici_adi]:
            eski_gunler = {k: v for k, v in log[kullanici_adi].items() if k != "_profil"}
            log[kullanici_adi] = {
                "_profil": profil_data,
                "gunler": eski_gunler
            }
        else:
            # Mevcut profili korurken sadece dolu alanlari guncelle
            mevcut_profil = log[kullanici_adi]["_profil"]
            for k, v in profil_data.items():
                if v is not None:
                    mevcut_profil[k] = v

    log_kaydet(log)


def kullanici_hedefi(kullanici_adi):
    log = log_yukle()
    if kullanici_adi in log and isinstance(log[kullanici_adi], dict):
        profil = log[kullanici_adi].get("_profil", {})
        return profil.get("gunluk_hedef", 2000)
    return 2000


def _kullanici_gunleri(log, kullanici_adi):
    # Eski ve yeni format icin gunleri don
    if kullanici_adi not in log:
        return {}
    veri = log[kullanici_adi]
    if not isinstance(veri, dict):
        return {}
    if "gunler" in veri:
        return veri["gunler"]
    # Eski format - direkt tarih key'leri
    return {k: v for k, v in veri.items() if k != "_profil"}


def ogun_ekle(kullanici_adi, ogun):
    log = log_yukle()

    if kullanici_adi not in log:
        log[kullanici_adi] = {
            "_profil": {"gunluk_hedef": 2000},
            "gunler": {}
        }

    # Yeni formata zorla
    if "gunler" not in log[kullanici_adi]:
        eski_gunler = {k: v for k, v in log[kullanici_adi].items() if k != "_profil"}
        log[kullanici_adi] = {
            "_profil": log[kullanici_adi].get("_profil", {"gunluk_hedef": 2000}),
            "gunler": eski_gunler
        }

    bugun = datetime.now().strftime("%Y-%m-%d")
    simdi = datetime.now().strftime("%H:%M")

    gunler = log[kullanici_adi]["gunler"]
    if bugun not in gunler:
        gunler[bugun] = {"ogunler": []}

    ogun_kayit = {
        "saat": simdi,
        "yemek": ogun.get("yemek", "?"),
        "gram": round(ogun.get("gram", 0), 1),
        "kalori": round(ogun.get("kalori", 0), 1),
        "protein": round(ogun.get("protein", 0), 1),
        "yag": round(ogun.get("yag", 0), 1),
        "karb": round(ogun.get("karb", 0), 1),
        "adet": ogun.get("adet", 1),
    }

    gunler[bugun]["ogunler"].append(ogun_kayit)
    log_kaydet(log)
    return True


def ogun_sil(kullanici_adi, tarih, index):
    log = log_yukle()
    gunler = _kullanici_gunleri(log, kullanici_adi)
    if tarih in gunler:
        ogunler = gunler[tarih].get("ogunler", [])
        if 0 <= index < len(ogunler):
            ogunler.pop(index)
            # Yeni formata kaydet
            if "gunler" in log[kullanici_adi]:
                log[kullanici_adi]["gunler"] = gunler
            else:
                log[kullanici_adi] = gunler
            log_kaydet(log)
            return True
    return False


def gunu_sifirla(kullanici_adi, tarih=None):
    if tarih is None:
        tarih = datetime.now().strftime("%Y-%m-%d")

    log = log_yukle()
    gunler = _kullanici_gunleri(log, kullanici_adi)
    if tarih in gunler:
        del gunler[tarih]
        if "gunler" in log[kullanici_adi]:
            log[kullanici_adi]["gunler"] = gunler
        else:
            log[kullanici_adi] = gunler
        log_kaydet(log)
        return True
    return False


def gunluk_ozet(kullanici_adi, tarih=None):
    if tarih is None:
        tarih = datetime.now().strftime("%Y-%m-%d")

    log = log_yukle()
    gunler = _kullanici_gunleri(log, kullanici_adi)

    if tarih not in gunler:
        return {
            "toplam_kalori": 0,
            "toplam_protein": 0,
            "toplam_yag": 0,
            "toplam_karb": 0,
            "ogun_sayisi": 0,
            "ogunler": []
        }

    ogunler = gunler[tarih].get("ogunler", [])
    return {
        "toplam_kalori": sum(o.get("kalori", 0) for o in ogunler),
        "toplam_protein": sum(o.get("protein", 0) for o in ogunler),
        "toplam_yag": sum(o.get("yag", 0) for o in ogunler),
        "toplam_karb": sum(o.get("karb", 0) for o in ogunler),
        "ogun_sayisi": len(ogunler),
        "ogunler": ogunler
    }


def son_gunler(kullanici_adi, gun_sayisi=7):
    log = log_yukle()
    gunler = _kullanici_gunleri(log, kullanici_adi)
    if not gunler:
        return []

    bugun = datetime.now().date()
    sonuc = []

    for i in range(gun_sayisi):
        tarih_obj = bugun - timedelta(days=i)
        tarih = tarih_obj.strftime("%Y-%m-%d")
        if tarih in gunler:
            ozet = gunluk_ozet(kullanici_adi, tarih)
            ozet["tarih"] = tarih
            sonuc.append(ozet)

    return sonuc

def kullanici_profili(kullanici_adi):
    # Tum profil bilgisini don
    log = log_yukle()
    if kullanici_adi in log and isinstance(log[kullanici_adi], dict):
        return log[kullanici_adi].get("_profil", {})
    return {}


def kullanici_rolu(kullanici_adi):
    profil = kullanici_profili(kullanici_adi)
    return profil.get("rol", "user")


def kullanicilari_role_gore_getir(rol):
    # Belirli bir roldeki tum kullanicilari listele
    log = log_yukle()
    sonuc = []
    for k, v in log.items():
        if isinstance(v, dict):
            profil = v.get("_profil", {})
            if profil.get("rol", "user") == rol:
                sonuc.append(k)
    return sorted(sonuc)


def kullanici_sil(kullanici_adi):
    log = log_yukle()
    if kullanici_adi in log:
        del log[kullanici_adi]
        log_kaydet(log)
        return True
    return False


def tum_kullanicilar_detayli():
    # Admin paneli icin
    log = log_yukle()
    sonuc = []
    for k, v in log.items():
        if isinstance(v, dict):
            profil = v.get("_profil", {})
            sonuc.append({
                "ad": k,
                "rol": profil.get("rol", "user"),
                "email": profil.get("email", "-"),
                "hedef_kalori": profil.get("gunluk_hedef", 2000),
            })
    return sorted(sonuc, key=lambda x: (x["rol"], x["ad"]))

def diyetisyen_ata(user_adi, diyetisyen_adi):
    # Bir user'a diyetisyen ata
    log = log_yukle()
    if user_adi in log and isinstance(log[user_adi], dict):
        if "_profil" not in log[user_adi]:
            log[user_adi]["_profil"] = {}
        log[user_adi]["_profil"]["atanmis_diyetisyen"] = diyetisyen_adi
        log_kaydet(log)
        return True
    return False


def diyetisyen_kaldir(user_adi):
    log = log_yukle()
    if user_adi in log and isinstance(log[user_adi], dict):
        if "_profil" in log[user_adi]:
            log[user_adi]["_profil"].pop("atanmis_diyetisyen", None)
            log_kaydet(log)
            return True
    return False


def diyetisyenin_danisanlari(diyetisyen_adi):
    # Belirli bir diyetisyene atanan tum user'lari listele
    log = log_yukle()
    sonuc = []
    for k, v in log.items():
        if not isinstance(v, dict):
            continue
        profil = v.get("_profil", {})
        if profil.get("rol") == "user" and profil.get("atanmis_diyetisyen") == diyetisyen_adi:
            sonuc.append(k)
    return sorted(sonuc)


def kullanicinin_diyetisyeni(user_adi):
    profil = kullanici_profili(user_adi)
    return profil.get("atanmis_diyetisyen")

# SIFRE VE GIRIS YONETIMI

def _sifre_hashle(sifre, salt=None):
    # SHA-256 + salt ile sifreyi hash'le
    if salt is None:
        salt = secrets.token_hex(16)
    hash_str = hashlib.sha256((salt + sifre).encode("utf-8")).hexdigest()
    return f"{salt}${hash_str}"


def _sifre_dogrula(sifre, hash_kayit):
    # Kaydedilmis hash'i kontrol et
    if not hash_kayit or "$" not in hash_kayit:
        return False
    try:
        salt, kayit_hash = hash_kayit.split("$", 1)
        beklenen = hashlib.sha256((salt + sifre).encode("utf-8")).hexdigest()
        return secrets.compare_digest(beklenen, kayit_hash)
    except Exception:
        return False


def email_gecerli_mi(email):
    # Basit email regex kontrolu
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def kullanici_olustur_sifreyle(ad, email, sifre, gunluk_hedef=2000, rol="user"):
    # Yeni kullanici olustur. Donus: (basarili, hata_mesaji)
    ad = ad.strip()
    email = email.strip().lower()

    if not ad:
        return False, "Ad boş olamaz"
    if not email_gecerli_mi(email):
        return False, "Geçersiz email formatı"
    if not sifre or len(sifre) < 4:
        return False, "Şifre en az 4 karakter olmalı"

    log = log_yukle()

    # Ayni email ile kayitli kullanici var mi
    for k, v in log.items():
        if not isinstance(v, dict):
            continue
        profil = v.get("_profil", {})
        if profil.get("email", "").lower() == email:
            return False, "Bu email zaten kayıtlı"

    if ad in log:
        return False, "Bu kullanıcı adı zaten alınmış"

    sifre_hash = _sifre_hashle(sifre)

    log[ad] = {
        "_profil": {
            "rol": rol,
            "email": email,
            "sifre_hash": sifre_hash,
            "gunluk_hedef": int(gunluk_hedef),
        },
        "gunler": {}
    }
    log_kaydet(log)
    return True, None


def giris_yap(email, sifre):
    # Email + sifre ile kimlik dogrulama. Donus: (basarili, kullanici_adi_veya_hata)
    if not email or not sifre:
        return False, "Email ve şifre gerekli"

    email = email.strip().lower()
    log = log_yukle()

    for k, v in log.items():
        if not isinstance(v, dict):
            continue
        profil = v.get("_profil", {})
        if profil.get("email", "").lower() == email:
            kayitli_hash = profil.get("sifre_hash")
            if kayitli_hash and _sifre_dogrula(sifre, kayitli_hash):
                return True, k
            else:
                return False, "Şifre hatalı"

    return False, "Bu email ile kayıtlı kullanıcı bulunamadı"


def sifre_degistir(kullanici_adi, yeni_sifre):
    # Admin yetkisi ile sifre degistirme (eski sifre sormaz)
    if not yeni_sifre or len(yeni_sifre) < 4:
        return False, "Şifre en az 4 karakter olmalı"

    log = log_yukle()
    if kullanici_adi not in log or not isinstance(log[kullanici_adi], dict):
        return False, "Kullanıcı bulunamadı"

    if "_profil" not in log[kullanici_adi]:
        log[kullanici_adi]["_profil"] = {}

    log[kullanici_adi]["_profil"]["sifre_hash"] = _sifre_hashle(yeni_sifre)
    log_kaydet(log)
    return True, None