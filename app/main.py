import streamlit as st
import json
import sys
from pathlib import Path
from PIL import Image
 
sys.path.insert(0, str(Path(__file__).parent.parent))
 
st.set_page_config(
    page_title="Prompt Engineers - DietMetrics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Giris ekrani kontrolu - aktif kullanici secilmemisse giris ekranina gonder
if "aktif_kullanici" not in st.session_state or st.session_state.get("aktif_kullanici") is None:
    from app.giris_ekrani import giris_ekrani_goster
    
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

with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
 
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
ROL_ETIKET = {"user": "Danışan", "dietitian": "Diyetisyen", "admin": "Sistem Yöneticisi"}

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
 
st.markdown("""
<div class="ust_bar">
    <div class="logo_alan">
        <div class="logo_daire">📊</div>
        <div><p class="logo_yazi">Prompt Engineers - DietMetrics</p></div>
    </div>
    <div class="durum_pill">
        <div class="durum_nokta"></div>
        <p class="durum_yazi">Sistem Hazır</p>
    </div>
</div>
""", unsafe_allow_html=True)
 
st.divider()
 
# Sayfa Yönlendirme
# Default sayfa: Anasayfa
if "aktif_sayfa" not in st.session_state:
    st.session_state["aktif_sayfa"] = "Anasayfa"

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
        ("Anasayfa", "📊", "Anasayfa"),
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
        ("Anasayfa", "📊", "Anasayfa"),
        ("Analiz", "📸", "Analiz"),
        ("Günlüğüm", "🗓️", "Gunlugum"),
        ("Tarif", "🥘", "Tarif"),
        ("Danışman", "💬", "Danisman"),
        ("Profil", "👤", "Profil"),
    ]

# Mevcut sayfa rol icin gecerli mi kontrol et
sayfa_anahtari = [s[2] for s in nav_sayfalar]
if st.session_state["aktif_sayfa"] not in sayfa_anahtari:
    st.session_state["aktif_sayfa"] = nav_sayfalar[0][2] if nav_sayfalar else "Anasayfa"

# Navigasyon butonlari
nav_cols = st.columns(len(nav_sayfalar))
for ix, (label, ikon, sayfa) in enumerate(nav_sayfalar):
    with nav_cols[ix]:
        _nav_button(label, ikon, sayfa)

st.divider()

if st.session_state["aktif_sayfa"] == "Anasayfa":
    from app.dashboard import dashboard_goster
    dashboard_goster(aktif_kullanici)
 
if st.session_state["aktif_sayfa"] == "Analiz":
    from app.analiz_sayfa import analiz_sayfa_goster
    analiz_sayfa_goster(aktif_kullanici, db)

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
    from app.danisman_sayfa import danisman_sayfa_goster
    danisman_sayfa_goster(aktif_kullanici)

if st.session_state["aktif_sayfa"] == "Gunlugum":
    from app.gunlugum_sayfa import gunlugum_sayfa_goster
    gunlugum_sayfa_goster(aktif_kullanici)

if st.session_state["aktif_sayfa"] == "Tarif":
    from app.tarif_sayfa import tarif_sayfa_goster
    tarif_sayfa_goster(aktif_kullanici)
 
if st.session_state["aktif_sayfa"] == "Profil":
    from app.profil_sayfa import profil_sayfa_goster
    profil_sayfa_goster(aktif_kullanici)

# DANISANLAR SAYFASI (Diyetisyen)
if st.session_state["aktif_sayfa"] == "Danisanlar":
    from app.diyetisyen_panel import diyetisyen_panel_goster
    diyetisyen_panel_goster(aktif_kullanici)
# ADMIN SAYFASI
if st.session_state["aktif_sayfa"] == "Admin":
    from app.admin_panel import admin_panel_goster
    admin_panel_goster(aktif_kullanici)