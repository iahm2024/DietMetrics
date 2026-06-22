import streamlit as st
import json
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Prompt Engineers - Calori AI",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stBaseButton-primary"] {
    background-color: #D4700A !important;
    border-color: #D4700A !important;
    color: #FFF8F0 !important;
    font-size: 16px !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stBaseButton-primary"]:hover {
    background-color: #A3520A !important;
}
.ust_bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 0 0.8rem 0;
}
.logo_alan {
    display: flex;
    align-items: center;
    gap: 12px;
}
.logo_daire {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #D4700A, #6C5CE7);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}
.logo_yazi {
    font-size: 22px;
    font-weight: 500;
    color: #FFF8F0;
    margin: 0;
}
.durum_pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #16213E;
    border: 0.5px solid #ffffff11;
    border-radius: 20px;
    padding: 7px 16px;
}
.durum_nokta {
    width: 8px;
    height: 8px;
    background: #4CAF50;
    border-radius: 50%;
}
.durum_yazi {
    font-size: 13px;
    color: #999;
    margin: 0;
}
.kart {
    background: #16213E;
    border: 0.5px solid #ffffff11;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.kart_baslik {
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 8px 0;
}
.makro_kart {
    background: #16213E;
    border: 0.5px solid #ffffff11;
    border-radius: 14px;
    padding: 1.5rem 1rem;
    text-align: center;
    margin-bottom: 1rem;
}
.makro_ad {
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 10px 0;
}
.makro_deger {
    font-size: 48px;
    font-weight: 500;
    margin: 0;
    line-height: 1;
}
.makro_birim {
    font-size: 13px;
    color: #555;
    margin: 6px 0 0 0;
}
.bos_alan {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    text-align: center;
}
.tespit_kart {
    background: #16213E;
    border: 0.5px solid #D4700A55;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.kalori_kart {
    background: linear-gradient(135deg, #1a1200, #2a1800);
    border: 0.5px solid #D4700A88;
    border-radius: 14px;
    padding: 2rem 1.5rem;
    margin-bottom: 1rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def veritabani_yukle():
    db_yolu = Path(__file__).parent.parent / "data" / "food_db.json"
    with open(db_yolu, "r", encoding="utf-8") as f:
        return json.load(f)

db = veritabani_yukle()

st.markdown("""
<div class="ust_bar">
    <div class="logo_alan">
        <div class="logo_daire">🍽</div>
        <div>
            <p class="logo_yazi">Prompt Engineers - Calori AI</p>
        </div>
    </div>
    <div class="durum_pill">
        <div class="durum_nokta"></div>
        <p class="durum_yazi">Sistem Hazır</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

sekme_analiz, sekme_chat, sekme_ayarlar = st.tabs(["📸  Analiz", "💬  Danışman", "⚙️  Ayarlar"])

with sekme_analiz:
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
            st.image(aktif_fotograf, width="stretch")
            st.markdown("---")

            yemek_secenekleri = {
                "Baklava": "baklava",
                "Lahmacun": "lahmacun",
                "Pirinç Pilavı": "pirinc_pilavi",
                "Kebap": "kebap",
            }
            secilen_yemek_label = st.selectbox(
                "Yemek Seç",
                options=list(yemek_secenekleri.keys()),
            )
            secilen_yemek = yemek_secenekleri[secilen_yemek_label]

            porsiyon_carpani = st.slider(
                "Porsiyon çarpanı",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1
            )
            analiz_baslat = st.button(
                "🔍  Analiz Et",
                type="primary",
                width="stretch"
            )
        else:
            analiz_baslat = False
            porsiyon_carpani = 1.0

    with sag:
        if aktif_fotograf and analiz_baslat:
            with st.spinner("Analiz ediliyor..."):
                time.sleep(0.8)

            tespit = secilen_yemek
            y = db["turkish_classes"][tespit]
            gram = y["avg_portion_g"] * porsiyon_carpani
            kalori = (y["calories_per_100g"] * gram) / 100
            protein = (y["protein_per_100g"] * gram) / 100
            yag = (y["fat_per_100g"] * gram) / 100
            karb = (y["carbs_per_100g"] * gram) / 100

            st.markdown(f"""
            <div class="tespit_kart">
                <div>
                    <p class="kart_baslik">Tespit Edilen Yemek</p>
                    <p style="font-size:28px;font-weight:500;color:#FFF8F0;margin:0;">
                        {y['display_name']}
                    </p>
                    <p style="font-size:13px;color:#888;margin:6px 0 0;">
                        {y['meal_type']} · ~{gram:.0f} g
                    </p>
                </div>
                <div style="font-size:48px;">🍽️</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="kalori_kart">
                <p class="kart_baslik">Toplam Kalori</p>
                <p style="font-size:64px;font-weight:500;color:#D4700A;margin:0;line-height:1;">
                    {kalori:.0f}
                </p>
                <p style="font-size:16px;color:#888;margin:8px 0 0;">kcal</p>
            </div>
            """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            makrolar = [
                (m1, "Protein", protein, "g", "#6C5CE7"),
                (m2, "Yağ", yag, "g", "#D4700A"),
                (m3, "Karbonhidrat", karb, "g", "#F5A84B"),
            ]
            for col, ad, deger, birim, renk in makrolar:
                with col:
                    st.markdown(f"""
                    <div class="makro_kart">
                        <p class="makro_ad">{ad}</p>
                        <p class="makro_deger" style="color:{renk};font-size:48px;">
                            {deger:.1f}
                        </p>
                        <p class="makro_birim">{birim}</p>
                    </div>
                    """, unsafe_allow_html=True)

            toplam = protein + yag + karb
            if toplam > 0:
                with st.container(border=True):
                    st.markdown("**Makro Dağılım**")
                    st.progress(protein / toplam,
                        text=f"Protein — {protein:.1f}g  (%{protein/toplam*100:.0f})")
                    st.progress(yag / toplam,
                        text=f"Yağ — {yag:.1f}g  (%{yag/toplam*100:.0f})")
                    st.progress(karb / toplam,
                        text=f"Karbonhidrat — {karb:.1f}g  (%{karb/toplam*100:.0f})")

            if y["glycemic_warning"]:
                st.warning(
                    f"⚠️ Yüksek glisemik indeks ({y['glycemic_index']})."
                    f" Yemekten sonra 15 dakika yürüyüş önerilir."
                )

            st.markdown(f"""
            <div class="kart">
                <p class="kart_baslik">Malzemeler</p>
                <p style="color:#ccc;font-size:15px;margin:8px 0 0;line-height:1.8;">
                    {'  ·  '.join(y['ingredients'])}
                </p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="bos_alan">
                <p style="font-size:64px;margin:0;">🍽️</p>
                <p style="color:#D4700A;font-size:18px;font-weight:500;margin:16px 0 6px;">
                    Fotoğraf yükle ve analiz et
                </p>
                <p style="color:#444;font-size:14px;margin:0;">
                    Sonuçlar burada görünecek
                </p>
            </div>
            """, unsafe_allow_html=True)

with sekme_chat:
    if "mesajlar" not in st.session_state:
        st.session_state.mesajlar = [
            {"rol": "asistan",
             "icerik": "Merhaba! Beslenme konusunda sana yardımcı olabilirim."}
        ]

    for mesaj in st.session_state.mesajlar:
        with st.chat_message(
            "user" if mesaj["rol"] == "kullanici" else "assistant"
        ):
            st.write(mesaj["icerik"])

    kullanici_mesaji = st.chat_input("Mesajını yaz...")
    if kullanici_mesaji:
        st.session_state.mesajlar.append(
            {"rol": "kullanici", "icerik": kullanici_mesaji})
        st.session_state.mesajlar.append(
            {"rol": "asistan", "icerik": "Ollama henüz bağlı değil."})
        st.rerun()

with sekme_ayarlar:
    st.markdown('<div class="kart">', unsafe_allow_html=True)
    st.markdown("**Referans Nesne**")
    st.radio(
        "ref",
        ["Çatal (20 cm)", "Kaşık (17 cm)", "Tabak şablonu (26 cm)"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown("**Model Durumu**")
    st.caption("🔴  YOLOv8s — yüklenmedi")
    st.caption("🔴  Depth-Anything-V2 — yüklenmedi")
    st.caption("🔴  Qwen2.5-3B — Ollama bekleniyor")
    st.markdown('</div>', unsafe_allow_html=True)