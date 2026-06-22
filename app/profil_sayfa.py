import streamlit as st
from datetime import datetime
from app.gunluk_takip import (
    kullanici_profili, kullanici_ekle, kullanici_hedefi, son_gunler
)


ROL_ETIKET = {
    "user": "Kullanıcı",
    "dietitian": "Diyetisyen",
    "admin": "Sistem Yöneticisi"
}

ROL_RENK = {
    "user": "#10B981",
    "dietitian": "#D97706",
    "admin": "#2563EB"
}


def profil_sayfa_goster(aktif_kullanici):
    profil = kullanici_profili(aktif_kullanici)
    rol = profil.get("rol", "user")
    rol_renk = ROL_RENK.get(rol, "#10B981")
    email = profil.get("email", f"{aktif_kullanici.lower()}@example.com")

    # Ust banner - avatar + temel bilgi
    ilk_harf = aktif_kullanici[0].upper()

    banner_html = (
        f'<div style="background:linear-gradient(135deg,#F1F5F9 0%,#ECFDF5 100%);'
        f'border:1px solid #A7F3D0;border-radius:14px;padding:2rem;margin-bottom:1.5rem;'
        f'text-align:center;">'
        f'<div style="width:80px;height:80px;background:{rol_renk};border-radius:50%;'
        f'display:inline-flex;align-items:center;justify-content:center;'
        f'font-size:32px;color:white;font-weight:600;margin-bottom:12px;'
        f'box-shadow:0 4px 12px rgba(16,185,129,0.25);">{ilk_harf}</div>'
        f'<h1 style="font-size:26px;font-weight:700;color:#1A202C;margin:0;'
        f'letter-spacing:-0.5px;">{aktif_kullanici}</h1>'
        f'<p style="font-size:13px;color:#64748B;margin:6px 0 0;">{email}</p>'
        f'<div style="display:inline-block;margin-top:10px;padding:4px 12px;'
        f'background:white;border:1px solid {rol_renk};border-radius:20px;'
        f'font-size:12px;color:{rol_renk};font-weight:600;">'
        f'{ROL_ETIKET.get(rol, "Kullanıcı")}</div>'
        f'</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)

    # Hedef bilgileri - 2 kart yan yana
    hedef_kalori = profil.get("gunluk_hedef", 2000)
    hedef_protein = profil.get("hedef_protein_g") or 0

    hedef_html = (
        f'<div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:14px;'
        f'padding:1.5rem;margin-bottom:1.5rem;display:flex;justify-content:space-around;">'
        f'<div style="text-align:center;flex:1;">'
        f'<p style="font-size:11px;color:#64748B;text-transform:uppercase;'
        f'letter-spacing:1px;margin:0;font-weight:600;">Hedef Kalori</p>'
        f'<p style="font-size:32px;font-weight:700;color:#10B981;margin:8px 0 0;'
        f'line-height:1;">{hedef_kalori}'
        f'<span style="font-size:14px;color:#64748B;font-weight:500;"> kcal</span></p>'
        f'</div>'
        f'<div style="width:1px;background:#A7F3D0;"></div>'
        f'<div style="text-align:center;flex:1;">'
        f'<p style="font-size:11px;color:#64748B;text-transform:uppercase;'
        f'letter-spacing:1px;margin:0;font-weight:600;">Hedef Protein</p>'
        f'<p style="font-size:32px;font-weight:700;color:#DC2626;margin:8px 0 0;'
        f'line-height:1;">{hedef_protein or "—"}'
        f'<span style="font-size:14px;color:#64748B;font-weight:500;"> g</span></p>'
        f'</div>'
        f'</div>'
    )
    st.markdown(hedef_html, unsafe_allow_html=True)

    # Kisisel bilgiler - duzenlenebilir
    with st.expander("✏️ Kişisel Bilgilerimi Düzenle", expanded=False):
        st.caption("Bu bilgiler chatbot'taki kalori hesaplaması ve diyetisyenin görmesi için kullanılır.")

        d1, d2 = st.columns(2)
        with d1:
            yas_g = st.number_input(
                "Yaş",
                min_value=10, max_value=120,
                value=int(profil.get("yas") or 25),
                step=1,
                key="profil_yas"
            )
            kilo_g = st.number_input(
                "Kilo (kg)",
                min_value=30.0, max_value=300.0,
                value=float(profil.get("kilo_kg") or 70),
                step=0.5,
                key="profil_kilo"
            )
        with d2:
            boy_g = st.number_input(
                "Boy (cm)",
                min_value=100, max_value=250,
                value=int(profil.get("boy_cm") or 170),
                step=1,
                key="profil_boy"
            )
            cinsiyet_secenekleri = ["Belirtilmemiş", "Erkek", "Kadın"]
            mevcut_cinsiyet = profil.get("cinsiyet") or "Belirtilmemiş"
            if mevcut_cinsiyet not in cinsiyet_secenekleri:
                mevcut_cinsiyet = "Belirtilmemiş"
            cinsiyet_g = st.selectbox(
                "Cinsiyet",
                options=cinsiyet_secenekleri,
                index=cinsiyet_secenekleri.index(mevcut_cinsiyet),
                key="profil_cinsiyet"
            )

        st.markdown("**Hedefler**")
        h1, h2 = st.columns(2)
        with h1:
            yeni_kalori = st.number_input(
                "Günlük kalori hedefi (kcal)",
                min_value=1000, max_value=5000,
                value=int(hedef_kalori),
                step=50,
                key="profil_kalori_hedef"
            )
        with h2:
            yeni_protein = st.number_input(
                "Günlük protein hedefi (g)",
                min_value=0, max_value=500,
                value=int(hedef_protein) if hedef_protein else 100,
                step=5,
                key="profil_protein_hedef"
            )

        if st.button("💾 Kaydet", type="primary", use_container_width=True, key="profil_kaydet_btn"):
            kullanici_ekle(
                aktif_kullanici,
                gunluk_hedef=yeni_kalori,
                rol=rol,
                yas=yas_g,
                boy_cm=boy_g,
                kilo_kg=kilo_g,
                cinsiyet=cinsiyet_g if cinsiyet_g != "Belirtilmemiş" else None,
                hedef_protein_g=yeni_protein,
                email=email
            )
            st.toast("✅ Profil güncellendi", icon="💾")
            st.rerun()

    # Son aktiviteler
    st.markdown(
        '<p style="font-size:14px;font-weight:600;color:#1A202C;margin:1.5rem 0 0.8rem;">'
        '⏱️ Son Aktiviteler</p>',
        unsafe_allow_html=True
    )

    gecmis = son_gunler(aktif_kullanici, gun_sayisi=7)
    tum_ogunler = []
    for gun in gecmis:
        for ogun in gun["ogunler"]:
            tum_ogunler.append({
                "tarih": gun["tarih"],
                "saat": ogun.get("saat", "-"),
                "yemek": ogun.get("yemek", "-"),
                "adet": ogun.get("adet", 1),
                "gram": ogun.get("gram", 0),
                "kalori": ogun.get("kalori", 0),
            })

    # En yeni 5 aktiviteyi al
    tum_ogunler = tum_ogunler[:5] if len(tum_ogunler) > 5 else tum_ogunler

    if not tum_ogunler:
        st.markdown(
            '<div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:14px;'
            'padding:1.5rem;text-align:center;color:#64748B;font-size:14px;">'
            'Henüz aktivite yok. Analiz sekmesinden öğün ekleyebilirsin.'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for ogun in tum_ogunler:
            adet_txt = f" × {ogun['adet']}" if ogun["adet"] > 1 else ""
            tarih_obj = datetime.strptime(ogun["tarih"], "%Y-%m-%d")
            tarih_kisa = tarih_obj.strftime("%d/%m")

            aktivite_html = (
                f'<div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:10px;'
                f'padding:12px 16px;margin-bottom:8px;display:flex;'
                f'justify-content:space-between;align-items:center;">'
                f'<div>'
                f'<p style="font-size:14px;color:#1A202C;margin:0;font-weight:500;">'
                f'{ogun["yemek"]}{adet_txt}</p>'
                f'<p style="font-size:11px;color:#64748B;margin:2px 0 0;">'
                f'{tarih_kisa} · {ogun["saat"]} · {ogun["gram"]:.0f} g</p>'
                f'</div>'
                f'<p style="font-size:16px;font-weight:600;color:#10B981;margin:0;">'
                f'{ogun["kalori"]:.0f}'
                f'<span style="font-size:11px;color:#64748B;font-weight:500;"> kcal</span></p>'
                f'</div>'
            )
            st.markdown(aktivite_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cikis butonu
    c1, c2, c3 = st.columns([2, 2, 2])
    with c2:
        if st.button(
            "🚪 Çıkış Yap",
            use_container_width=True,
            key="profil_cikis_btn"
        ):
            # Tum state'i temizle ve giris ekranina don
            st.session_state["aktif_kullanici"] = None
            for k in [
                "analiz_sonucu", "analiz_tamamlandi", "son_analiz_coklu",
                "ek_kalemler_listesi", "yemek_gramlari", "mesajlar",
                "son_tarif", "tarif_adaylar", "aktif_sayfa"
            ]:
                st.session_state.pop(k, None)
            st.rerun()