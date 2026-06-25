import streamlit as st
from app.gunluk_takip import gunluk_ozet, kullanici_hedefi

def tarif_sayfa_goster(aktif_kullanici):
    st.markdown("### 🥘 Sana Özel Tarif Önerisi")
    st.caption(
        "Dolabındaki malzemeleri yaz, sistem kalan kalorine uygun tarifler bulsun. "
        "Eksik bir şeyin varsa belirt (örn. 'sarımsağım yok'), AI uyarlayacak."
    )

    if aktif_kullanici:
        ozet_t = gunluk_ozet(aktif_kullanici)
        hedef_t = kullanici_hedefi(aktif_kullanici)
        kalan_kalori_t = max(hedef_t - ozet_t["toplam_kalori"], 0)

        bilgi_c1, bilgi_c2, bilgi_c3 = st.columns(3)
        with bilgi_c1:
            st.metric("Günlük Hedef", f"{hedef_t} kcal")
        with bilgi_c2:
            st.metric("Bugün Yenen", f"{ozet_t['toplam_kalori']:.0f} kcal")
        with bilgi_c3:
            st.metric("Kalan", f"{kalan_kalori_t:.0f} kcal")

        if kalan_kalori_t <= 0:
            st.warning("⚠️ Günlük kalori limitin doldu. Yine de tarif önerilebilir.")
    else:
        st.info("ℹ️ Profil seçmeden de kullanabilirsin, ama günlük kalori takibi için sidebar'dan profil oluştur.")
        kalan_kalori_t = 2000

    st.markdown("---")

    malzeme_girdi = st.text_area(
        "🥦 Dolabındaki malzemeleri yaz",
        placeholder="örn: tavuk, domates, soğan, zeytinyağı. Sarımsağım yok.",
        height=100,
        key="tarif_malzeme_input"
    )

    with st.expander("⚙️ Kalori limitini değiştir", expanded=False):
        manuel_kalori = st.slider(
            "Tarif için kalori üst sınırı (kcal)",
            min_value=100,
            max_value=2000,
            value=int(max(kalan_kalori_t, 200)),
            step=50,
            key="tarif_manuel_kalori"
        )

    kullanilacak_kalori = st.session_state.get("tarif_manuel_kalori", int(max(kalan_kalori_t, 200)))

    if st.button("🔍 Tarif Bul", type="primary", use_container_width=True, key="tarif_bul_btn"):
        if not malzeme_girdi.strip():
            st.warning("⚠️ Lütfen malzemeleri gir.")
        else:
            with st.spinner("🔎 Tarif veritabanı taranıyor..."):
                try:
                    from app.rag_motor import (
                        tarif_bul, kisit_var_mi, kisitlari_ayikla, malzemeleri_ayikla
                    )

                    # Once kisitlari ve gercek malzemeleri ayir
                    temiz_malzemeler, olmayanlar = malzemeleri_ayikla(malzeme_girdi)
                    # FAISS'e sadece istenen malzemeleri ver
                    sorgu_metni = temiz_malzemeler if temiz_malzemeler else malzeme_girdi

                    secilen, adaylar = tarif_bul(
                        sorgu_metni,
                        kullanilacak_kalori,
                        top_k=20,
                        olmayanlar=olmayanlar
                    )

                    if secilen is None:
                        st.error("Tarif bulunamadı.")
                    else:
                        # Kaloriye uyan adaylardan ilk 3'u al (cesitlilik icin)
                        kalori_uyan_adaylar = [
                            t for t in adaylar
                            if t["kalori"] <= kullanilacak_kalori * 1.1
                        ]
                        if not kalori_uyan_adaylar:
                            kalori_uyan_adaylar = adaylar[:5]

                        # Top 3 oneri
                        st.session_state["tarif_adaylar"] = kalori_uyan_adaylar[:3]
                        st.session_state["son_tarif"] = kalori_uyan_adaylar[0] if kalori_uyan_adaylar else secilen
                        st.session_state["son_tarif_istek"] = malzeme_girdi
                        st.session_state["son_tarif_olmayanlar"] = olmayanlar
                        st.session_state["son_tarif_kisit"] = bool(olmayanlar) or kisit_var_mi(malzeme_girdi)
                        st.session_state["son_tarif_uyarlama"] = None

                except FileNotFoundError as e:
                    st.error(f"❌ {e}")
                except Exception as e:
                    st.error(f"❌ Tarif sisteminde hata: {e}")

    # Aday tarifler
    if st.session_state.get("tarif_adaylar") and len(st.session_state["tarif_adaylar"]) > 1:
        st.markdown("---")
        st.markdown("#### 📋 Sana en uygun tarifler")
        st.caption("Diğer tarifi görmek için üzerine tıkla.")

        adaylar_secim = st.session_state["tarif_adaylar"]
        secili_ad = st.session_state["son_tarif"]["ad"]
        sec_cols = st.columns(len(adaylar_secim))

        for ix, aday in enumerate(adaylar_secim):
            with sec_cols[ix]:
                aktif = (secili_ad == aday["ad"])
                btn_tip = "primary" if aktif else "secondary"

                # Buton metnini sade tut (markdown artifact olmasin)
                buton_metni = f"{aday['ad']} — {aday['kalori']:.0f} kcal"
                if aktif:
                    buton_metni = "✓ " + buton_metni

                if st.button(
                    buton_metni,
                    key=f"aday_sec_{ix}",
                    type=btn_tip,
                    use_container_width=True
                ):
                    st.session_state["son_tarif"] = aday
                    st.session_state["son_tarif_uyarlama"] = None
                    st.rerun()

    # Bulunan tarifi goster
    if st.session_state.get("son_tarif"):
        tarif = st.session_state["son_tarif"]
        kisit_var = st.session_state.get("son_tarif_kisit", False)
        olmayanlar = st.session_state.get("son_tarif_olmayanlar", [])

        st.markdown("---")

        st.markdown(f"""
        <div class="kalori_kart">
            <p class="kart_baslik">🍽️ Şefin Önerisi</p>
            <p style="font-size:28px;font-weight:500;color:#1A202C;margin:8px 0 4px;">
                {tarif['ad']}
            </p>
            <p style="font-size:16px;color:#DD5A43;margin:0;">{tarif['kalori']:.0f} kcal</p>
        </div>
        """, unsafe_allow_html=True)

        # LLM uyarlamasi
        if kisit_var:
            if st.session_state.get("son_tarif_uyarlama") is None:
                with st.spinner("🤖 AI tarifi senin kısıtlarına göre uyarlıyor..."):
                    try:
                        from app.ollama_client import tarif_uyarla, ollama_calisiyor_mu
                        if ollama_calisiyor_mu():
                            uyarlama = tarif_uyarla(
                                tarif,
                                st.session_state["son_tarif_istek"],
                                olmayan_malzemeler=olmayanlar
                            )
                            st.session_state["son_tarif_uyarlama"] = uyarlama or "Uyarlama üretilemedi."
                        else:
                            st.session_state["son_tarif_uyarlama"] = "(Ollama çalışmıyor.)"
                    except Exception as e:
                        st.session_state["son_tarif_uyarlama"] = f"(Hata: {e})"

            if st.session_state.get("son_tarif_uyarlama"):
                st.markdown(f"""
                <div class="kart" style="border-left:3px solid #2563EB;">
                    <p class="kart_baslik">🤖 AI Uyarlaması</p>
                    <p style="color:#475569;font-size:15px;margin:8px 0 0;line-height:1.6;">
                        💡 {st.session_state['son_tarif_uyarlama']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kart">
            <p class="kart_baslik">🥗 Malzemeler</p>
            <p style="color:#475569;font-size:15px;margin:8px 0 0;line-height:1.8;white-space:pre-wrap;">{tarif['malzemeler_metin']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kart">
            <p class="kart_baslik">👨‍🍳 Yapılışı</p>
            <p style="color:#475569;font-size:15px;margin:8px 0 0;line-height:1.8;white-space:pre-wrap;">{tarif['yapilis_metin']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.caption("💡 Afiyet olsun! Başka tarif için tekrar 'Tarif Bul' diyebilirsin.")