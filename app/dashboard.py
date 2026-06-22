import streamlit as st
from datetime import datetime, timedelta
from app.gunluk_takip import (
    gunluk_ozet, kullanici_hedefi, kullanici_profili, son_gunler
)


AYLAR_TR = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

GUN_KISA = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


def _haftalik_veri(kullanici_adi):
    # Son 7 gunun kalori toplamlarini liste olarak don
    bugun = datetime.now().date()
    sonuc = []
    for i in range(6, -1, -1):  # 6 gun once -> bugun
        tarih_obj = bugun - timedelta(days=i)
        tarih = tarih_obj.strftime("%Y-%m-%d")
        ozet = gunluk_ozet(kullanici_adi, tarih)
        gun_idx = tarih_obj.weekday()  # 0=Pazartesi
        sonuc.append({
            "gun": GUN_KISA[gun_idx],
            "tarih": tarih,
            "kalori": ozet["toplam_kalori"],
            "bugun_mu": (i == 0),
        })
    return sonuc


def dashboard_goster(aktif_kullanici):
    profil = kullanici_profili(aktif_kullanici)
    ozet = gunluk_ozet(aktif_kullanici)
    hedef = kullanici_hedefi(aktif_kullanici)

    toplam_kal = ozet["toplam_kalori"]
    kalan = max(hedef - toplam_kal, 0)
    yuzde = min((toplam_kal / hedef) * 100, 100) if hedef > 0 else 0

    # Karsilama
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:32px;font-weight:700;color:#1A202C;margin:0;letter-spacing:-1px;">
            Merhaba, <span style="color:#10B981;">{aktif_kullanici}</span>
        </h1>
        <p style="font-size:14px;color:#64748B;margin:6px 0 0;">
            Bugün harika gidiyorsun!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Kalan kalori karti - buyuk gosterim
    daire_renk = "#10B981" if yuzde < 90 else ("#D97706" if yuzde < 110 else "#DC2626")
    daire_oran = min(yuzde / 100, 1.0)

    st.markdown(f"""
    <div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:14px;
                padding:1.8rem 2rem;margin-bottom:1.5rem;
                display:flex;justify-content:space-between;align-items:center;">
        <div>
            <p style="font-size:13px;color:#64748B;text-transform:uppercase;
                      letter-spacing:1px;margin:0;font-weight:600;">Kalan Kalori</p>
            <p style="font-size:56px;font-weight:700;color:#1A202C;margin:8px 0 0;line-height:1;">
                {kalan:.0f}<span style="font-size:18px;color:#64748B;font-weight:500;"> kcal</span>
            </p>
            <p style="font-size:13px;color:#64748B;margin:8px 0 0;">
                Hedef: {hedef} kcal · Yenen: {toplam_kal:.0f} kcal
            </p>
        </div>
        <div style="position:relative;width:100px;height:100px;">
            <svg width="100" height="100" viewBox="0 0 100 100" style="transform:rotate(-90deg);">
                <circle cx="50" cy="50" r="42" fill="none" stroke="#E5E7EB" stroke-width="8"/>
                <circle cx="50" cy="50" r="42" fill="none" stroke="{daire_renk}" stroke-width="8"
                        stroke-dasharray="{2 * 3.14159 * 42}"
                        stroke-dashoffset="{2 * 3.14159 * 42 * (1 - daire_oran)}"
                        stroke-linecap="round"/>
            </svg>
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                        font-size:18px;font-weight:700;color:#1A202C;">
                %{yuzde:.0f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Makro dagilimi
    p_yuzde = min(ozet["toplam_protein"] / 150 * 100, 100)
    k_yuzde = min(ozet["toplam_karb"] / 300 * 100, 100)
    y_yuzde = min(ozet["toplam_yag"] / 80 * 100, 100)

    st.markdown(f"""
    <div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;">
        <p style="font-size:14px;font-weight:600;color:#1A202C;margin:0 0 16px;">Makro Dağılımı</p>
        <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:13px;color:#64748B;font-weight:500;">Protein</span>
                <span style="font-size:13px;color:#DC2626;font-weight:600;">{ozet['toplam_protein']:.0f} g</span>
            </div>
            <div style="height:6px;background:#E5E7EB;border-radius:10px;overflow:hidden;">
                <div style="height:100%;width:{p_yuzde}%;background:#DC2626;border-radius:10px;"></div>
            </div>
        </div>
        <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:13px;color:#64748B;font-weight:500;">Karbonhidrat</span>
                <span style="font-size:13px;color:#D97706;font-weight:600;">{ozet['toplam_karb']:.0f} g</span>
            </div>
            <div style="height:6px;background:#E5E7EB;border-radius:10px;overflow:hidden;">
                <div style="height:100%;width:{k_yuzde}%;background:#D97706;border-radius:10px;"></div>
            </div>
        </div>
        <div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:13px;color:#64748B;font-weight:500;">Yağ</span>
                <span style="font-size:13px;color:#2563EB;font-weight:600;">{ozet['toplam_yag']:.0f} g</span>
            </div>
            <div style="height:6px;background:#E5E7EB;border-radius:10px;overflow:hidden;">
                <div style="height:100%;width:{y_yuzde}%;background:#2563EB;border-radius:10px;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Haftalik ozet bar chart
    haftalik = _haftalik_veri(aktif_kullanici)
    max_kalori = max([h["kalori"] for h in haftalik] + [hedef]) or 1

    bar_html_parcalari = []
    for h in haftalik:
        yukseklik_yuzde = max((h["kalori"] / max_kalori) * 100, 2) if h["kalori"] > 0 else 2
        renk = "#10B981" if h["bugun_mu"] else "#A7F3D0"
        kalori_yazi_opacity = 1 if h["kalori"] > 0 else 0
        bar_parca = (
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;'
            f'justify-content:flex-end;height:140px;">'
            f'<div style="font-size:11px;color:#1A202C;font-weight:600;margin-bottom:6px;'
            f'opacity:{kalori_yazi_opacity};">{h["kalori"]:.0f}</div>'
            f'<div style="width:60%;background:{renk};border-radius:6px 6px 0 0;'
            f'height:{yukseklik_yuzde}%;min-height:4px;"></div>'
            f'<div style="font-size:11px;color:#64748B;margin-top:8px;font-weight:500;">{h["gun"]}</div>'
            f'</div>'
        )
        bar_html_parcalari.append(bar_parca)

    bar_html = "".join(bar_html_parcalari)

    haftalik_html = (
        f'<div style="background:#F1F5F9;border:1px solid #A7F3D0;border-radius:14px;'
        f'padding:1.5rem;margin-bottom:1.5rem;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">'
        f'<p style="font-size:14px;font-weight:600;color:#1A202C;margin:0;">Haftalık Özet</p>'
        f'<p style="font-size:11px;color:#64748B;margin:0;">Son 7 gün</p>'
        f'</div>'
        f'<div style="display:flex;gap:8px;align-items:flex-end;padding:0 4px;">{bar_html}</div>'
        f'</div>'
    )

    st.markdown(haftalik_html, unsafe_allow_html=True)

    # Hizli erisim kartlari
    st.markdown("<p style='font-size:14px;font-weight:600;color:#1A202C;margin:1.5rem 0 0.8rem;'>Hızlı Erişim</p>", unsafe_allow_html=True)

    he1, he2 = st.columns(2)
    with he1:
        if st.button(
            "📸  Yemek Tara (AI)",
            use_container_width=True,
            key="dash_yemek_tara_btn",
            type="primary"
        ):
            st.session_state["aktif_sayfa"] = "Analiz"
            st.rerun()
    with he2:
        if st.button(
            "🥘  Tarif Önerisi",
            use_container_width=True,
            key="dash_tarif_btn"
        ):
            st.session_state["aktif_sayfa"] = "Tarif"
            st.rerun()