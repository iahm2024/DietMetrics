import streamlit as st
from pathlib import Path
from PIL import Image


YEMEK_SECENEKLERI = {
    "Baklava": "baklava",
    "Lahmacun": "lahmacun",
    "Pirinç Pilavı": "pirinc_pilavi",
    "Şiş Kebap": "kebap",
}
YEMEK_TERS = {v: k for k, v in YEMEK_SECENEKLERI.items()}


@st.cache_resource
def mlp_yukle():
    # MLP ve scaler'i bir kere yükle, sonra cacheden dön
    import joblib
    mlp_path = Path(__file__).parent.parent / "models" / "mlp_action.pkl"
    scaler_path = Path(__file__).parent.parent / "models" / "mlp_scaler.pkl"
    if mlp_path.exists() and scaler_path.exists():
        return joblib.load(mlp_path), joblib.load(scaler_path)
    return None, None


def analiz_sayfa_goster(aktif_kullanici, db):
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

            # Foto değişirse analiz state'ini sıfırla
            yeni_foto_kimlik = f"{aktif_fotograf.name}_{aktif_fotograf.size if hasattr(aktif_fotograf, 'size') else id(aktif_fotograf)}"
            if st.session_state.get("yuklu_foto_kimlik") != yeni_foto_kimlik:
                st.session_state["yuklu_foto_kimlik"] = yeni_foto_kimlik
                st.session_state["analiz_tamamlandi"] = False
                st.session_state.pop("analiz_sonucu", None)
                st.session_state.pop("manuel_gram", None)
                st.session_state.pop("manuel_carpan", None)
                st.session_state.pop("manuel_yemek", None)
                st.session_state.pop("ek_kalemler_listesi", None)
                st.session_state.pop("yemek_gramlari", None)
                st.session_state.pop("son_analiz_coklu", None)

            st.markdown("---")

            analiz_baslat = st.button(
                "🔍  Analiz Et",
                type="primary",
                width="stretch"
            )
            secilen_yemek = "baklava"
        else:
            analiz_baslat = False
            pil_img = None
            secilen_yemek = "baklava"
            st.session_state["analiz_tamamlandi"] = False
            st.session_state.pop("analiz_sonucu", None)
            st.session_state.pop("ek_kalemler_listesi", None)
            st.session_state.pop("yemek_gramlari", None)
            st.session_state.pop("son_analiz_coklu", None)
 
    with sag:
        # Analiz tetiklenirse - hesapla ve state'e kaydet
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
                    tespit_mesaji = ("success", f"✅ Otomatik tespit: {otomatik_tespit} ({kullanilan_model}, conf %{analiz['otomatik_confidence']*100:.0f})")
                else:
                    otomatik_tespit = secilen_yemek
                    tespit_mesaji = ("info", "ℹ️ Otomatik tespit güvenilir değil, seçilen yemek kullanildi.")

                # State'e tüm analiz verilerini kaydet
                st.session_state["analiz_sonucu"] = {
                    "pil_img": pil_img,
                    "tespitler": tespitler,
                    "maskeler": maskeler,
                    "otomatik_tespit": otomatik_tespit,
                    "tespit_mesaji": tespit_mesaji,
                    "referans": analiz.get("referans"),
                    "goruntu_genisligi": pil_img.width,
                    "foto_ad": aktif_fotograf.name,
                }

                # Foto değişirse manuel ayar sıfırla
                foto_id = f"{aktif_fotograf.name}_{otomatik_tespit}"
                if st.session_state.get("son_foto_id") != foto_id:
                    st.session_state["son_foto_id"] = foto_id
                    st.session_state.pop("manuel_gram", None)
                    st.session_state.pop("manuel_carpan", None)
                    st.session_state.pop("manuel_yemek", None)

        # Analiz sonucu state'te varsa göster
        if st.session_state.get("analiz_sonucu"):
            sonuc = st.session_state["analiz_sonucu"]
            pil_img_son = sonuc["pil_img"]
            tespitler = sonuc["tespitler"]
            maskeler = sonuc["maskeler"]
            otomatik_tespit = sonuc["otomatik_tespit"]
            referans = sonuc["referans"]

            # Maskeli görüntü
            if maskeler is not None and len(maskeler) > 0:
                from app.seg_gorsel import maskeli_goruntu_olustur
                custom_tespitler = [t for t in tespitler if t.get("kaynak") == "custom"]
                maskeli_img = maskeli_goruntu_olustur(pil_img_son, maskeler, custom_tespitler)
                st.image(maskeli_img, width="stretch")
            else:
                st.image(pil_img_son, width="stretch")

            # ÇOKLU YEMEK MANTIĞI - Custom tespitleri sinifa gore grupla
            custom_tespitler = [t for t in tespitler if t.get("kaynak") == "custom"]

            # Eger hic custom tespit yoksa gostermek icin bir sey yok
            if not custom_tespitler:
                tespit_gruplari = {}
            else:
                tespit_gruplari = {}
                for t in custom_tespitler:
                    sinif = t["sinif"]
                    tespit_gruplari[sinif] = tespit_gruplari.get(sinif, 0) + 1

            # Referans nesne bilgisi
            if referans:
                st.caption(f"📏 Referans: {referans['sinif']} (%{referans['confidence']*100:.0f})")
            else:
                st.caption("📏 Referans nesne yok · ortalama porsiyon kullanildi")

            # Her sınıf için gramaj + kalori hesabı
            from app.heuristic_engine import gramaj_hesapla

            # Manuel düzeltmeler session'da tutulur
            if "yemek_gramlari" not in st.session_state:
                st.session_state["yemek_gramlari"] = {}

            yemek_detaylari = []

            for sinif, adet in tespit_gruplari.items():
                if sinif not in db["turkish_classes"]:
                    continue

                y = db["turkish_classes"][sinif]

                # Otomatik gramaj
                if referans:
                    gram_tek = gramaj_hesapla(sinif, 1.0, referans, pil_img_son.width, db)
                    otomatik_gram = gram_tek * adet
                else:
                    otomatik_gram = y["avg_portion_g"] * adet

                # Manuel düzeltilmiş gram varsa onu kullan
                final_gram = st.session_state["yemek_gramlari"].get(sinif, otomatik_gram)

                kal = (y["calories_per_100g"] * final_gram) / 100
                pro = (y["protein_per_100g"] * final_gram) / 100
                yg = (y["fat_per_100g"] * final_gram) / 100
                kb = (y["carbs_per_100g"] * final_gram) / 100

                yemek_detaylari.append({
                    "sinif": sinif,
                    "display_name": y["display_name"],
                    "adet": adet,
                    "birim": y.get("porsiyon_birimi", "porsiyon"),
                    "gram": final_gram,
                    "otomatik_gram": otomatik_gram,
                    "kalori": kal,
                    "protein": pro,
                    "yag": yg,
                    "karb": kb,
                    "gi": y["glycemic_index"],
                })

            # Ek kalemleri ekle (manuel girilenler)
            ek_kalemler = st.session_state.get("ek_kalemler_listesi", [])

            # Birleşik Panel
            toplam_kalori = sum(y["kalori"] for y in yemek_detaylari) + sum(e["kalori"] for e in ek_kalemler)
            toplam_protein = sum(y["protein"] for y in yemek_detaylari) + sum(e["protein"] for e in ek_kalemler)
            toplam_yag = sum(y["yag"] for y in yemek_detaylari) + sum(e["yag"] for e in ek_kalemler)
            toplam_karb = sum(y["karb"] for y in yemek_detaylari) + sum(e["karb"] for e in ek_kalemler)
            toplam_gram = sum(y["gram"] for y in yemek_detaylari) + sum(e["gram"] for e in ek_kalemler)

            # Tespit edilen yemekler
            with st.container(border=True):
                st.markdown('<p class="kart_baslik">Tabaktaki Yemekler</p>', unsafe_allow_html=True)

                if not yemek_detaylari and not ek_kalemler:
                    st.markdown(
                        "<p style='color:#64748B;text-align:center;padding:1rem;'>"
                        "Tabakta tanınan yemek yok. Aşağıdan manuel ekleyebilirsin.</p>",
                        unsafe_allow_html=True
                    )
                else:
                    for yd in yemek_detaylari:
                        adet_txt = f" × {yd['adet']} {yd['birim']}" if yd['adet'] > 1 else ""
                        sat_c1, sat_c2 = st.columns([4, 1])
                        with sat_c1:
                            st.markdown(
                                f"<p style='font-size:16px;color:#1A202C;margin:0;font-weight:500;'>"
                                f"{yd['display_name']}{adet_txt}</p>"
                                f"<p style='font-size:12px;color:#64748B;margin:2px 0 8px;'>"
                                f"{yd['gram']:.0f} g</p>",
                                unsafe_allow_html=True
                            )
                        with sat_c2:
                            st.markdown(
                                f"<p style='font-size:18px;color:#DD5A43;margin:0;font-weight:500;text-align:right;'>"
                                f"{yd['kalori']:.0f}<span style='font-size:11px;color:#64748B;'> kcal</span></p>",
                                unsafe_allow_html=True
                            )

                    for ek in ek_kalemler:
                        sat_c1, sat_c2 = st.columns([4, 1])
                        with sat_c1:
                            st.markdown(
                                f"<p style='font-size:16px;color:#1A202C;margin:0;font-weight:500;'>"
                                f"+ {ek['display_name']}</p>"
                                f"<p style='font-size:12px;color:#64748B;margin:2px 0 8px;'>"
                                f"{ek['gram']:.0f} g · manuel ek</p>",
                                unsafe_allow_html=True
                            )
                        with sat_c2:
                            st.markdown(
                                f"<p style='font-size:18px;color:#2563EB;margin:0;font-weight:500;text-align:right;'>"
                                f"{ek['kalori']:.0f}<span style='font-size:11px;color:#64748B;'> kcal</span></p>",
                                unsafe_allow_html=True
                            )

            # Toplam kalori kartı
            st.markdown(f"""
            <div class="kalori_kart">
                <p class="kart_baslik">Toplam Tabak Kalorisi</p>
                <p style="font-size:64px;font-weight:500;color:#DD5A43;margin:0;line-height:1;">
                    {toplam_kalori:.0f}
                </p>
                <p style="font-size:16px;color:#64748B;margin:8px 0 0;">kcal · {toplam_gram:.0f} g toplam</p>
            </div>
            """, unsafe_allow_html=True)

            # Makro kartları
            m1, m2, m3 = st.columns(3)
            for col, ad, deger, renk in [
                (m1, "Protein", toplam_protein, "#2563EB"),
                (m2, "Yağ", toplam_yag, "#DD5A43"),
                (m3, "Karbonhidrat", toplam_karb, "#D97706"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="makro_kart">
                        <p class="makro_ad">{ad}</p>
                        <p class="makro_deger" style="color:{renk};font-size:48px;">{deger:.1f}</p>
                        <p class="makro_birim">g</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Makro ddağılım çubukları
            makro_toplam = toplam_protein + toplam_yag + toplam_karb
            if makro_toplam > 0:
                with st.container(border=True):
                    st.markdown("**Makro Dağılım**")
                    st.progress(toplam_protein / makro_toplam,
                        text=f"Protein — {toplam_protein:.1f}g  (%{toplam_protein/makro_toplam*100:.0f})")
                    st.progress(toplam_yag / makro_toplam,
                        text=f"Yağ — {toplam_yag:.1f}g  (%{toplam_yag/makro_toplam*100:.0f})")
                    st.progress(toplam_karb / makro_toplam,
                        text=f"Karbonhidrat — {toplam_karb:.1f}g  (%{toplam_karb/makro_toplam*100:.0f})")

            # Manuel Düzeltme
            with st.expander("Sonuç doğru mu? Manuel düzeltme", expanded=False):
                st.caption("Tespit edilen bir yemeğin gramajını düzeltebilirsin.")

                if yemek_detaylari:
                    duz_yemek_secenekleri = {yd["display_name"]: yd["sinif"] for yd in yemek_detaylari}
                    secilen_label = st.selectbox(
                        "Düzeltmek istediğin yemek",
                        options=list(duz_yemek_secenekleri.keys()),
                        key="duzeltme_yemek_secimi"
                    )
                    secilen_sinif = duz_yemek_secenekleri[secilen_label]
                    mevcut_yd = next(yd for yd in yemek_detaylari if yd["sinif"] == secilen_sinif)

                    yeni_gram = st.number_input(
                        f"{mevcut_yd['display_name']} için gramaj (g)",
                        min_value=10.0,
                        max_value=2000.0,
                        value=float(mevcut_yd["gram"]),
                        step=10.0,
                        key=f"duz_gram_{secilen_sinif}"
                    )

                    dk1, dk2 = st.columns(2)
                    with dk1:
                        if st.button("Yeniden Hesapla", type="primary", use_container_width=True, key="duz_kaydet"):
                            st.session_state["yemek_gramlari"][secilen_sinif] = yeni_gram
                            st.rerun()
                    with dk2:
                        if st.button("Bu Yemeği Otomatiğe Don", use_container_width=True, key="duz_sifirla"):
                            st.session_state["yemek_gramlari"].pop(secilen_sinif, None)
                            st.rerun()
                else:
                    st.caption("Düzeltilebilecek otomatik tespit yok.")

            # Manuel Yemek Ekleme
            with st.expander("➕ Tabakta tanınmayan bir şey var mı? Ekle", expanded=False):
                st.caption(
                    "Sistemimiz şu an 4 yemek tipini tanıyor (baklava, lahmacun, pilav, kebap). "
                    "Tabağındaki diğer kalemleri buradan ekleyebilirsin."
                )

                EK_KATEGORI_TR = {
                    "salata": "🥗 Salatalar",
                    "icecek": "🥤 İçecekler",
                    "ekmek": "🍞 Ekmek/Lavaş",
                    "yan_yemek": "🍚 Yan Yemekler",
                    "tatli": "🍰 Tatlılar",
                    "atistirmalik": "🧀 Atıştırmalık",
                    "meyve": "🍎 Meyveler",
                }

                ek_kalemler_db = db.get("ek_kalemler", {})

                # Dropdown Seçenekleri
                dropdown_options = ["-- Listeden seç --"]
                option_keys = [None]
                for kat_key, kat_label in EK_KATEGORI_TR.items():
                    for ek_key, ek_val in ek_kalemler_db.items():
                        if ek_val.get("kategori") == kat_key:
                            dropdown_options.append(f"{kat_label.split()[0]} {ek_val['display_name']}")
                            option_keys.append(ek_key)
                dropdown_options.append("✏️ Listede yok, manuel gir")
                option_keys.append("__manuel__")

                secilen_idx = st.selectbox(
                    "Ne eklemek istiyorsun?",
                    options=range(len(dropdown_options)),
                    format_func=lambda i: dropdown_options[i],
                    key="ek_kalem_secim"
                )
                secilen_ek_key = option_keys[secilen_idx]

                if secilen_ek_key is None:
                    pass
                elif secilen_ek_key == "__manuel__":
                    # Manuel giriş formu
                    me_ad = st.text_input("Yemek/içecek adı", key="me_ad")
                    me_gram = st.number_input("Gramaj (g)", min_value=1.0, max_value=2000.0, value=100.0, step=10.0, key="me_gram")

                    me_c1, me_c2 = st.columns(2)
                    with me_c1:
                        me_kal_100 = st.number_input("Kalori (kcal/100g)", min_value=0.0, max_value=900.0, value=100.0, step=10.0, key="me_kal")
                    with me_c2:
                        me_pro_100 = st.number_input("Protein (g/100g)", min_value=0.0, max_value=100.0, value=2.0, step=0.5, key="me_pro")

                    me_c3, me_c4 = st.columns(2)
                    with me_c3:
                        me_yag_100 = st.number_input("Yağ (g/100g)", min_value=0.0, max_value=100.0, value=3.0, step=0.5, key="me_yag")
                    with me_c4:
                        me_karb_100 = st.number_input("Karbonhidrat (g/100g)", min_value=0.0, max_value=100.0, value=15.0, step=0.5, key="me_karb")

                    if st.button("➕ Manuel Kalemi Ekle", type="primary", use_container_width=True, key="me_ekle_btn"):
                        if me_ad.strip():
                            ek_yeni = {
                                "sinif_key": f"manuel_{len(ek_kalemler)}",
                                "display_name": me_ad.strip(),
                                "gram": me_gram,
                                "kalori": (me_kal_100 * me_gram) / 100,
                                "protein": (me_pro_100 * me_gram) / 100,
                                "yag": (me_yag_100 * me_gram) / 100,
                                "karb": (me_karb_100 * me_gram) / 100,
                                "gi": 0,
                                "manuel": True,
                            }
                            st.session_state.setdefault("ek_kalemler_listesi", []).append(ek_yeni)
                            st.rerun()
                else:
                    # Veritabanından seçildi
                    ek_data = ek_kalemler_db[secilen_ek_key]
                    ek_gram = st.number_input(
                        f"{ek_data['display_name']} için gramaj (g)",
                        min_value=1.0,
                        max_value=2000.0,
                        value=100.0,
                        step=10.0,
                        key=f"ek_gram_{secilen_ek_key}"
                    )

                    onizleme_kal = (ek_data["calories_per_100g"] * ek_gram) / 100
                    st.caption(f"Önizleme: ~{onizleme_kal:.0f} kcal")

                    if st.button("➕ Ekle", type="primary", use_container_width=True, key=f"ek_ekle_{secilen_ek_key}"):
                        ek_yeni = {
                            "sinif_key": secilen_ek_key,
                            "display_name": ek_data["display_name"],
                            "gram": ek_gram,
                            "kalori": (ek_data["calories_per_100g"] * ek_gram) / 100,
                            "protein": (ek_data["protein_per_100g"] * ek_gram) / 100,
                            "yag": (ek_data["fat_per_100g"] * ek_gram) / 100,
                            "karb": (ek_data["carbs_per_100g"] * ek_gram) / 100,
                            "gi": 0,
                            "manuel": False,
                        }
                        st.session_state.setdefault("ek_kalemler_listesi", []).append(ek_yeni)
                        st.rerun()

                # Eklenmiş ek kalemleri listele
                if ek_kalemler:
                    st.markdown("---")
                    st.caption("**Bu öğüne manuel eklenenler:**")
                    for ix, ek in enumerate(ek_kalemler):
                        ek_c1, ek_c2 = st.columns([5, 1])
                        with ek_c1:
                            st.markdown(f"• {ek['display_name']} ({ek['gram']:.0f}g) — {ek['kalori']:.0f} kcal")
                        with ek_c2:
                            if st.button("✕", key=f"ek_sil_{ix}"):
                                ek_kalemler.pop(ix)
                                st.session_state["ek_kalemler_listesi"] = ek_kalemler
                                st.rerun()

            # Glisemik Profil
            from app.heuristic_engine import glisemik_yuk_hesapla, glisemik_yuk_siniflandir

            # Ağırlıklı ortalama GI hesabı
            karb_li_yemekler = [yd for yd in yemek_detaylari if yd["karb"] > 0]
            toplam_karb_agirlik = sum(yd["karb"] for yd in karb_li_yemekler)

            if toplam_karb_agirlik > 0:
                agirlikli_gi = sum(yd["gi"] * yd["karb"] for yd in karb_li_yemekler) / toplam_karb_agirlik
            else:
                agirlikli_gi = 0

            gl_deger = glisemik_yuk_hesapla(agirlikli_gi, toplam_karb)
            gl_sinif = glisemik_yuk_siniflandir(gl_deger)

            if agirlikli_gi == 0:
                gi_renk = "#888888"
                gi_etiket = "Yok"
            elif agirlikli_gi <= 55:
                gi_renk = "#059669"
                gi_etiket = "Düşük"
            elif agirlikli_gi <= 69:
                gi_renk = "#DD5A43"
                gi_etiket = "Orta"
            else:
                gi_renk = "#DC2626"
                gi_etiket = "Yüksek"

            st.markdown(f"""
            <div class="kart">
                <p class="kart_baslik">Glisemik Profil (Tabak Ortalaması)</p>
                <div style="display:flex;gap:1rem;margin-top:8px;">
                    <div style="flex:1;background:#F8FAFC;border-radius:10px;padding:1rem;border-left:3px solid {gi_renk};">
                        <p style="font-size:11px;color:#64748B;margin:0 0 4px;text-transform:uppercase;letter-spacing:1px;">Ağırlıklı GI</p>
                        <p style="font-size:28px;font-weight:500;color:{gi_renk};margin:0;line-height:1;">{agirlikli_gi:.0f}</p>
                        <p style="font-size:12px;color:#64748B;margin:6px 0 0;">{gi_etiket} · karb ağırlıklı</p>
                    </div>
                    <div style="flex:1;background:#F8FAFC;border-radius:10px;padding:1rem;border-left:3px solid {gl_sinif['renk']};">
                        <p style="font-size:11px;color:#64748B;margin:0 0 4px;text-transform:uppercase;letter-spacing:1px;">Glisemik Yük</p>
                        <p style="font-size:28px;font-weight:500;color:{gl_sinif['renk']};margin:0;line-height:1;">{gl_deger:.1f}</p>
                        <p style="font-size:12px;color:#64748B;margin:6px 0 0;">{gl_sinif['etiket']} · toplam etki</p>
                    </div>
                </div>
                <p style="font-size:13px;color:#64748B;margin:12px 0 0;font-style:italic;">
                    {gl_sinif['aciklama']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # MALZEMELER
            if yemek_detaylari:
                tum_malzemeler = []
                for yd in yemek_detaylari:
                    y_db = db["turkish_classes"][yd["sinif"]]
                    tum_malzemeler.extend(y_db["ingredients"])
                tum_malzemeler = list(dict.fromkeys(tum_malzemeler))

                st.markdown(f"""
                <div class="kart">
                    <p class="kart_baslik">Malzemeler</p>
                    <p style="color:#475569;font-size:15px;margin:8px 0 0;line-height:1.8;">
                        {'  ·  '.join(tum_malzemeler)}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # MLP KARAR AĞI
            try:
                mlp_model, scaler = mlp_yukle()
                if mlp_model is not None:
                    girdi = scaler.transform([[toplam_kalori, toplam_karb, agirlikli_gi]])
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
                        <p style="font-size:18px;font-weight:500;color:#DD5A43;margin:0;">{baslik}</p>
                        <p style="color:#475569;font-size:14px;margin:8px 0 0;">{aciklama}</p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception:
                pass

            # Günlüğe Ekleme
            st.session_state["son_analiz_coklu"] = {
                "yemekler": yemek_detaylari,
                "ek_kalemler": ek_kalemler,
                "toplam_kalori": toplam_kalori,
                "toplam_protein": toplam_protein,
                "toplam_yag": toplam_yag,
                "toplam_karb": toplam_karb,
                "toplam_gram": toplam_gram,
            }
            st.session_state["analiz_tamamlandi"] = True

        elif aktif_fotograf and not analiz_baslat:
            st.image(pil_img, width="stretch")
        else:
            st.markdown("""
            <div class="bos_alan">
                <p style="font-size:64px;margin:0;">🍽️</p>
                <p style="color:#DD5A43;font-size:18px;font-weight:500;margin:16px 0 6px;">
                    Fotoğraf yükle ve analiz et
                </p>
                <p style="color:#94A3B8;font-size:14px;margin:0;">
                    Sonuçlar burada görünecek
                </p>
            </div>
            """, unsafe_allow_html=True)