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
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.2rem 0 0.8rem 0;
}
.logo_alan { display: flex; align-items: center; gap: 12px; }
.logo_daire {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #D4700A, #6C5CE7);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
}
.logo_yazi { font-size: 22px; font-weight: 500; color: #FFF8F0; margin: 0; }
.durum_pill {
    display: flex; align-items: center; gap: 8px;
    background: #16213E; border: 0.5px solid #ffffff11;
    border-radius: 20px; padding: 7px 16px;
}
.durum_nokta { width: 8px; height: 8px; background: #4CAF50; border-radius: 50%; }
.durum_yazi { font-size: 13px; color: #999; margin: 0; }
.kart {
    background: #16213E; border: 0.5px solid #ffffff11;
    border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem;
}
.kart_baslik {
    font-size: 11px; color: #666;
    text-transform: uppercase; letter-spacing: 1px;
    margin: 0 0 8px 0;
}
.makro_kart {
    background: #16213E; border: 0.5px solid #ffffff11;
    border-radius: 14px; padding: 1.5rem 1rem;
    text-align: center; margin-bottom: 1rem;
}
.makro_ad {
    font-size: 11px; color: #666;
    text-transform: uppercase; letter-spacing: 1px;
    margin: 0 0 10px 0;
}
.makro_deger { font-size: 48px; font-weight: 500; margin: 0; line-height: 1; }
.makro_birim { font-size: 13px; color: #555; margin: 6px 0 0 0; }
.bos_alan {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 400px; text-align: center;
}
.tespit_kart {
    background: #16213E; border: 0.5px solid #D4700A55;
    border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem;
    display: flex; align-items: center; justify-content: space-between;
}
.kalori_kart {
    background: linear-gradient(135deg, #1a1200, #2a1800);
    border: 0.5px solid #D4700A88;
    border-radius: 14px; padding: 2rem 1.5rem;
    margin-bottom: 1rem; text-align: center;
}
</style>
""", unsafe_allow_html=True)
 
@st.cache_data
def veritabani_yukle():
    db_yolu = Path(__file__).parent.parent / "data" / "food_db.json"
    with open(db_yolu, "r", encoding="utf-8") as f:
        return json.load(f)
 
db = veritabani_yukle()
 
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
        <div class="logo_daire">🍽</div>
        <div><p class="logo_yazi">Prompt Engineers - Calori AI</p></div>
    </div>
    <div class="durum_pill">
        <div class="durum_nokta"></div>
        <p class="durum_yazi">Sistem Hazır</p>
    </div>
</div>
""", unsafe_allow_html=True)
 
st.divider()
 
sekme_analiz, sekme_chat, sekme_ayarlar = st.tabs(["📸  Analiz", "💬  Danışman", "⚙️  Ayarlar"])
 
def makro_panel_ciz(y, gram, kalori, protein, yag, karb, adet=1):
    birim = y.get("porsiyon_birimi", "porsiyon")
    adet_yazi = f" × {adet} {birim}" if adet > 1 else ""
 
    st.markdown(f"""
    <div class="tespit_kart">
        <div>
            <p class="kart_baslik">Tespit Edilen Yemek</p>
            <p style="font-size:28px;font-weight:500;color:#FFF8F0;margin:0;">
                {y['display_name']}{adet_yazi}
            </p>
            <p style="font-size:13px;color:#888;margin:6px 0 0;">
                {y['meal_type']} · ~{gram:.0f} g toplam
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
    for col, ad, deger, birim2, renk in makrolar:
        with col:
            st.markdown(f"""
            <div class="makro_kart">
                <p class="makro_ad">{ad}</p>
                <p class="makro_deger" style="color:{renk};font-size:48px;">{deger:.1f}</p>
                <p class="makro_birim">{birim2}</p>
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
            pil_img = Image.open(aktif_fotograf).convert("RGB")
            st.markdown("---")
 
            analiz_baslat = st.button(
                "🔍  Analiz Et",
                type="primary",
                width="stretch"
            )
            secilen_yemek = "baklava"  # default fallback, manuel duzeltmede degistirilebilir
        else:
            analiz_baslat = False
            pil_img = None
            secilen_yemek = "baklava"
 
    with sag:
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
                    st.success(f"✅ Otomatik tespit: {otomatik_tespit} ({kullanilan_model}, conf %{analiz['otomatik_confidence']*100:.0f})")
                else:
                    otomatik_tespit = secilen_yemek
                    st.info("ℹ️ Otomatik tespit güvenilir değil, seçilen yemek kullanildi.")
 
            # Manuel yemek varsa kullan, yoksa otomatik
            tespit = st.session_state.get("manuel_yemek", otomatik_tespit)
 
            if maskeler is not None and len(maskeler) > 0:
                from app.seg_gorsel import maskeli_goruntu_olustur
                custom_tespitler = [t for t in tespitler if t.get("kaynak") == "custom"]
                maskeli_img = maskeli_goruntu_olustur(pil_img, maskeler, custom_tespitler)
                st.image(maskeli_img, width="stretch")
            else:
                st.image(pil_img, width="stretch")
 
            y = db["turkish_classes"][tespit]
            referans = analiz.get("referans")
 
            # Adet sayisi (tespit edilenlerle ayni siniftan)
            ayni_sinif_sayisi = len([
                t for t in tespitler
                if t.get("kaynak") == "custom" and t.get("sinif") == otomatik_tespit
            ])
            if ayni_sinif_sayisi == 0:
                ayni_sinif_sayisi = 1
 
            # Otomatik gramaj hesabi
            if referans:
                from app.heuristic_engine import gramaj_hesapla
                goruntu_genisligi = pil_img.width
                gram_tek = gramaj_hesapla(
                    tespit, 1.0, referans, goruntu_genisligi, db
                )
                otomatik_gram = gram_tek * ayni_sinif_sayisi
                st.caption(f"📏 Referans: {referans['sinif']} (%{referans['confidence']*100:.0f}) | Tespit: {ayni_sinif_sayisi} adet")
            else:
                otomatik_gram = y["avg_portion_g"] * ayni_sinif_sayisi
                st.caption(f"📏 Referans nesne yok | Tespit: {ayni_sinif_sayisi} adet × ortalama porsiyon")
 
            if tespitler:
                tespit_metni = ", ".join([
                    f"{t['sinif']} (%{t['confidence']*100:.0f})"
                    for t in tespitler[:6]
                ])
                st.info(f"🔍 Görüntüde tespit edilenler: {tespit_metni}")
 
            # Foto degisirse manuel ayar sifirla
            foto_id = f"{aktif_fotograf.name}_{otomatik_tespit}_{ayni_sinif_sayisi}"
            if st.session_state.get("son_foto_id") != foto_id:
                st.session_state["son_foto_id"] = foto_id
                st.session_state["manuel_gram"] = float(otomatik_gram)
                st.session_state["manuel_carpan"] = 1.0
                st.session_state.pop("manuel_yemek", None)
 
            # Final gramaj
            final_gram = st.session_state.get("manuel_gram", otomatik_gram) * st.session_state.get("manuel_carpan", 1.0)
 
            kalori = (y["calories_per_100g"] * final_gram) / 100
            protein = (y["protein_per_100g"] * final_gram) / 100
            yag = (y["fat_per_100g"] * final_gram) / 100
            karb = (y["carbs_per_100g"] * final_gram) / 100
 
            makro_panel_ciz(y, final_gram, kalori, protein, yag, karb, ayni_sinif_sayisi)
 
            # Manuel duzeltme
            with st.expander("Sonuç doğru mu? Manuel düzeltme", expanded=False):
                st.caption("Otomatik tespit hatalı olabilir. Yemeği, gramajı veya porsiyonu düzeltebilirsin.")
 
                mevcut_label = YEMEK_TERS.get(tespit, "Baklava")
                yeni_yemek_label = st.selectbox(
                    "Yemek (yanlış tespit edildiyse değiştir)",
                    options=list(YEMEK_SECENEKLERI.keys()),
                    index=list(YEMEK_SECENEKLERI.keys()).index(mevcut_label),
                    key="manuel_yemek_input"
                )
                yeni_yemek = YEMEK_SECENEKLERI[yeni_yemek_label]
 
                d1, d2 = st.columns(2)
                with d1:
                    yeni_gram = st.number_input(
                        "Gramaj (g)",
                        min_value=10.0,
                        max_value=2000.0,
                        value=float(st.session_state.get("manuel_gram", otomatik_gram)),
                        step=10.0,
                        key="manuel_gram_input"
                    )
                with d2:
                    yeni_carpan = st.slider(
                        "Porsiyon çarpanı",
                        min_value=0.5,
                        max_value=2.0,
                        value=float(st.session_state.get("manuel_carpan", 1.0)),
                        step=0.1,
                        key="manuel_carpan_input"
                    )
 
                btn_sol, btn_sag = st.columns(2)
                with btn_sol:
                    if st.button("Yeniden Hesapla", type="primary", use_container_width=True, key="yeniden_hesapla"):
                        st.session_state["manuel_gram"] = yeni_gram
                        st.session_state["manuel_carpan"] = yeni_carpan
                        st.session_state["manuel_yemek"] = yeni_yemek
                        st.rerun()
                with btn_sag:
                    if st.button("Otomatiğe Don", use_container_width=True, key="otomatige_don"):
                        st.session_state["manuel_gram"] = float(otomatik_gram)
                        st.session_state["manuel_carpan"] = 1.0
                        st.session_state.pop("manuel_yemek", None)
                        st.rerun()
 
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
 
            try:
                import joblib
                mlp_model_path = Path(__file__).parent.parent / "models" / "mlp_action.pkl"
                scaler_path = Path(__file__).parent.parent / "models" / "mlp_scaler.pkl"
                if mlp_model_path.exists() and scaler_path.exists():
                    mlp_model = joblib.load(mlp_model_path)
                    scaler = joblib.load(scaler_path)
 
                    girdi = scaler.transform([[kalori, karb, y["glycemic_index"]]])
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
                        <p style="font-size:18px;font-weight:500;color:#D4700A;margin:0;">{baslik}</p>
                        <p style="color:#ccc;font-size:14px;margin:8px 0 0;">{aciklama}</p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception:
                pass
 
            st.session_state["son_analiz"] = {
                "yemek": y["display_name"],
                "gram": final_gram,
                "kalori": kalori,
                "protein": protein,
                "yag": yag,
                "karb": karb,
                "adet": ayni_sinif_sayisi,
            }
 
        elif aktif_fotograf and not analiz_baslat:
            st.image(pil_img, width="stretch")
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
            cevap = mesaj_gonder(
                kullanici_mesaji,
                sohbet_gecmisi=st.session_state.mesajlar,
                yemek_bilgisi=st.session_state.get("son_analiz")
            )
 
        st.session_state.mesajlar.append({"rol": "asistan", "icerik": cevap})
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
    custom_model_var = (Path(__file__).parent.parent / "models" / "yolo11m_food.pt").exists()
    mlp_var = (Path(__file__).parent.parent / "models" / "mlp_action.pkl").exists()
    st.caption(f"{'🟢' if custom_model_var else '🔴'}  YOLO11m-seg (Custom Türk yemekleri)")
    st.caption("🟢  YOLOv8n (COCO Fallback)")
    st.caption(f"{'🟢' if mlp_var else '🔴'}  MLP Karar Ağı")
    st.caption("⚪  Depth-Anything-V2 (planli)")
    st.caption("🟢  Qwen2.5-7B (Ollama)")
    st.markdown('</div>', unsafe_allow_html=True)