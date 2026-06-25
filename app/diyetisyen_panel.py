import streamlit as st
from datetime import datetime, timedelta
from app.gunluk_takip import (
    kullanicilari_role_gore_getir, kullanici_profili, kullanici_ekle,
    gunluk_ozet, son_gunler, kullanici_hedefi
)


AYLAR_TR = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}


def _tarih_tr(tarih_str):
    try:
        t = datetime.strptime(tarih_str, "%Y-%m-%d")
        return f"{t.day} {AYLAR_TR[t.month]} {t.year}"
    except Exception:
        return tarih_str


def diyetisyen_panel_goster(aktif_kullanici):
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:28px;font-weight:700;color:#1A202C;margin:0;letter-spacing:-0.5px;">
            🩺 Danışanlarım
        </h1>
        <p style="font-size:14px;color:#64748B;margin:6px 0 0;">
            Sana atanmış danışanların profillerini ve günlüklerini incele, hedeflerini belirle.
        </p>
    </div>
    """, unsafe_allow_html=True)

    from app.gunluk_takip import diyetisyenin_danisanlari
    danisanlar = diyetisyenin_danisanlari(aktif_kullanici)

    if not danisanlar:
        st.markdown("""
        <div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:14px;
                    padding:2rem;text-align:center;">
            <p style="font-size:48px;margin:0;">👥</p>
            <p style="font-size:16px;color:#64748B;margin:12px 0 0;">
                Henüz sana atanmış danışan yok.
            </p>
            <p style="font-size:13px;color:#94A3B8;margin:6px 0 0;">
                Sistem yöneticisi danışan atadığında burada görünecek.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Danisan secimi
    secili = st.session_state.get("diyetisyen_secili_danisan")
    if secili not in danisanlar:
        secili = danisanlar[0]
        st.session_state["diyetisyen_secili_danisan"] = secili

    # Danisan listesi (sol kolon) + detay (sag kolon)
    kol_sol, kol_sag = st.columns([2, 5])

    with kol_sol:
        st.markdown("**Danışanlar**")
        for d in danisanlar:
            aktif = (d == secili)
            tip = "primary" if aktif else "secondary"
            etiket = f"{'✓ ' if aktif else ''}{d}"
            if st.button(etiket, key=f"diet_dan_{d}", type=tip, use_container_width=True):
                st.session_state["diyetisyen_secili_danisan"] = d
                st.rerun()

    with kol_sag:
        _danisan_detay_goster(secili)


