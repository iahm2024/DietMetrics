import streamlit as st
from app.gunluk_takip import (
    giris_yap, kullanici_olustur_sifreyle, kullanicilari_getir
)


def giris_ekrani_goster():
    # DietMetrics giris/kayit ekrani

    # Logo ve baslik
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;">
        <div style="display:inline-flex;width:80px;height:80px;background:#10B981;
                    border-radius:20px;align-items:center;justify-content:center;
                    box-shadow:0 8px 24px rgba(16,185,129,0.3);font-size:42px;">
            🥗
        </div>
        <h1 style="font-size:36px;font-weight:700;color:#1A202C;margin:20px 0 8px;letter-spacing:-1px;">
            DietMetrics
        </h1>
        <p style="font-size:15px;color:#64748B;margin:0;">
            Yapay zeka destekli beslenme asistanın
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Form kapsayicisi - ortalanmis
    kol1, kol2, kol3 = st.columns([1, 3, 1])

    with kol2:
        sekme_giris, sekme_kayit = st.tabs(["🔐 Giriş Yap", "✨ Kayıt Ol"])

        # === GIRIS SEKMESI ===
        with sekme_giris:
            st.markdown("<br>", unsafe_allow_html=True)

            g_email = st.text_input(
                "Email",
                key="giris_email",
                placeholder="ornek@mail.com",
            )
            g_sifre = st.text_input(
                "Şifre",
                type="password",
                key="giris_sifre",
                placeholder="••••••",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Giriş Yap", type="primary", use_container_width=True, key="giris_btn"):
                basarili, sonuc = giris_yap(g_email, g_sifre)
                if basarili:
                    st.session_state["aktif_kullanici"] = sonuc
                    st.rerun()
                else:
                    st.error(f"❌ {sonuc}")

            # Hic kullanici yoksa hatirlatma
            if not kullanicilari_getir():
                st.info("ℹ️ Henüz hiç kullanıcı kaydı yok. Önce 'Kayıt Ol' sekmesinden hesap oluştur.")

        # KAYIT SEKMESI
        with sekme_kayit:
            st.markdown("<br>", unsafe_allow_html=True)

            k_ad = st.text_input(
                "Ad Soyad",
                key="kayit_ad",
                placeholder="örn. Ahmet",
            )
            k_email = st.text_input(
                "Email",
                key="kayit_email",
                placeholder="ornek@mail.com",
            )

            ks1, ks2 = st.columns(2)
            with ks1:
                k_sifre = st.text_input(
                    "Şifre (en az 4 karakter)",
                    type="password",
                    key="kayit_sifre",
                    placeholder="••••••",
                )
            with ks2:
                k_sifre2 = st.text_input(
                    "Şifre tekrar",
                    type="password",
                    key="kayit_sifre2",
                    placeholder="••••••",
                )

            k_hedef = st.number_input(
                "Günlük kalori hedefi (kcal)",
                min_value=1000,
                max_value=5000,
                value=2000,
                step=100,
                key="kayit_hedef",
                help="Yetişkin ortalama: 2000 kcal. Sonradan profil sayfasından değiştirebilirsin.",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Hesap Oluştur", type="primary", use_container_width=True, key="kayit_btn"):
                if not k_ad.strip():
                    st.error("❌ Ad boş olamaz")
                elif not k_sifre or len(k_sifre) < 4:
                    st.error("❌ Şifre en az 4 karakter olmalı")
                elif k_sifre != k_sifre2:
                    st.error("❌ Şifreler eşleşmiyor")
                else:
                    basarili, hata = kullanici_olustur_sifreyle(
                        ad=k_ad,
                        email=k_email,
                        sifre=k_sifre,
                        gunluk_hedef=k_hedef,
                        rol="user"
                    )
                    if basarili:
                        st.success(f"✅ Hesap oluşturuldu! Şimdi giriş yapabilirsin.")
                        st.session_state["aktif_kullanici"] = k_ad.strip()
                        st.rerun()
                    else:
                        st.error(f"❌ {hata}")

    return None