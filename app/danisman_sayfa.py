import streamlit as st
from app.gunluk_takip import gunluk_ozet, kullanici_hedefi
from app.ollama_client import mesaj_gonder, ollama_calisiyor_mu

def danisman_sayfa_goster(aktif_kullanici):
 
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
            # Profil ve günlük bilgisini chatbot'a aktar
            from app.gunluk_takip import kullanici_profili as kp_getir, gunluk_ozet as go_getir, kullanici_hedefi as kh_getir

            profil_dict = kp_getir(aktif_kullanici)
            profil_dict["ad"] = aktif_kullanici  # Adı da ekle

            ozet_bilgi = go_getir(aktif_kullanici)
            gunluk_dict = {
                "toplam_kalori": ozet_bilgi["toplam_kalori"],
                "hedef": kh_getir(aktif_kullanici),
                "ogunler": ozet_bilgi["ogunler"],
            }

            cevap = mesaj_gonder(
                kullanici_mesaji,
                sohbet_gecmisi=st.session_state.mesajlar,
                yemek_bilgisi=st.session_state.get("son_analiz_coklu"),
                kullanici_profili=profil_dict,
                gunluk_durum=gunluk_dict
            )
 
        st.session_state.mesajlar.append({"rol": "asistan", "icerik": cevap})
        st.rerun()