import streamlit as st
import json
import sys
from pathlib import Path
from PIL import Image
 
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent))
 
st.set_page_config(
    page_title="Prompt Engineers - Calori AI",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Giris ekrani kontrolu - aktif kullanici secilmemisse giris ekranina gonder
if "aktif_kullanici" not in st.session_state or st.session_state.get("aktif_kullanici") is None:
    from app.giris_ekrani import giris_ekrani_goster
    # Minimal CSS sadece giris ekrani icin
    st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F0FDF4 !important;
    }
    [data-testid="stBaseButton-primary"] {
        background-color: #10B981 !important;
        border-color: #10B981 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    [data-testid="stBaseButton-primary"]:hover {
        background-color: #059669 !important;
    }
    [data-testid="stBaseButton-secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #A7F3D0 !important;
        color: #1A202C !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        text-align: left !important;
    }
    [data-testid="stBaseButton-secondary"]:hover {
        background-color: #ECFDF5 !important;
        border-color: #10B981 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    giris_ekrani_goster()
    st.stop()
 
st.markdown("""
<style>
:root {
    --deep-carbon: #1A202C;
    --pure-bg: #F0FDF4;
    --card-bg: #F1F5F9;
    --input-bg: #FFFFFF;
    --premium-emerald: #10B981;
    --emerald-dark: #059669;
    --emerald-light: #ECFDF5;
    --emerald-soft: #D1FAE5;
    --emerald-border: #A7F3D0;
    --burnt-terracotta: #DD5A43;
    --crimson-red: #DC2626;
    --amber-gold: #D97706;
    --royal-blue: #2563EB;
    --muted-text: #64748B;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    background-color: #F0FDF4 !important;
}

[data-testid="stBaseButton-primary"] {
    background-color: #10B981 !important;
    border: 1px solid #10B981 !important;
    color: #FFFFFF !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 0.6rem 1rem !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(16,185,129,0.25) !important;
}
[data-testid="stBaseButton-primary"]:hover {
    background-color: #059669 !important;
    border-color: #059669 !important;
}

[data-testid="stBaseButton-secondary"] {
    background-color: #F1F5F9 !important;
    border: 1px solid #A7F3D0 !important;
    color: #1A202C !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    background-color: #ECFDF5 !important;
    border-color: #10B981 !important;
}

.ust_bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.2rem 0 0.8rem 0;
}
.logo_alan { display: flex; align-items: center; gap: 12px; }
.logo_daire {
    width: 44px; height: 44px;
    background: #10B981;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    color: white;
    box-shadow: 0 4px 12px rgba(16,185,129,0.35);
}
.logo_yazi {
    font-size: 22px;
    font-weight: 600;
    color: #1A202C;
    margin: 0;
    letter-spacing: -0.5px;
}
.durum_pill {
    display: flex; align-items: center; gap: 8px;
    background: #F1F5F9;
    border: 1px solid #A7F3D0;
    border-radius: 20px;
    padding: 7px 16px;
}
.durum_nokta {
    width: 8px; height: 8px;
    background: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.25);
}
.durum_yazi {
    font-size: 13px;
    color: #64748B;
    margin: 0;
    font-weight: 500;
}

.kart {
    background: #F1F5F9;
    border: 1px solid #A7F3D0;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.kart_baslik {
    font-size: 11px;
    color: #10B981;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 8px 0;
    font-weight: 600;
}

.makro_kart {
    background: #F1F5F9;
    border: 1px solid #A7F3D0;
    border-radius: 14px;
    padding: 1.5rem 1rem;
    text-align: center;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.makro_ad {
    font-size: 11px;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 10px 0;
    font-weight: 600;
}
.makro_deger {
    font-size: 48px;
    font-weight: 600;
    margin: 0;
    line-height: 1;
}
.makro_birim {
    font-size: 13px;
    color: #94A3B8;
    margin: 6px 0 0 0;
}

.bos_alan {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 400px;
    text-align: center;
    background: #F1F5F9;
    border: 2px dashed #A7F3D0;
    border-radius: 14px;
}

.tespit_kart {
    background: #F1F5F9;
    border: 1px solid #A7F3D0;
    border-left: 3px solid #10B981;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.kalori_kart {
    background: linear-gradient(135deg, #F1F5F9 0%, #D1FAE5 100%);
    border: 1px solid #10B981;
    border-radius: 14px;
    padding: 2rem 1.5rem;
    margin-bottom: 1rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(16,185,129,0.12);
}

.streamlit-expanderHeader {
    background-color: #F1F5F9 !important;
    border: 1px solid #A7F3D0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    color: #1A202C !important;
}
[data-testid="stExpander"] {
    background-color: #F1F5F9 !important;
    border: 1px solid #A7F3D0 !important;
    border-radius: 10px !important;
}

[data-testid="stMetric"] {
    background: #F1F5F9;
    border: 1px solid #A7F3D0;
    border-radius: 10px;
    padding: 12px;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #1A202C !important;
    font-weight: 600 !important;
}

hr {
    border-top: 1px solid #A7F3D0 !important;
    margin: 1rem 0 !important;
}

[data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent !important;
    border-bottom: 1px solid #A7F3D0;
}
[data-baseweb="tab"] {
    font-weight: 500;
    color: #64748B;
    background-color: transparent !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #10B981 !important;
}
[data-baseweb="tab-highlight"] {
    background-color: #10B981 !important;
}

[data-testid="stSidebar"] {
    background-color: #F1F5F9 !important;
    border-right: 1px solid #A7F3D0;
}
[data-testid="stSidebar"] * {
    color: #1A202C !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #1A202C !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    border: 1px solid #A7F3D0 !important;
    color: #1A202C !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 2px rgba(16,185,129,0.15) !important;
}

[data-testid="stSelectbox"] > div > div {
    background-color: #FFFFFF !important;
    border: 1px solid #A7F3D0 !important;
}

[data-testid="stFileUploader"] section {
    background-color: #FFFFFF !important;
    border: 2px dashed #A7F3D0 !important;
    border-radius: 10px !important;
}

.stProgress > div > div > div {
    background-color: #E5E7EB !important;
}
.stProgress > div > div > div > div {
    background-color: #10B981 !important;
}

[data-testid="stChatMessageContent"] {
    background-color: #F1F5F9 !important;
    border: 1px solid #A7F3D0;
    border-radius: 12px;
}

[data-testid="stDivider"] {
    background-color: #A7F3D0 !important;
}
</style>
""", unsafe_allow_html=True)
 
@st.cache_data
def veritabani_yukle():
    db_yolu = Path(__file__).parent.parent / "data" / "food_db.json"
    with open(db_yolu, "r", encoding="utf-8") as f:
        return json.load(f)
 
db = veritabani_yukle()

# Sidebar - aktif kullanici varsa profil bilgisi ve gunluk ozet
from app.gunluk_takip import (
    kullanicilari_getir, kullanici_ekle, gunluk_ozet, son_gunler,
    kullanici_hedefi, kullanici_profili, kullanici_rolu
)
from datetime import datetime

AYLAR_TR = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

def tarih_tr(tarih_obj):
    return f"{tarih_obj.day} {AYLAR_TR[tarih_obj.month]} {tarih_obj.year}"

aktif_kullanici = st.session_state.get("aktif_kullanici")
aktif_rol = kullanici_rolu(aktif_kullanici) if aktif_kullanici else "user"
aktif_profil = kullanici_profili(aktif_kullanici) if aktif_kullanici else {}

ROL_IKON = {"user": "👤", "dietitian": "🩺", "admin": "🛡️"}
ROL_ETIKET = {"user": "Kullanıcı", "dietitian": "Diyetisyen", "admin": "Sistem Yöneticisi"}

with st.sidebar:
    # Aktif profil karti
    rol_ikon = ROL_IKON.get(aktif_rol, "👤")
    rol_etiket = ROL_ETIKET.get(aktif_rol, "Kullanıcı")

    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #A7F3D0;border-radius:12px;
                padding:1rem;margin-bottom:1rem;text-align:center;">
        <div style="width:56px;height:56px;background:#10B981;border-radius:50%;
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:24px;color:white;margin-bottom:8px;">
            {aktif_kullanici[0].upper() if aktif_kullanici else '?'}
        </div>
        <p style="font-size:16px;font-weight:600;color:#1A202C;margin:0;">{aktif_kullanici}</p>
        <p style="font-size:12px;color:#64748B;margin:4px 0 0;">{rol_ikon} {rol_etiket}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Bugunun ozet bilgisi (sadece kendi gunlugu olanlar icin: user)
    if aktif_rol in ["user", "admin"]:
        bugun_obj = datetime.now()
        bugun_str = bugun_obj.strftime("%Y-%m-%d")
        st.markdown(
            f"### 📊 Bugünkü Özet"
            f"<br><span style='font-size:12px;color:#64748B;font-weight:normal;'>"
            f"{tarih_tr(bugun_obj)}</span>",
            unsafe_allow_html=True
        )

        ozet = gunluk_ozet(aktif_kullanici)
        kullanici_hedef = kullanici_hedefi(aktif_kullanici)

        toplam_kal = ozet["toplam_kalori"]
        hedef_orani = min(toplam_kal / kullanici_hedef, 1.0) if kullanici_hedef > 0 else 0

        st.markdown(
            f"<p style='font-size:32px;font-weight:600;color:#10B981;margin:0;line-height:1;'>"
            f"{toplam_kal:.0f}<span style='font-size:14px;color:#64748B;font-weight:400;'> / {kullanici_hedef} kcal</span></p>",
            unsafe_allow_html=True
        )
        st.progress(hedef_orani)

        kalan = kullanici_hedef - toplam_kal
        if kalan > 0:
            st.caption(f"📉 {kalan:.0f} kcal kaldı")
        else:
            st.caption(f"⚠️ Hedef aşıldı: +{abs(kalan):.0f} kcal")

        s1, s2, s3 = st.columns(3)
        s1.metric("Protein", f"{ozet['toplam_protein']:.0f}g")
        s2.metric("Yağ", f"{ozet['toplam_yag']:.0f}g")
        s3.metric("Karb", f"{ozet['toplam_karb']:.0f}g")

        st.caption(f"🍽️ {ozet['ogun_sayisi']} öğün kaydedildi")

    elif aktif_rol == "dietitian":
        st.markdown("### 🩺 Diyetisyen Paneli")
        st.caption("Danışanlarını görmek için **Danışanlar** sekmesine git.")

    if aktif_rol == "admin":
        st.divider()
        st.caption("🛡️ Admin modu aktif.")
 
YEMEK_SECENEKLERI = {
    "Baklava": "baklava",
    "Lahmacun": "lahmacun",
    "Pirinç Pilavı": "pirinc_pilavi",
    "Şiş Kebap": "kebap",
}
YEMEK_TERS = {v: k for k, v in YEMEK_SECENEKLERI.items()}
 
st.markdown("""
<div class="ust_bar">
    <div class="logo_alan">
        <div class="logo_daire">📊</div>
        <div><p class="logo_yazi">Prompt Engineers - Calori AI</p></div>
    </div>
    <div class="durum_pill">
        <div class="durum_nokta"></div>
        <p class="durum_yazi">Sistem Hazır</p>
    </div>
</div>
""", unsafe_allow_html=True)
 
st.divider()
 
# === SAYFA ROUTING ===
# Default sayfa: Dashboard
if "aktif_sayfa" not in st.session_state:
    st.session_state["aktif_sayfa"] = "Dashboard"

# Ust navigasyon barı - sayfa secim butonlari
def _nav_button(label, ikon, sayfa_adi):
    aktif = (st.session_state["aktif_sayfa"] == sayfa_adi)
    btn_tip = "primary" if aktif else "secondary"
    if st.button(f"{ikon} {label}", key=f"nav_{sayfa_adi}", use_container_width=True, type=btn_tip):
        st.session_state["aktif_sayfa"] = sayfa_adi
        st.rerun()

# Rol bazli navigasyon
nav_sayfalar = []
if aktif_rol == "user":
    nav_sayfalar = [
        ("Dashboard", "📊", "Dashboard"),
        ("Analiz", "📸", "Analiz"),
        ("Günlüğüm", "🗓️", "Gunlugum"),
        ("Tarif", "🥘", "Tarif"),
        ("Danışman", "💬", "Danisman"),
        ("Profil", "👤", "Profil"),
    ]
elif aktif_rol == "dietitian":
    nav_sayfalar = [
        ("Danışanlar", "👥", "Danisanlar"),
        ("Danışman", "💬", "Danisman"),
        ("Profil", "👤", "Profil"),
    ]
elif aktif_rol == "admin":
    nav_sayfalar = [
        ("Yönetim", "🛡️", "Admin"),
        ("Dashboard", "📊", "Dashboard"),
        ("Analiz", "📸", "Analiz"),
        ("Günlüğüm", "🗓️", "Gunlugum"),
        ("Tarif", "🥘", "Tarif"),
        ("Danışman", "💬", "Danisman"),
        ("Profil", "👤", "Profil"),
    ]

# Mevcut sayfa rol icin gecerli mi kontrol et
sayfa_anahtari = [s[2] for s in nav_sayfalar]
if st.session_state["aktif_sayfa"] not in sayfa_anahtari:
    st.session_state["aktif_sayfa"] = nav_sayfalar[0][2] if nav_sayfalar else "Dashboard"

# Navigasyon butonlari
nav_cols = st.columns(len(nav_sayfalar))
for ix, (label, ikon, sayfa) in enumerate(nav_sayfalar):
    with nav_cols[ix]:
        _nav_button(label, ikon, sayfa)

st.divider()

if st.session_state["aktif_sayfa"] == "Dashboard":
    from app.dashboard import dashboard_goster
    dashboard_goster(aktif_kullanici)
 
if st.session_state["aktif_sayfa"] == "Analiz":
    sol, bosluk, sag = st.columns([4, 1, 6])
 
    with sol:
        yuklu_fotograf = st.file_uploader(
            "Tabak fotoğrafı seç",
            type=["jpg", "jpeg", "png"],
        )
        with st.expander("📷  Kamerayla çek"):
            kamera_fotograf = st.camera_input("", label_visibility="collapsed")
 
        aktif_fotograf = yuklu_fotograf or kamera_fotograf
 
        if aktif_fotograf:
            pil_img = Image.open(aktif_fotograf).convert("RGB")

            # Foto degisirse analiz state'ini sifirla
            yeni_foto_kimlik = f"{aktif_fotograf.name}_{aktif_fotograf.size if hasattr(aktif_fotograf, 'size') else id(aktif_fotograf)}"
            if st.session_state.get("yuklu_foto_kimlik") != yeni_foto_kimlik:
                st.session_state["yuklu_foto_kimlik"] = yeni_foto_kimlik
                st.session_state["analiz_tamamlandi"] = False
                st.session_state.pop("analiz_sonucu", None)
                st.session_state.pop("manuel_gram", None)
                st.session_state.pop("manuel_carpan", None)
                st.session_state.pop("manuel_yemek", None)
                st.session_state.pop("ek_kalemler_listesi", None)
                st.session_state.pop("yemek_gramlari", None)
                st.session_state.pop("son_analiz_coklu", None)

            st.markdown("---")

            analiz_baslat = st.button(
                "🔍  Analiz Et",
                type="primary",
                width="stretch"
            )
            secilen_yemek = "baklava"
        else:
            analiz_baslat = False
            pil_img = None
            secilen_yemek = "baklava"
            st.session_state["analiz_tamamlandi"] = False
            st.session_state.pop("analiz_sonucu", None)
            st.session_state.pop("ek_kalemler_listesi", None)
            st.session_state.pop("yemek_gramlari", None)
            st.session_state.pop("son_analiz_coklu", None)
 
    with sag:
        # Analiz tetiklenirse - hesapla ve state'e kaydet
        if aktif_fotograf and analiz_baslat:
            with st.spinner("Analiz ediliyor..."):
                from app.ai_pipeline import goruntu_analiz_et
                aktif_fotograf.seek(0)
                analiz = goruntu_analiz_et(aktif_fotograf)
                tespitler = analiz.get("tespitler", [])
                maskeler = analiz.get("maskeler")

                if analiz["otomatik_tespit"] and analiz["otomatik_confidence"] > 0.45:
                    otomatik_tespit = analiz["otomatik_tespit"]
                    kullanilan_model = analiz.get("kullanilan_model", "?")
                    tespit_mesaji = ("success", f"✅ Otomatik tespit: {otomatik_tespit} ({kullanilan_model}, conf %{analiz['otomatik_confidence']*100:.0f})")
                else:
                    otomatik_tespit = secilen_yemek
                    tespit_mesaji = ("info", "ℹ️ Otomatik tespit güvenilir değil, seçilen yemek kullanildi.")

                # State'e tum analiz verilerini kaydet
                st.session_state["analiz_sonucu"] = {
                    "pil_img": pil_img,
                    "tespitler": tespitler,
                    "maskeler": maskeler,
                    "otomatik_tespit": otomatik_tespit,
                    "tespit_mesaji": tespit_mesaji,
                    "referans": analiz.get("referans"),
                    "goruntu_genisligi": pil_img.width,
                    "foto_ad": aktif_fotograf.name,
                }

                # Foto degisirse manuel ayar sifirla
                foto_id = f"{aktif_fotograf.name}_{otomatik_tespit}"
                if st.session_state.get("son_foto_id") != foto_id:
                    st.session_state["son_foto_id"] = foto_id
                    st.session_state.pop("manuel_gram", None)
                    st.session_state.pop("manuel_carpan", None)
                    st.session_state.pop("manuel_yemek", None)

       # Analiz sonucu state'te varsa goster (rerun sonrasi da gozukur)
        if st.session_state.get("analiz_sonucu"):
            sonuc = st.session_state["analiz_sonucu"]
            pil_img_son = sonuc["pil_img"]
            tespitler = sonuc["tespitler"]
            maskeler = sonuc["maskeler"]
            otomatik_tespit = sonuc["otomatik_tespit"]
            referans = sonuc["referans"]

            # Maskeli goruntu
            if maskeler is not None and len(maskeler) > 0:
                from app.seg_gorsel import maskeli_goruntu_olustur
                custom_tespitler = [t for t in tespitler if t.get("kaynak") == "custom"]
                maskeli_img = maskeli_goruntu_olustur(pil_img_son, maskeler, custom_tespitler)
                st.image(maskeli_img, width="stretch")
            else:
                st.image(pil_img_son, width="stretch")

            # ÇOKLU YEMEK MANTIGI - Custom tespitleri sinifa gore grupla
            custom_tespitler = [t for t in tespitler if t.get("kaynak") == "custom"]

            # Eger hic custom tespit yoksa fallback
            if not custom_tespitler and otomatik_tespit:
                # COCO fallback - tek yemek varsay
                tespit_gruplari = {otomatik_tespit: 1}
            elif not custom_tespitler:
                tespit_gruplari = {}
            else:
                tespit_gruplari = {}
                for t in custom_tespitler:
                    sinif = t["sinif"]
                    tespit_gruplari[sinif] = tespit_gruplari.get(sinif, 0) + 1

            # Referans nesne bilgisi
            if referans:
                st.caption(f"📏 Referans: {referans['sinif']} (%{referans['confidence']*100:.0f})")
            else:
                st.caption("📏 Referans nesne yok · ortalama porsiyon kullanildi")

            # Her sinif icin gramaj + kalori hesabi
            from app.heuristic_engine import gramaj_hesapla

            # Manuel duzeltmeler session'da tutulur (her yemek icin ayri)
            if "yemek_gramlari" not in st.session_state:
                st.session_state["yemek_gramlari"] = {}

            yemek_detaylari = []

            for sinif, adet in tespit_gruplari.items():
                if sinif not in db["turkish_classes"]:
                    continue

                y = db["turkish_classes"][sinif]

                # Otomatik gramaj
                if referans:
                    gram_tek = gramaj_hesapla(sinif, 1.0, referans, pil_img_son.width, db)
                    otomatik_gram = gram_tek * adet
                else:
                    otomatik_gram = y["avg_portion_g"] * adet

                # Manuel duzeltilmis gram varsa onu kullan
                final_gram = st.session_state["yemek_gramlari"].get(sinif, otomatik_gram)

                kal = (y["calories_per_100g"] * final_gram) / 100
                pro = (y["protein_per_100g"] * final_gram) / 100
                yg = (y["fat_per_100g"] * final_gram) / 100
                kb = (y["carbs_per_100g"] * final_gram) / 100

                yemek_detaylari.append({
                    "sinif": sinif,
                    "display_name": y["display_name"],
                    "adet": adet,
                    "birim": y.get("porsiyon_birimi", "porsiyon"),
                    "gram": final_gram,
                    "otomatik_gram": otomatik_gram,
                    "kalori": kal,
                    "protein": pro,
                    "yag": yg,
                    "karb": kb,
                    "gi": y["glycemic_index"],
                })

            # Ek kalemleri ekle (manuel girilenler)
            ek_kalemler = st.session_state.get("ek_kalemler_listesi", [])

            # BIRLESIK PANEL
            toplam_kalori = sum(y["kalori"] for y in yemek_detaylari) + sum(e["kalori"] for e in ek_kalemler)
            toplam_protein = sum(y["protein"] for y in yemek_detaylari) + sum(e["protein"] for e in ek_kalemler)
            toplam_yag = sum(y["yag"] for y in yemek_detaylari) + sum(e["yag"] for e in ek_kalemler)
            toplam_karb = sum(y["karb"] for y in yemek_detaylari) + sum(e["karb"] for e in ek_kalemler)
            toplam_gram = sum(y["gram"] for y in yemek_detaylari) + sum(e["gram"] for e in ek_kalemler)

            # Tespit edilen yemekler
            with st.container(border=True):
                st.markdown('<p class="kart_baslik">Tabaktaki Yemekler</p>', unsafe_allow_html=True)

                if not yemek_detaylari and not ek_kalemler:
                    st.markdown(
                        "<p style='color:#64748B;text-align:center;padding:1rem;'>"
                        "Tabakta tanınan yemek yok. Aşağıdan manuel ekleyebilirsin.</p>",
                        unsafe_allow_html=True
                    )
                else:
                    for yd in yemek_detaylari:
                        adet_txt = f" × {yd['adet']} {yd['birim']}" if yd['adet'] > 1 else ""
                        sat_c1, sat_c2 = st.columns([4, 1])
                        with sat_c1:
                            st.markdown(
                                f"<p style='font-size:16px;color:#1A202C;margin:0;font-weight:500;'>"
                                f"{yd['display_name']}{adet_txt}</p>"
                                f"<p style='font-size:12px;color:#64748B;margin:2px 0 8px;'>"
                                f"{yd['gram']:.0f} g</p>",
                                unsafe_allow_html=True
                            )
                        with sat_c2:
                            st.markdown(
                                f"<p style='font-size:18px;color:#DD5A43;margin:0;font-weight:500;text-align:right;'>"
                                f"{yd['kalori']:.0f}<span style='font-size:11px;color:#64748B;'> kcal</span></p>",
                                unsafe_allow_html=True
                            )

                    for ek in ek_kalemler:
                        sat_c1, sat_c2 = st.columns([4, 1])
                        with sat_c1:
                            st.markdown(
                                f"<p style='font-size:16px;color:#1A202C;margin:0;font-weight:500;'>"
                                f"+ {ek['display_name']}</p>"
                                f"<p style='font-size:12px;color:#64748B;margin:2px 0 8px;'>"
                                f"{ek['gram']:.0f} g · manuel ek</p>",
                                unsafe_allow_html=True
                            )
                        with sat_c2:
                            st.markdown(
                                f"<p style='font-size:18px;color:#2563EB;margin:0;font-weight:500;text-align:right;'>"
                                f"{ek['kalori']:.0f}<span style='font-size:11px;color:#64748B;'> kcal</span></p>",
                                unsafe_allow_html=True
                            )

            # Toplam kalori kart
            st.markdown(f"""
            <div class="kalori_kart">
                <p class="kart_baslik">Toplam Tabak Kalorisi</p>
                <p style="font-size:64px;font-weight:500;color:#DD5A43;margin:0;line-height:1;">
                    {toplam_kalori:.0f}
                </p>
                <p style="font-size:16px;color:#64748B;margin:8px 0 0;">kcal · {toplam_gram:.0f} g toplam</p>
            </div>
            """, unsafe_allow_html=True)

            # Makro kartlari
            m1, m2, m3 = st.columns(3)
            for col, ad, deger, renk in [
                (m1, "Protein", toplam_protein, "#2563EB"),
                (m2, "Yağ", toplam_yag, "#DD5A43"),
                (m3, "Karbonhidrat", toplam_karb, "#D97706"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="makro_kart">
                        <p class="makro_ad">{ad}</p>
                        <p class="makro_deger" style="color:{renk};font-size:48px;">{deger:.1f}</p>
                        <p class="makro_birim">g</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Makro dagilim cubuklari
            makro_toplam = toplam_protein + toplam_yag + toplam_karb
            if makro_toplam > 0:
                with st.container(border=True):
                    st.markdown("**Makro Dağılım**")
                    st.progress(toplam_protein / makro_toplam,
                        text=f"Protein — {toplam_protein:.1f}g  (%{toplam_protein/makro_toplam*100:.0f})")
                    st.progress(toplam_yag / makro_toplam,
                        text=f"Yağ — {toplam_yag:.1f}g  (%{toplam_yag/makro_toplam*100:.0f})")
                    st.progress(toplam_karb / makro_toplam,
                        text=f"Karbonhidrat — {toplam_karb:.1f}g  (%{toplam_karb/makro_toplam*100:.0f})")

            # MANUEL DUZELTME
            with st.expander("Sonuç doğru mu? Manuel düzeltme", expanded=False):
                st.caption("Tespit edilen bir yemeğin gramajını düzeltebilirsin.")

                if yemek_detaylari:
                    duz_yemek_secenekleri = {yd["display_name"]: yd["sinif"] for yd in yemek_detaylari}
                    secilen_label = st.selectbox(
                        "Düzeltmek istediğin yemek",
                        options=list(duz_yemek_secenekleri.keys()),
                        key="duzeltme_yemek_secimi"
                    )
                    secilen_sinif = duz_yemek_secenekleri[secilen_label]
                    mevcut_yd = next(yd for yd in yemek_detaylari if yd["sinif"] == secilen_sinif)

                    yeni_gram = st.number_input(
                        f"{mevcut_yd['display_name']} için gramaj (g)",
                        min_value=10.0,
                        max_value=2000.0,
                        value=float(mevcut_yd["gram"]),
                        step=10.0,
                        key=f"duz_gram_{secilen_sinif}"
                    )

                    dk1, dk2 = st.columns(2)
                    with dk1:
                        if st.button("Yeniden Hesapla", type="primary", use_container_width=True, key="duz_kaydet"):
                            st.session_state["yemek_gramlari"][secilen_sinif] = yeni_gram
                            st.rerun()
                    with dk2:
                        if st.button("Bu Yemeği Otomatiğe Don", use_container_width=True, key="duz_sifirla"):
                            st.session_state["yemek_gramlari"].pop(secilen_sinif, None)
                            st.rerun()
                else:
                    st.caption("Düzeltilebilecek otomatik tespit yok.")

            # MANUEL EK KALEM
            with st.expander("➕ Tabakta tanınmayan bir şey var mı? Ekle", expanded=False):
                st.caption(
                    "Sistemimiz şu an 4 yemek tipini tanıyor (baklava, lahmacun, pilav, kebap). "
                    "Tabağındaki diğer kalemleri buradan ekleyebilirsin."
                )

                EK_KATEGORI_TR = {
                    "salata": "🥗 Salatalar",
                    "icecek": "🥤 İçecekler",
                    "ekmek": "🍞 Ekmek/Lavaş",
                    "yan_yemek": "🍚 Yan Yemekler",
                    "tatli": "🍰 Tatlılar",
                    "atistirmalik": "🧀 Atıştırmalık",
                    "meyve": "🍎 Meyveler",
                }

                ek_kalemler_db = db.get("ek_kalemler", {})

                # Dropdown secenekleri
                dropdown_options = ["-- Listeden seç --"]
                option_keys = [None]
                for kat_key, kat_label in EK_KATEGORI_TR.items():
                    for ek_key, ek_val in ek_kalemler_db.items():
                        if ek_val.get("kategori") == kat_key:
                            dropdown_options.append(f"{kat_label.split()[0]} {ek_val['display_name']}")
                            option_keys.append(ek_key)
                dropdown_options.append("✏️ Listede yok, manuel gir")
                option_keys.append("__manuel__")

                secilen_idx = st.selectbox(
                    "Ne eklemek istiyorsun?",
                    options=range(len(dropdown_options)),
                    format_func=lambda i: dropdown_options[i],
                    key="ek_kalem_secim"
                )
                secilen_ek_key = option_keys[secilen_idx]

                if secilen_ek_key is None:
                    pass  # Hicbir secim yapilmamis
                elif secilen_ek_key == "__manuel__":
                    # Manuel giris formu
                    me_ad = st.text_input("Yemek/içecek adı", key="me_ad")
                    me_gram = st.number_input("Gramaj (g)", min_value=1.0, max_value=2000.0, value=100.0, step=10.0, key="me_gram")

                    me_c1, me_c2 = st.columns(2)
                    with me_c1:
                        me_kal_100 = st.number_input("Kalori (kcal/100g)", min_value=0.0, max_value=900.0, value=100.0, step=10.0, key="me_kal")
                    with me_c2:
                        me_pro_100 = st.number_input("Protein (g/100g)", min_value=0.0, max_value=100.0, value=2.0, step=0.5, key="me_pro")

                    me_c3, me_c4 = st.columns(2)
                    with me_c3:
                        me_yag_100 = st.number_input("Yağ (g/100g)", min_value=0.0, max_value=100.0, value=3.0, step=0.5, key="me_yag")
                    with me_c4:
                        me_karb_100 = st.number_input("Karbonhidrat (g/100g)", min_value=0.0, max_value=100.0, value=15.0, step=0.5, key="me_karb")

                    if st.button("➕ Manuel Kalemi Ekle", type="primary", use_container_width=True, key="me_ekle_btn"):
                        if me_ad.strip():
                            ek_yeni = {
                                "sinif_key": f"manuel_{len(ek_kalemler)}",
                                "display_name": me_ad.strip(),
                                "gram": me_gram,
                                "kalori": (me_kal_100 * me_gram) / 100,
                                "protein": (me_pro_100 * me_gram) / 100,
                                "yag": (me_yag_100 * me_gram) / 100,
                                "karb": (me_karb_100 * me_gram) / 100,
                                "gi": 0,
                                "manuel": True,
                            }
                            st.session_state.setdefault("ek_kalemler_listesi", []).append(ek_yeni)
                            st.rerun()
                else:
                    # Veritabanindan secildi
                    ek_data = ek_kalemler_db[secilen_ek_key]
                    ek_gram = st.number_input(
                        f"{ek_data['display_name']} için gramaj (g)",
                        min_value=1.0,
                        max_value=2000.0,
                        value=100.0,
                        step=10.0,
                        key=f"ek_gram_{secilen_ek_key}"
                    )

                    onizleme_kal = (ek_data["calories_per_100g"] * ek_gram) / 100
                    st.caption(f"Önizleme: ~{onizleme_kal:.0f} kcal")

                    if st.button("➕ Ekle", type="primary", use_container_width=True, key=f"ek_ekle_{secilen_ek_key}"):
                        ek_yeni = {
                            "sinif_key": secilen_ek_key,
                            "display_name": ek_data["display_name"],
                            "gram": ek_gram,
                            "kalori": (ek_data["calories_per_100g"] * ek_gram) / 100,
                            "protein": (ek_data["protein_per_100g"] * ek_gram) / 100,
                            "yag": (ek_data["fat_per_100g"] * ek_gram) / 100,
                            "karb": (ek_data["carbs_per_100g"] * ek_gram) / 100,
                            "gi": 0,
                            "manuel": False,
                        }
                        st.session_state.setdefault("ek_kalemler_listesi", []).append(ek_yeni)
                        st.rerun()

                # Eklenmis ek kalemleri listele
                if ek_kalemler:
                    st.markdown("---")
                    st.caption("**Bu öğüne manuel eklenenler:**")
                    for ix, ek in enumerate(ek_kalemler):
                        ek_c1, ek_c2 = st.columns([5, 1])
                        with ek_c1:
                            st.markdown(f"• {ek['display_name']} ({ek['gram']:.0f}g) — {ek['kalori']:.0f} kcal")
                        with ek_c2:
                            if st.button("✕", key=f"ek_sil_{ix}"):
                                ek_kalemler.pop(ix)
                                st.session_state["ek_kalemler_listesi"] = ek_kalemler
                                st.rerun()

            # GLISEMIK PROFIL
            from app.heuristic_engine import glisemik_yuk_hesapla, glisemik_yuk_siniflandir

            # Agirlikli ortalama GI hesabi (sadece karbi olan yemekler uzerinden)
            karb_li_yemekler = [yd for yd in yemek_detaylari if yd["karb"] > 0]
            toplam_karb_agirlik = sum(yd["karb"] for yd in karb_li_yemekler)

            if toplam_karb_agirlik > 0:
                agirlikli_gi = sum(yd["gi"] * yd["karb"] for yd in karb_li_yemekler) / toplam_karb_agirlik
            else:
                agirlikli_gi = 0

            gl_deger = glisemik_yuk_hesapla(agirlikli_gi, toplam_karb)
            gl_sinif = glisemik_yuk_siniflandir(gl_deger)

            if agirlikli_gi == 0:
                gi_renk = "#888888"
                gi_etiket = "Yok"
            elif agirlikli_gi <= 55:
                gi_renk = "#059669"
                gi_etiket = "Düşük"
            elif agirlikli_gi <= 69:
                gi_renk = "#DD5A43"
                gi_etiket = "Orta"
            else:
                gi_renk = "#DC2626"
                gi_etiket = "Yüksek"

            st.markdown(f"""
            <div class="kart">
                <p class="kart_baslik">Glisemik Profil (Tabak Ortalaması)</p>
                <div style="display:flex;gap:1rem;margin-top:8px;">
                    <div style="flex:1;background:#F8FAFC;border-radius:10px;padding:1rem;border-left:3px solid {gi_renk};">
                        <p style="font-size:11px;color:#64748B;margin:0 0 4px;text-transform:uppercase;letter-spacing:1px;">Ağırlıklı GI</p>
                        <p style="font-size:28px;font-weight:500;color:{gi_renk};margin:0;line-height:1;">{agirlikli_gi:.0f}</p>
                        <p style="font-size:12px;color:#64748B;margin:6px 0 0;">{gi_etiket} · karb ağırlıklı</p>
                    </div>
                    <div style="flex:1;background:#F8FAFC;border-radius:10px;padding:1rem;border-left:3px solid {gl_sinif['renk']};">
                        <p style="font-size:11px;color:#64748B;margin:0 0 4px;text-transform:uppercase;letter-spacing:1px;">Glisemik Yük</p>
                        <p style="font-size:28px;font-weight:500;color:{gl_sinif['renk']};margin:0;line-height:1;">{gl_deger:.1f}</p>
                        <p style="font-size:12px;color:#64748B;margin:6px 0 0;">{gl_sinif['etiket']} · toplam etki</p>
                    </div>
                </div>
                <p style="font-size:13px;color:#64748B;margin:12px 0 0;font-style:italic;">
                    {gl_sinif['aciklama']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # MALZEMELER
            if yemek_detaylari:
                tum_malzemeler = []
                for yd in yemek_detaylari:
                    y_db = db["turkish_classes"][yd["sinif"]]
                    tum_malzemeler.extend(y_db["ingredients"])
                tum_malzemeler = list(dict.fromkeys(tum_malzemeler))  # tekrarsiz

                st.markdown(f"""
                <div class="kart">
                    <p class="kart_baslik">Malzemeler</p>
                    <p style="color:#475569;font-size:15px;margin:8px 0 0;line-height:1.8;">
                        {'  ·  '.join(tum_malzemeler)}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # MLP KARAR AGI
            try:
                import joblib
                mlp_model_path = Path(__file__).parent.parent / "models" / "mlp_action.pkl"
                scaler_path = Path(__file__).parent.parent / "models" / "mlp_scaler.pkl"
                if mlp_model_path.exists() and scaler_path.exists():
                    mlp_model = joblib.load(mlp_model_path)
                    scaler = joblib.load(scaler_path)

                    girdi = scaler.transform([[toplam_kalori, toplam_karb, agirlikli_gi]])
                    aksiyon_id = int(mlp_model.predict(girdi)[0])

                    aksiyon_adlari = {
                        0: ("✅ Normal Beslenme", "Bu öğün dengeli. Su iç ve dinlen."),
                        1: ("⚠️ Glisemik Uyarı", "Yemekten sonra 15 dakika yürüyüş önerilir."),
                        2: ("💪 Ağır Öğün", "Protein-yağ yoğun. Sonraki öğünde hafif yiyin."),
                        3: ("🔥 Cheat Meal", "Yoğun kalori. Akşam öğününü atlamak iyi olabilir."),
                    }
                    baslik, aciklama = aksiyon_adlari[aksiyon_id]
                    st.markdown(f"""
                    <div class="kart">
                        <p class="kart_baslik">AI Önerisi (MLP Karar Ağı)</p>
                        <p style="font-size:18px;font-weight:500;color:#DD5A43;margin:0;">{baslik}</p>
                        <p style="color:#475569;font-size:14px;margin:8px 0 0;">{aciklama}</p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception:
                pass

            # GUNLUGE EKLEME STATE
            st.session_state["son_analiz_coklu"] = {
                "yemekler": yemek_detaylari,
                "ek_kalemler": ek_kalemler,
                "toplam_kalori": toplam_kalori,
                "toplam_protein": toplam_protein,
                "toplam_yag": toplam_yag,
                "toplam_karb": toplam_karb,
                "toplam_gram": toplam_gram,
            }
            st.session_state["analiz_tamamlandi"] = True

        elif aktif_fotograf and not analiz_baslat:
            st.image(pil_img, width="stretch")
        else:
            st.markdown("""
            <div class="bos_alan">
                <p style="font-size:64px;margin:0;">🍽️</p>
                <p style="color:#DD5A43;font-size:18px;font-weight:500;margin:16px 0 6px;">
                    Fotoğraf yükle ve analiz et
                </p>
                <p style="color:#94A3B8;font-size:14px;margin:0;">
                    Sonuçlar burada görünecek
                </p>
            </div>
            """, unsafe_allow_html=True)

# Gunluk ekleme butonu
    if st.session_state.get("analiz_tamamlandi") and st.session_state.get("son_analiz_coklu"):
        from app.gunluk_takip import ogun_ekle

        st.markdown("---")

        if st.session_state.get("son_ekleme_basarili"):
            st.success(f"✅ Tabakta tespit edilen tüm öğeler günlüğe eklendi!")
            st.session_state["son_ekleme_basarili"] = False

        if aktif_kullanici:
            son_analiz_c = st.session_state["son_analiz_coklu"]
            toplam_eklenecek = len(son_analiz_c["yemekler"]) + len(son_analiz_c["ek_kalemler"])

            ekle_c1, ekle_c2 = st.columns([2, 3])
            with ekle_c1:
                if st.button(
                    f"📝  Günlüğe ekle ({toplam_eklenecek} öğe)",
                    type="primary",
                    use_container_width=True,
                    key="gunluge_ekle_coklu_btn",
                    disabled=(toplam_eklenecek == 0)
                ):
                    # Her yemegi ayri ogun olarak ekle
                    for yd in son_analiz_c["yemekler"]:
                        ogun_ekle(aktif_kullanici, {
                            "yemek": yd["display_name"],
                            "gram": yd["gram"],
                            "kalori": yd["kalori"],
                            "protein": yd["protein"],
                            "yag": yd["yag"],
                            "karb": yd["karb"],
                            "adet": yd["adet"],
                        })

                    for ek in son_analiz_c["ek_kalemler"]:
                        ogun_ekle(aktif_kullanici, {
                            "yemek": ek["display_name"],
                            "gram": ek["gram"],
                            "kalori": ek["kalori"],
                            "protein": ek["protein"],
                            "yag": ek["yag"],
                            "karb": ek["karb"],
                            "adet": 1,
                        })

                    st.session_state["son_ekleme_basarili"] = True
                    # Eklenenler temizlensin yeni analiz icin
                    st.session_state["ek_kalemler_listesi"] = []
                    st.session_state["yemek_gramlari"] = {}
                    st.rerun()
            with ekle_c2:
                st.caption(
                    f"Aktif kullanıcı: **{aktif_kullanici}** · "
                    f"Tüm öğeler ayrı ayrı günlüğe yazılır"
                )
        else:
            st.info("ℹ️ Günlüğe eklemek için önce sidebar'dan bir profil oluştur")
 
if st.session_state["aktif_sayfa"] == "Danisman":
    from app.ollama_client import mesaj_gonder, ollama_calisiyor_mu
 
    if "mesajlar" not in st.session_state:
        st.session_state.mesajlar = [
            {"rol": "asistan",
             "icerik": "Merhaba! Beslenme konusunda sana yardımcı olabilirim."}
        ]
 
    if ollama_calisiyor_mu():
        st.success("🟢 Yemek danışmanı aktif")
    else:
        st.error("🔴 Ollama bağlantısı yok — terminalde 'ollama serve' çalıştır")
 
    for mesaj in st.session_state.mesajlar:
        with st.chat_message("user" if mesaj["rol"] == "kullanici" else "assistant"):
            st.write(mesaj["icerik"])
 
    kullanici_mesaji = st.chat_input("Mesajını yaz...")
    if kullanici_mesaji:
        st.session_state.mesajlar.append({"rol": "kullanici", "icerik": kullanici_mesaji})
 
        with st.spinner("Düşünüyor..."):
            # Profil ve gunluk bilgisini chatbot'a aktar
            from app.gunluk_takip import kullanici_profili as kp_getir, gunluk_ozet as go_getir, kullanici_hedefi as kh_getir

            profil_dict = kp_getir(aktif_kullanici)
            profil_dict["ad"] = aktif_kullanici  # Adi da ekle

            ozet_bilgi = go_getir(aktif_kullanici)
            gunluk_dict = {
                "toplam_kalori": ozet_bilgi["toplam_kalori"],
                "hedef": kh_getir(aktif_kullanici),
                "ogunler": ozet_bilgi["ogunler"],
            }

            cevap = mesaj_gonder(
                kullanici_mesaji,
                sohbet_gecmisi=st.session_state.mesajlar,
                yemek_bilgisi=st.session_state.get("son_analiz"),
                kullanici_profili=profil_dict,
                gunluk_durum=gunluk_dict
            )
 
        st.session_state.mesajlar.append({"rol": "asistan", "icerik": cevap})
        st.rerun()

if st.session_state["aktif_sayfa"] == "Gunlugum":
    from app.gunluk_takip import son_gunler, ogun_sil, gunu_sifirla

    if not aktif_kullanici:
        st.info("ℹ️ Günlüğü görmek için önce sidebar'dan bir profil oluştur.")
    else:
        bugun_obj_g = datetime.now()
        bugun_str_g = bugun_obj_g.strftime("%Y-%m-%d")

        st.markdown(f"### {aktif_kullanici} — Beslenme Günlüğü")
        st.caption(f"📅 {tarih_tr(bugun_obj_g)}")

        bugun_ozet_g = gunluk_ozet(aktif_kullanici, bugun_str_g)

        if bugun_ozet_g["ogun_sayisi"] == 0:
            st.markdown("""
            <div class="bos_alan">
                <p style="font-size:64px;margin:0;">📊</p>
                <p style="color:#DD5A43;font-size:18px;font-weight:500;margin:16px 0 6px;">
                    Bugün için henüz öğün kaydı yok
                </p>
                <p style="color:#94A3B8;font-size:14px;margin:0;">
                    Analiz sekmesinden öğün ekleyebilirsin
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bugun toplam kart
            kullanici_hedef_g = kullanici_hedefi(aktif_kullanici)
            hedef_orani_g = min(bugun_ozet_g["toplam_kalori"] / kullanici_hedef_g, 1.0) if kullanici_hedef_g > 0 else 0
            st.markdown(f"""
            <div class="kalori_kart">
                <p class="kart_baslik">Bugünün Toplamı</p>
                <p style="font-size:64px;font-weight:500;color:#DD5A43;margin:0;line-height:1;">
                    {bugun_ozet_g['toplam_kalori']:.0f}
                </p>
                <p style="font-size:16px;color:#64748B;margin:8px 0 0;">
                    / {kullanici_hedef_g} kcal · {bugun_ozet_g['ogun_sayisi']} öğün
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(hedef_orani_g)

            bm1, bm2, bm3 = st.columns(3)
            bm1.metric("Toplam Protein", f"{bugun_ozet_g['toplam_protein']:.0f} g")
            bm2.metric("Toplam Yağ", f"{bugun_ozet_g['toplam_yag']:.0f} g")
            bm3.metric("Toplam Karb", f"{bugun_ozet_g['toplam_karb']:.0f} g")

            st.divider()
            st.markdown("#### 🍽️ Bugünün Öğünleri")
            st.caption("Eklenme sırasına göre (sabahtan akşama)")

            # Eklenme sirasina gore (kronolojik - en eski ustte)
            ogunler_sirali = bugun_ozet_g["ogunler"]

            for idx, ogun in enumerate(ogunler_sirali):
                adet_txt = f" × {ogun['adet']}" if ogun.get("adet", 1) > 1 else ""

                st.markdown(f"""
                <div class="kart" style="margin-bottom:0.8rem;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div style="flex:1;">
                            <p style="font-size:18px;font-weight:500;color:#1A202C;margin:0;">
                                {ogun['yemek']}{adet_txt}
                            </p>
                            <p style="font-size:13px;color:#64748B;margin:4px 0 0;">
                                ⏰ {ogun['saat']}  ·  {ogun['gram']:.0f} g
                            </p>
                        </div>
                        <div style="text-align:right;">
                            <p style="font-size:24px;font-weight:500;color:#DD5A43;margin:0;line-height:1;">
                                {ogun['kalori']:.0f}
                            </p>
                            <p style="font-size:11px;color:#64748B;margin:2px 0 0;">kcal</p>
                        </div>
                    </div>
                    <div style="display:flex;gap:1rem;margin-top:12px;padding-top:12px;border-top:0.5px solid #ffffff11;">
                        <div style="flex:1;">
                            <p style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin:0;">Protein</p>
                            <p style="font-size:16px;color:#2563EB;margin:2px 0 0;font-weight:500;">{ogun['protein']:.1f}g</p>
                        </div>
                        <div style="flex:1;">
                            <p style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin:0;">Yağ</p>
                            <p style="font-size:16px;color:#DD5A43;margin:2px 0 0;font-weight:500;">{ogun['yag']:.1f}g</p>
                        </div>
                        <div style="flex:1;">
                            <p style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin:0;">Karb</p>
                            <p style="font-size:16px;color:#D97706;margin:2px 0 0;font-weight:500;">{ogun['karb']:.1f}g</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Sil butonu kartin altinda
                sil_col1, sil_col2 = st.columns([5, 1])
                with sil_col2:
                    if st.button("🗑️ Sil", key=f"sil_{bugun_str_g}_{idx}", use_container_width=True):
                        ogun_sil(aktif_kullanici, bugun_str_g, idx)
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # Bugunu sifirla
            st.markdown("""
            <style>
            div[data-testid="stButton"] button[kind="secondary"]#bugunu_sifirla_btn {
                background: transparent !important;
                color: #DC2626 !important;
                border: none !important;
                text-decoration: underline !important;
                box-shadow: none !important;
            }
            </style>
            """, unsafe_allow_html=True)

            sifirla_col1, sifirla_col2, sifirla_col3 = st.columns([2, 2, 2])
            with sifirla_col2:
                if st.button(
                    "🗑️ Bugünü Sıfırla",
                    type="secondary",
                    use_container_width=True,
                    key="bugunu_sifirla_btn",
                    help="Bugünün tüm öğünlerini siler"
                ):
                    gunu_sifirla(aktif_kullanici, bugun_str_g)
                    st.rerun()

        # Gecmis gunler (varsa)
        gecmis_tum = son_gunler(aktif_kullanici, gun_sayisi=7)
        gecmis_diger = [g for g in gecmis_tum if g["tarih"] != bugun_str_g]

        if gecmis_diger:
            st.divider()
            st.markdown("#### 📅 Önceki Günler")

            for gun in gecmis_diger:
                tarih_obj = datetime.strptime(gun["tarih"], "%Y-%m-%d")
                with st.expander(
                    f"{tarih_tr(tarih_obj)}  ·  {gun['toplam_kalori']:.0f} kcal  ·  {gun['ogun_sayisi']} öğün"
                ):
                    for ogun in gun["ogunler"]:
                        adet_txt = f" × {ogun['adet']}" if ogun.get("adet", 1) > 1 else ""
                        st.markdown(
                            f"**{ogun['saat']}** · {ogun['yemek']}{adet_txt} "
                            f"({ogun['gram']:.0f}g) · **{ogun['kalori']:.0f} kcal**"
                        )
                        st.caption(
                            f"P: {ogun['protein']:.1f}g · "
                            f"Y: {ogun['yag']:.1f}g · "
                            f"K: {ogun['karb']:.1f}g"
                        )

if st.session_state["aktif_sayfa"] == "Tarif":
    st.markdown("### 🥘 Sana Özel Tarif Önerisi")
    st.caption(
        "Dolabındaki malzemeleri yaz, sistem kalan kalorine uygun tarifler bulsun. "
        "Eksik bir şeyin varsa belirt (örn. 'sarımsağım yok'), AI uyarlayacak."
    )

    if aktif_kullanici:
        from app.gunluk_takip import gunluk_ozet, kullanici_hedefi
        ozet_t = gunluk_ozet(aktif_kullanici)
        hedef_t = kullanici_hedefi(aktif_kullanici)
        kalan_kalori_t = max(hedef_t - ozet_t["toplam_kalori"], 0)

        bilgi_c1, bilgi_c2, bilgi_c3 = st.columns(3)
        with bilgi_c1:
            st.metric("Günlük Hedef", f"{hedef_t} kcal")
        with bilgi_c2:
            st.metric("Bugün Yenen", f"{ozet_t['toplam_kalori']:.0f} kcal")
        with bilgi_c3:
            st.metric("Kalan", f"{kalan_kalori_t:.0f} kcal")

        if kalan_kalori_t <= 0:
            st.warning("⚠️ Günlük kalori limitin doldu. Yine de tarif önerilebilir.")
    else:
        st.info("ℹ️ Profil seçmeden de kullanabilirsin, ama günlük kalori takibi için sidebar'dan profil oluştur.")
        kalan_kalori_t = 2000

    st.markdown("---")

    malzeme_girdi = st.text_area(
        "🥦 Dolabındaki malzemeleri yaz",
        placeholder="örn: tavuk, domates, soğan, zeytinyağı. Sarımsağım yok.",
        height=100,
        key="tarif_malzeme_input"
    )

    with st.expander("⚙️ Kalori limitini değiştir", expanded=False):
        manuel_kalori = st.slider(
            "Tarif için kalori üst sınırı (kcal)",
            min_value=100,
            max_value=2000,
            value=int(max(kalan_kalori_t, 200)),
            step=50,
            key="tarif_manuel_kalori"
        )

    kullanilacak_kalori = st.session_state.get("tarif_manuel_kalori", int(max(kalan_kalori_t, 200)))

    if st.button("🔍 Tarif Bul", type="primary", use_container_width=True, key="tarif_bul_btn"):
        if not malzeme_girdi.strip():
            st.warning("⚠️ Lütfen malzemeleri gir.")
        else:
            with st.spinner("🔎 Tarif veritabanı taranıyor..."):
                try:
                    from app.rag_motor import (
                        tarif_bul, kisit_var_mi, kisitlari_ayikla, malzemeleri_ayikla
                    )

                    # Once kisitlari ve gercek malzemeleri ayir
                    temiz_malzemeler, olmayanlar = malzemeleri_ayikla(malzeme_girdi)
                    # FAISS'e sadece istenen malzemeleri ver
                    sorgu_metni = temiz_malzemeler if temiz_malzemeler else malzeme_girdi

                    secilen, adaylar = tarif_bul(
                        sorgu_metni,
                        kullanilacak_kalori,
                        top_k=20,
                        olmayanlar=olmayanlar
                    )

                    if secilen is None:
                        st.error("Tarif bulunamadı.")
                    else:
                        # Kaloriye uyan adaylardan ilk 3'u al (cesitlilik icin)
                        kalori_uyan_adaylar = [
                            t for t in adaylar
                            if t["kalori"] <= kullanilacak_kalori * 1.1
                        ]
                        if not kalori_uyan_adaylar:
                            kalori_uyan_adaylar = adaylar[:5]

                        # Top 3 oneri
                        st.session_state["tarif_adaylar"] = kalori_uyan_adaylar[:3]
                        st.session_state["son_tarif"] = kalori_uyan_adaylar[0] if kalori_uyan_adaylar else secilen
                        st.session_state["son_tarif_istek"] = malzeme_girdi
                        st.session_state["son_tarif_olmayanlar"] = olmayanlar
                        st.session_state["son_tarif_kisit"] = bool(olmayanlar) or kisit_var_mi(malzeme_girdi)
                        st.session_state["son_tarif_uyarlama"] = None

                except FileNotFoundError as e:
                    st.error(f"❌ {e}")
                except Exception as e:
                    st.error(f"❌ Tarif sisteminde hata: {e}")

    # Aday tarifler
    if st.session_state.get("tarif_adaylar") and len(st.session_state["tarif_adaylar"]) > 1:
        st.markdown("---")
        st.markdown("#### 📋 Sana en uygun tarifler")
        st.caption("Diğer tarifi görmek için üzerine tıkla.")

        adaylar_secim = st.session_state["tarif_adaylar"]
        secili_ad = st.session_state["son_tarif"]["ad"]
        sec_cols = st.columns(len(adaylar_secim))

        for ix, aday in enumerate(adaylar_secim):
            with sec_cols[ix]:
                aktif = (secili_ad == aday["ad"])
                btn_tip = "primary" if aktif else "secondary"

                # Buton metnini sade tut (markdown artifact olmasin)
                buton_metni = f"{aday['ad']} — {aday['kalori']:.0f} kcal"
                if aktif:
                    buton_metni = "✓ " + buton_metni

                if st.button(
                    buton_metni,
                    key=f"aday_sec_{ix}",
                    type=btn_tip,
                    use_container_width=True
                ):
                    st.session_state["son_tarif"] = aday
                    st.session_state["son_tarif_uyarlama"] = None
                    st.rerun()

    # Bulunan tarifi goster
    if st.session_state.get("son_tarif"):
        tarif = st.session_state["son_tarif"]
        kisit_var = st.session_state.get("son_tarif_kisit", False)
        olmayanlar = st.session_state.get("son_tarif_olmayanlar", [])

        st.markdown("---")

        st.markdown(f"""
        <div class="kalori_kart">
            <p class="kart_baslik">🍽️ Şefin Önerisi</p>
            <p style="font-size:28px;font-weight:500;color:#1A202C;margin:8px 0 4px;">
                {tarif['ad']}
            </p>
            <p style="font-size:16px;color:#DD5A43;margin:0;">{tarif['kalori']:.0f} kcal</p>
        </div>
        """, unsafe_allow_html=True)

        # LLM uyarlamasi
        if kisit_var:
            if st.session_state.get("son_tarif_uyarlama") is None:
                with st.spinner("🤖 AI tarifi senin kısıtlarına göre uyarlıyor..."):
                    try:
                        from app.ollama_client import tarif_uyarla, ollama_calisiyor_mu
                        if ollama_calisiyor_mu():
                            uyarlama = tarif_uyarla(
                                tarif,
                                st.session_state["son_tarif_istek"],
                                olmayan_malzemeler=olmayanlar
                            )
                            st.session_state["son_tarif_uyarlama"] = uyarlama or "Uyarlama üretilemedi."
                        else:
                            st.session_state["son_tarif_uyarlama"] = "(Ollama çalışmıyor.)"
                    except Exception as e:
                        st.session_state["son_tarif_uyarlama"] = f"(Hata: {e})"

            if st.session_state.get("son_tarif_uyarlama"):
                st.markdown(f"""
                <div class="kart" style="border-left:3px solid #2563EB;">
                    <p class="kart_baslik">🤖 AI Uyarlaması</p>
                    <p style="color:#475569;font-size:15px;margin:8px 0 0;line-height:1.6;">
                        💡 {st.session_state['son_tarif_uyarlama']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kart">
            <p class="kart_baslik">🥗 Malzemeler</p>
            <p style="color:#475569;font-size:15px;margin:8px 0 0;line-height:1.8;white-space:pre-wrap;">{tarif['malzemeler_metin']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kart">
            <p class="kart_baslik">👨‍🍳 Yapılışı</p>
            <p style="color:#475569;font-size:15px;margin:8px 0 0;line-height:1.8;white-space:pre-wrap;">{tarif['yapilis_metin']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.caption("💡 Afiyet olsun! Başka tarif için tekrar 'Tarif Bul' diyebilirsin.")
 
if st.session_state["aktif_sayfa"] == "Profil":
    from app.profil_sayfa import profil_sayfa_goster
    profil_sayfa_goster(aktif_kullanici)

# DANISANLAR SAYFASI (Diyetisyen)
if st.session_state["aktif_sayfa"] == "Danisanlar":
    from app.diyetisyen_panel import dietisyen_panel_goster
    dietisyen_panel_goster()
# ADMIN SAYFASI
if st.session_state["aktif_sayfa"] == "Admin":
    from app.admin_panel import admin_panel_goster
    admin_panel_goster(aktif_kullanici)