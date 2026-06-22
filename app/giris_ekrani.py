import streamlit as st
from app.gunluk_takip import (
    kullanicilari_getir, kullanici_ekle, kullanici_profili, kullanici_rolu
)


def _rol_ikon(rol):
    return {
        "user": "👤",
        "dietitian": "🩺",
        "admin": "🛡️",
    }.get(rol, "👤")


def _rol_etiket(rol):
    return {
        "user": "Kullanıcı",
        "dietitian": "Diyetisyen",
        "admin": "Sistem Yöneticisi",
    }.get(rol, "Kullanıcı")


def _rol_renk(rol):
    return {
        "user": "#10B981",
        "dietitian": "#D97706",
        "admin": "#2563EB",
    }.get(rol, "#10B981")


def giris_ekrani_goster():
    # CaloriAI giris ekrani - tum profilleri kart kart goster
    # Donus: secilen kullanici adi veya None

    # Logo ve baslik
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;">
        <div style="display:inline-flex;width:80px;height:80px;background:#10B981;
                    border-radius:20px;align-items:center;justify-content:center;
                    box-shadow:0 8px 24px rgba(16,185,129,0.3);font-size:42px;">
            🥗
        </div>
        <h1 style="font-size:36px;font-weight:700;color:#1A202C;margin:20px 0 8px;letter-spacing:-1px;">
            CaloriAI
        </h1>
        <p style="font-size:15px;color:#64748B;margin:0;">
            Uygulamaya giriş yapmak için bir profil seç
        </p>
    </div>
    """, unsafe_allow_html=True)

    mevcut_kullanicilar = kullanicilari_getir()

    # Hic profil yoksa zorunlu kayit
    if not mevcut_kullanicilar:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### 🚀 İlk Profil")
            st.caption("Sistemde henüz profil yok. İlk profili oluştur.")

            ad = st.text_input("Adın", placeholder="örn. Ahmet", key="ilk_ad")
            email_g = st.text_input("E-posta (opsiyonel)", placeholder="ornek@mail.com", key="ilk_email")
            hedef_g = st.number_input("Günlük kalori hedefi", min_value=1000, max_value=5000, value=2000, step=100, key="ilk_hedef")

            if st.button("Hesabı Oluştur", type="primary", use_container_width=True):
                if ad.strip():
                    kullanici_ekle(
                        ad.strip(),
                        gunluk_hedef=hedef_g,
                        rol="user",
                        email=email_g if email_g else None
                    )
                    st.session_state["aktif_kullanici"] = ad.strip()
                    st.rerun()
        return None

    # Profil kartlarini goster
    for kullanici in mevcut_kullanicilar:
        profil = kullanici_profili(kullanici)
        rol = profil.get("rol", "user")
        ikon = _rol_ikon(rol)
        etiket = _rol_etiket(rol)
        renk = _rol_renk(rol)
        ilk_harf = kullanici[0].upper()

        kol1, kol2, kol3 = st.columns([1, 5, 1])
        with kol2:
            # Once gorsel kart, sonra altinda buton
            kart_html = (
                f'<div style="background:#FFFFFF;border:1px solid #A7F3D0;border-radius:14px;'
                f'padding:1rem 1.2rem;margin-bottom:8px;'
                f'display:flex;align-items:center;gap:14px;">'
                f'<div style="width:44px;height:44px;background:{renk};border-radius:50%;'
                f'display:inline-flex;align-items:center;justify-content:center;'
                f'font-size:18px;color:white;font-weight:600;flex-shrink:0;">{ilk_harf}</div>'
                f'<div style="flex:1;">'
                f'<p style="font-size:16px;font-weight:600;color:#1A202C;margin:0;">{kullanici}</p>'
                f'<p style="font-size:12px;color:#64748B;margin:3px 0 0;">{ikon} {etiket}</p>'
                f'</div>'
                f'</div>'
            )
            st.markdown(kart_html, unsafe_allow_html=True)

            if st.button(
                f"Bu profille devam et",
                key=f"giris_btn_{kullanici}",
                use_container_width=True,
                type="primary"
            ):
                st.session_state["aktif_kullanici"] = kullanici
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

    # Yeni profil olusturma (her zaman gorunur, en altta)
    st.markdown("<br>", unsafe_allow_html=True)
    kol1, kol2, kol3 = st.columns([1, 5, 1])
    with kol2:
        with st.expander("➕ Yeni profil oluştur"):
            yeni_ad = st.text_input("Adın", placeholder="örn. Mehmet", key="yeni_ad_giris")
            yeni_email = st.text_input("E-posta (opsiyonel)", placeholder="ornek@mail.com", key="yeni_email_giris")
            yeni_hedef = st.number_input("Günlük kalori hedefi", min_value=1000, max_value=5000, value=2000, step=100, key="yeni_hedef_giris")

            st.caption("💡 Yeni profiller varsayılan olarak 'Kullanıcı' rolünde oluşturulur. Diyetisyen veya Admin rolleri için sistem yöneticisine başvurun.")

            if st.button("Profil Oluştur", type="primary", use_container_width=True, key="yeni_olustur_giris"):
                if yeni_ad.strip() and yeni_ad.strip() not in mevcut_kullanicilar:
                    kullanici_ekle(
                        yeni_ad.strip(),
                        gunluk_hedef=yeni_hedef,
                        rol="user",  # Default user
                        email=yeni_email if yeni_email else None
                    )
                    st.session_state["aktif_kullanici"] = yeni_ad.strip()
                    st.rerun()

    return None