def _danisan_detay_goster(danisan_adi):
    profil = kullanici_profili(danisan_adi)
    hedef = kullanici_hedefi(danisan_adi)
    ozet_bugun = gunluk_ozet(danisan_adi)

    # Banner
    ilk_harf = danisan_adi[0].upper()
    email = profil.get("email", "-")

    banner_html = (
        f'<div style="background:linear-gradient(135deg,#F1F5F9 0%,#ECFDF5 100%);'
        f'border:1px solid #A7F3D0;border-radius:14px;padding:1.5rem;'
        f'display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">'
        f'<div style="width:60px;height:60px;background:#10B981;border-radius:50%;'
        f'display:inline-flex;align-items:center;justify-content:center;'
        f'font-size:24px;color:white;font-weight:600;">{ilk_harf}</div>'
        f'<div style="flex:1;">'
        f'<p style="font-size:20px;font-weight:700;color:#1A202C;margin:0;">{danisan_adi}</p>'
        f'<p style="font-size:12px;color:#64748B;margin:4px 0 0;">{email}</p>'
        f'</div>'
        f'</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)

    # Kisisel bilgiler
    yas = profil.get("yas") or "—"
    boy = profil.get("boy_cm") or "—"
    kilo = profil.get("kilo_kg") or "—"
    cinsiyet = profil.get("cinsiyet") or "—"

    bilgi_html = (
        f'<div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:14px;'
        f'padding:1.2rem;margin-bottom:1rem;display:grid;'
        f'grid-template-columns:repeat(4,1fr);gap:1rem;text-align:center;">'
        f'<div><p style="font-size:11px;color:#64748B;text-transform:uppercase;'
        f'letter-spacing:1px;margin:0;font-weight:600;">Yaş</p>'
        f'<p style="font-size:20px;color:#1A202C;font-weight:600;margin:4px 0 0;">{yas}</p></div>'
        f'<div><p style="font-size:11px;color:#64748B;text-transform:uppercase;'
        f'letter-spacing:1px;margin:0;font-weight:600;">Boy</p>'
        f'<p style="font-size:20px;color:#1A202C;font-weight:600;margin:4px 0 0;">{boy} cm</p></div>'
        f'<div><p style="font-size:11px;color:#64748B;text-transform:uppercase;'
        f'letter-spacing:1px;margin:0;font-weight:600;">Kilo</p>'
        f'<p style="font-size:20px;color:#1A202C;font-weight:600;margin:4px 0 0;">{kilo} kg</p></div>'
        f'<div><p style="font-size:11px;color:#64748B;text-transform:uppercase;'
        f'letter-spacing:1px;margin:0;font-weight:600;">Cinsiyet</p>'
        f'<p style="font-size:20px;color:#1A202C;font-weight:600;margin:4px 0 0;">{cinsiyet}</p></div>'
        f'</div>'
    )
    st.markdown(bilgi_html, unsafe_allow_html=True)

    # Hedefler ve bugunkü durum
    bugun_kal = ozet_bugun["toplam_kalori"]
    yuzde = min((bugun_kal / hedef) * 100, 100) if hedef > 0 else 0

    durum_html = (
        f'<div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:14px;'
        f'padding:1.2rem;margin-bottom:1rem;">'
        f'<p style="font-size:12px;color:#64748B;text-transform:uppercase;'
        f'letter-spacing:1px;margin:0;font-weight:600;">Bugünkü Durum</p>'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:8px;">'
        f'<p style="font-size:28px;font-weight:700;color:#10B981;margin:0;">'
        f'{bugun_kal:.0f} <span style="font-size:14px;color:#64748B;font-weight:500;">/ {hedef} kcal</span></p>'
        f'<p style="font-size:14px;color:#64748B;margin:0;">%{yuzde:.0f}</p>'
        f'</div>'
        f'<div style="height:6px;background:#E5E7EB;border-radius:10px;margin-top:8px;overflow:hidden;">'
        f'<div style="height:100%;width:{yuzde}%;background:#10B981;border-radius:10px;"></div>'
        f'</div>'
        f'<div style="display:flex;gap:1rem;margin-top:12px;">'
        f'<div style="flex:1;text-align:center;">'
        f'<p style="font-size:11px;color:#64748B;margin:0;">Protein</p>'
        f'<p style="font-size:16px;font-weight:600;color:#DC2626;margin:2px 0 0;">{ozet_bugun["toplam_protein"]:.0f} g</p>'
        f'</div>'
        f'<div style="flex:1;text-align:center;">'
        f'<p style="font-size:11px;color:#64748B;margin:0;">Karb</p>'
        f'<p style="font-size:16px;font-weight:600;color:#D97706;margin:2px 0 0;">{ozet_bugun["toplam_karb"]:.0f} g</p>'
        f'</div>'
        f'<div style="flex:1;text-align:center;">'
        f'<p style="font-size:11px;color:#64748B;margin:0;">Yağ</p>'
        f'<p style="font-size:16px;font-weight:600;color:#2563EB;margin:2px 0 0;">{ozet_bugun["toplam_yag"]:.0f} g</p>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(durum_html, unsafe_allow_html=True)

    # Hedef belirleme (Diyetisyen yetkisi)
    with st.expander("⚙️ Danışan için Hedef Belirle", expanded=False):
        st.caption("Bu danışan için günlük kalori ve protein hedefini ayarlayabilirsin.")
        h1, h2 = st.columns(2)
        with h1:
            yeni_kal = st.number_input(
                "Günlük kalori hedefi (kcal)",
                min_value=1000, max_value=5000,
                value=int(hedef), step=50,
                key=f"diet_kal_{danisan_adi}"
            )
        with h2:
            mevcut_pro = profil.get("hedef_protein_g") or 100
            yeni_pro = st.number_input(
                "Günlük protein hedefi (g)",
                min_value=0, max_value=500,
                value=int(mevcut_pro), step=5,
                key=f"diet_pro_{danisan_adi}"
            )

        if st.button("💾 Hedefleri Kaydet", type="primary", use_container_width=True, key=f"diet_kaydet_{danisan_adi}"):
            kullanici_ekle(
                danisan_adi,
                gunluk_hedef=yeni_kal,
                rol="user",
                hedef_protein_g=yeni_pro,
                yas=profil.get("yas"),
                boy_cm=profil.get("boy_cm"),
                kilo_kg=profil.get("kilo_kg"),
                cinsiyet=profil.get("cinsiyet"),
                email=profil.get("email"),
            )
            st.toast(f"✅ {danisan_adi} için hedefler güncellendi", icon="💾")
            st.rerun()

    # Tum ogun gecmisi (son 30 gun)
    st.markdown(
        '<p style="font-size:14px;font-weight:600;color:#1A202C;margin:1.5rem 0 0.8rem;">'
        '📜 Öğün Geçmişi (Son 30 Gün)</p>',
        unsafe_allow_html=True
    )

    gecmis = son_gunler(danisan_adi, gun_sayisi=30)
    if not gecmis:
        st.caption("Bu danışan henüz öğün eklemedi.")
    else:
        for gun in gecmis:
            ogun_sayisi = gun["ogun_sayisi"]
            toplam_kal = gun["toplam_kalori"]
            tarih = _tarih_tr(gun["tarih"])

            with st.expander(f"📅 {tarih}  ·  {toplam_kal:.0f} kcal  ·  {ogun_sayisi} öğün"):
                for o in gun["ogunler"]:
                    adet_txt = f" × {o.get('adet', 1)}" if o.get("adet", 1) > 1 else ""
                    o_html = (
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'padding:8px 0;border-bottom:1px solid #E5E7EB;">'
                        f'<div>'
                        f'<p style="font-size:14px;color:#1A202C;margin:0;font-weight:500;">'
                        f'{o.get("yemek", "?")}{adet_txt}</p>'
                        f'<p style="font-size:11px;color:#64748B;margin:2px 0 0;">'
                        f'⏰ {o.get("saat", "?")} · {o.get("gram", 0):.0f} g · '
                        f'P:{o.get("protein", 0):.1f} Y:{o.get("yag", 0):.1f} K:{o.get("karb", 0):.1f}</p>'
                        f'</div>'
                        f'<p style="font-size:16px;color:#10B981;margin:0;font-weight:600;">'
                        f'{o.get("kalori", 0):.0f} '
                        f'<span style="font-size:11px;color:#64748B;font-weight:500;">kcal</span></p>'
                        f'</div>'
                    )
                    st.markdown(o_html, unsafe_allow_html=True)