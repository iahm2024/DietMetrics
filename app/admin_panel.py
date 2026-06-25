import streamlit as st
from app.gunluk_takip import (
    tum_kullanicilar_detayli, kullanici_ekle, kullanici_sil,
    kullanici_profili, kullanicilari_getir
)


ROL_ETIKET = {
    "user": "Danışan",
    "dietitian": "Diyetisyen",
    "admin": "Admin"
}

ROL_RENK = {
    "user": "#10B981",
    "dietitian": "#D97706",
    "admin": "#2563EB"
}


def admin_panel_goster(aktif_kullanici):
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:28px;font-weight:700;color:#1A202C;margin:0;letter-spacing:-0.5px;">
            🛡️ Sistem Yönetimi
        </h1>
        <p style="font-size:14px;color:#64748B;margin:6px 0 0;">
            Kullanıcıları yönet, rolleri belirle, yeni profiller oluştur.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Yeni kullanici olusturma
    with st.expander("➕ Yeni Kullanıcı Oluştur (rol belirleyerek)"):
        from app.gunluk_takip import kullanici_olustur_sifreyle

        a1, a2 = st.columns(2)
        with a1:
            yeni_ad = st.text_input("Ad Soyad", key="admin_yeni_ad", placeholder="örn. Mehmet")
            yeni_email = st.text_input("Email", key="admin_yeni_email", placeholder="ornek@mail.com")
            yeni_sifre = st.text_input(
                "Şifre (en az 4 karakter)",
                type="password",
                key="admin_yeni_sifre",
                placeholder="••••••"
            )
        with a2:
            yeni_rol = st.selectbox(
                "Rol",
                options=["user", "dietitian", "admin"],
                format_func=lambda r: f"{ROL_ETIKET[r]}",
                key="admin_yeni_rol"
            )
            yeni_hedef = st.number_input(
                "Günlük kalori hedefi",
                min_value=1000, max_value=5000, value=2000, step=100,
                key="admin_yeni_hedef"
            )

        if st.button("✅ Kullanıcı Oluştur", type="primary", use_container_width=True, key="admin_yeni_btn"):
            basarili_y, hata_y = kullanici_olustur_sifreyle(
                ad=yeni_ad,
                email=yeni_email,
                sifre=yeni_sifre,
                gunluk_hedef=yeni_hedef,
                rol=yeni_rol
            )
            if basarili_y:
                st.toast(f"✅ {yeni_ad.strip()} oluşturuldu ({ROL_ETIKET[yeni_rol]})", icon="🛡️")
                st.rerun()
            else:
                st.error(f"❌ {hata_y}")

    st.markdown("---")

    # Tum kullanicilar listesi
    tum_k = tum_kullanicilar_detayli()

    # Rol bazli sayim
    user_sayi = len([k for k in tum_k if k["rol"] == "user"])
    diet_sayi = len([k for k in tum_k if k["rol"] == "dietitian"])
    admin_sayi = len([k for k in tum_k if k["rol"] == "admin"])

    sayim_html = (
        f'<div style="display:flex;gap:1rem;margin-bottom:1.5rem;">'
        f'<div style="flex:1;background:#F1F5F9;border:1px solid #A7F3D0;border-left:3px solid #10B981;'
        f'border-radius:10px;padding:1rem;text-align:center;">'
        f'<p style="font-size:11px;color:#64748B;margin:0;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Kullanıcı</p>'
        f'<p style="font-size:28px;color:#10B981;font-weight:700;margin:4px 0 0;line-height:1;">{user_sayi}</p>'
        f'</div>'
        f'<div style="flex:1;background:#F1F5F9;border:1px solid #A7F3D0;border-left:3px solid #D97706;'
        f'border-radius:10px;padding:1rem;text-align:center;">'
        f'<p style="font-size:11px;color:#64748B;margin:0;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Diyetisyen</p>'
        f'<p style="font-size:28px;color:#D97706;font-weight:700;margin:4px 0 0;line-height:1;">{diet_sayi}</p>'
        f'</div>'
        f'<div style="flex:1;background:#F1F5F9;border:1px solid #A7F3D0;border-left:3px solid #2563EB;'
        f'border-radius:10px;padding:1rem;text-align:center;">'
        f'<p style="font-size:11px;color:#64748B;margin:0;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Admin</p>'
        f'<p style="font-size:28px;color:#2563EB;font-weight:700;margin:4px 0 0;line-height:1;">{admin_sayi}</p>'
        f'</div>'
        f'</div>'
    )
    st.markdown(sayim_html, unsafe_allow_html=True)

    # Kullanici listesi - tablo gibi
    st.markdown("**Tüm Kullanıcılar**")

    for k in tum_k:
        kendisi = (k["ad"] == aktif_kullanici)
        rol = k["rol"]
        rol_renk = ROL_RENK.get(rol, "#10B981")
        rol_etiket = ROL_ETIKET.get(rol, "Kullanıcı")
        ilk_harf = k["ad"][0].upper()

        with st.container(border=True):
            k1, k2, k3 = st.columns([4, 2, 2])

            with k1:
                k_html = (
                    f'<div style="display:flex;align-items:center;gap:12px;">'
                    f'<div style="width:36px;height:36px;background:{rol_renk};border-radius:50%;'
                    f'display:inline-flex;align-items:center;justify-content:center;'
                    f'font-size:16px;color:white;font-weight:600;">{ilk_harf}</div>'
                    f'<div>'
                    f'<p style="font-size:15px;color:#1A202C;margin:0;font-weight:600;">{k["ad"]}'
                    f'{" (sen)" if kendisi else ""}</p>'
                    f'<p style="font-size:11px;color:#64748B;margin:2px 0 0;">{k["email"]}</p>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(k_html, unsafe_allow_html=True)

            with k2:
                # Rol degistirme
                rol_index = ["user", "dietitian", "admin"].index(rol)
                yeni_rol = st.selectbox(
                    "Rol",
                    options=["user", "dietitian", "admin"],
                    format_func=lambda r: ROL_ETIKET[r],
                    index=rol_index,
                    key=f"admin_rol_{k['ad']}",
                    label_visibility="collapsed",
                    disabled=kendisi  # Kendi rolunu degistiremesin
                )
                if yeni_rol != rol and not kendisi:
                    profil = kullanici_profili(k["ad"])
                    kullanici_ekle(
                        k["ad"],
                        gunluk_hedef=profil.get("gunluk_hedef", 2000),
                        rol=yeni_rol,
                        yas=profil.get("yas"),
                        boy_cm=profil.get("boy_cm"),
                        kilo_kg=profil.get("kilo_kg"),
                        cinsiyet=profil.get("cinsiyet"),
                        hedef_protein_g=profil.get("hedef_protein_g"),
                        email=profil.get("email")
                    )
                    st.toast(f"{k['ad']} → {ROL_ETIKET[yeni_rol]}", icon="🔄")
                    st.rerun()

            with k3:
                # User rolune diyetisyen ata
                if rol == "user" and not kendisi:
                    from app.gunluk_takip import (
                        kullanici_profili as kp_admin,
                        diyetisyen_ata, diyetisyen_kaldir,
                        kullanicilari_role_gore_getir as krgg
                    )

                    profil_k = kp_admin(k["ad"])
                    mevcut_diet = profil_k.get("atanmis_diyetisyen", "—")

                    tum_diyetisyenler = krgg("dietitian")
                    secenekler = ["(Atanmamış)"] + tum_diyetisyenler

                    mevcut_idx = 0
                    if mevcut_diet in tum_diyetisyenler:
                        mevcut_idx = secenekler.index(mevcut_diet)

                    secilen_diet = st.selectbox(
                        "Diyetisyen",
                        options=secenekler,
                        index=mevcut_idx,
                        key=f"admin_diet_{k['ad']}",
                        label_visibility="collapsed"
                    )

                    if secilen_diet != (mevcut_diet if mevcut_diet in secenekler else "(Atanmamış)"):
                        if secilen_diet == "(Atanmamış)":
                            diyetisyen_kaldir(k["ad"])
                            st.toast(f"🔓 {k['ad']} → diyetisyen kaldırıldı", icon="🔓")
                        else:
                            diyetisyen_ata(k["ad"], secilen_diet)
                            st.toast(f"🔗 {k['ad']} → {secilen_diet}", icon="🔗")
                        st.rerun()
                elif kendisi:
                    st.caption("Yönetici")
                else:
                    st.caption("—")
            
            # Sifre sifirlama (Admin yetkisi)
            if not kendisi:
                with st.expander(f"🔑 {k['ad']} için şifre sıfırla"):
                    from app.gunluk_takip import sifre_degistir
                    yeni_sifre_a = st.text_input(
                        "Yeni şifre (en az 4 karakter)",
                        type="password",
                        key=f"admin_yeni_sifre_{k['ad']}",
                        placeholder="••••••"
                    )
                    if st.button(
                        "Şifreyi Güncelle",
                        key=f"admin_sifre_btn_{k['ad']}",
                        use_container_width=True
                    ):
                        basarili_s, hata_s = sifre_degistir(k["ad"], yeni_sifre_a)
                        if basarili_s:
                            st.toast(f"🔑 {k['ad']} şifresi güncellendi", icon="🔑")
                            st.rerun()
                        else:
                            st.error(f"❌ {hata_s}")

            # Sil butonu
            if not kendisi:
                onay_key = f"admin_sil_onay_{k['ad']}"
                if st.session_state.get(onay_key):
                    sa, sb = st.columns(2)
                    with sa:
                        if st.button("❌ Vazgeç", key=f"admin_vazgec_{k['ad']}", use_container_width=True):
                            st.session_state[onay_key] = False
                            st.rerun()
                    with sb:
                        if st.button("✅ Sil!", key=f"admin_sil_onayli_{k['ad']}",
                                    use_container_width=True, type="primary"):
                            kullanici_sil(k["ad"])
                            st.session_state[onay_key] = False
                            st.toast(f"🗑️ {k['ad']} silindi", icon="🗑️")
                            st.rerun()
                else:
                    if st.button("🗑️ Bu kullanıcıyı sil", key=f"admin_sil_{k['ad']}",
                                use_container_width=True):
                        st.session_state[onay_key] = True
                        st.rerun()