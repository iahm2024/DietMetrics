import streamlit as st
from app.gunluk_takip import gunluk_ozet, kullanici_hedefi, ogun_sil, gunu_sifirla, son_gunler

from datetime import datetime
AYLAR_TR = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

def tarih_tr(tarih_obj):
    return f"{tarih_obj.day} {AYLAR_TR[tarih_obj.month]} {tarih_obj.year}"

def gunlugum_sayfa_goster(aktif_kullanici):

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