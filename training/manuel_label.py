import sys
from pathlib import Path
import shutil
import numpy as np
import cv2
import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates
 
# Proje koku
PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))
 
RAW_KLASOR = PROJE_KOK / "data" / "raw_images"
CIKTI_IMG = PROJE_KOK / "data" / "yolo_dataset" / "images"
CIKTI_LBL = PROJE_KOK / "data" / "yolo_dataset" / "labels"
PREVIEW = PROJE_KOK / "data" / "preview"
 
SINIFLAR = {
    "baklava": 0,
    "kebap": 1,
    "lahmacun": 2,
    "pirinc_pilavi": 3
}
 
RENKLER_BGR = {
    "baklava":       (10, 112, 212),
    "kebap":         (60, 90, 200),
    "lahmacun":      (50, 170, 240),
    "pirinc_pilavi": (180, 180, 180)
}
 
st.set_page_config(page_title="Manuel Etiketleme", layout="wide")
 
@st.cache_resource
def sam_yukle():
    from ultralytics import SAM
    return SAM("sam2_b.pt")
 
def maske_to_polygon(mask):
    mask_uint8 = (mask.astype(np.uint8) * 255)
    h, w = mask_uint8.shape
    konturlar, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not konturlar:
        return None
    kontur = max(konturlar, key=cv2.contourArea)
    if len(kontur) < 3:
        return None
    epsilon = 0.002 * cv2.arcLength(kontur, True)
    kontur_basit = cv2.approxPolyDP(kontur, epsilon, True)
    if len(kontur_basit) < 3:
        kontur_basit = kontur
    points = kontur_basit.reshape(-1, 2).astype(np.float32)
    points[:, 0] /= w
    points[:, 1] /= h
    return points.flatten()
 
def overlay_olustur(img_bgr, maskeler, sinif, noktalar=None):
    h, w = img_bgr.shape[:2]
    sonuc = img_bgr.copy()
    
    if maskeler is not None and len(maskeler) > 0:
        renk = RENKLER_BGR[sinif]
        overlay = sonuc.copy()
        for m in maskeler:
            if m.shape != (h, w):
                m = cv2.resize(m.astype(np.uint8), (w, h),
                             interpolation=cv2.INTER_NEAREST).astype(bool)
            overlay[m] = renk
        sonuc = cv2.addWeighted(sonuc, 0.55, overlay, 0.45, 0)
        for m in maskeler:
            if m.shape != (h, w):
                m = cv2.resize(m.astype(np.uint8), (w, h),
                             interpolation=cv2.INTER_NEAREST).astype(bool)
            m_uint8 = (m.astype(np.uint8) * 255)
            konturlar, _ = cv2.findContours(m_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(sonuc, konturlar, -1, renk, 3)
    
    if noktalar:
        for i, (px, py) in enumerate(noktalar):
            cv2.circle(sonuc, (px, py), 10, (0, 255, 0), -1)
            cv2.circle(sonuc, (px, py), 10, (0, 0, 0), 2)
    
    return sonuc
 
# State init
if "noktalar" not in st.session_state:
    st.session_state.noktalar = []
if "maskeler" not in st.session_state:
    st.session_state.maskeler = None
if "secili_sinif" not in st.session_state:
    st.session_state.secili_sinif = "kebap"
if "foto_idx" not in st.session_state:
    st.session_state.foto_idx = 0
 
st.title("🍽️ Manuel Yemek Etiketleme")
 
# Sidebar
with st.sidebar:
    st.header("Ayarlar")
    secili = st.selectbox("Sinif:", list(SINIFLAR.keys()),
                          index=list(SINIFLAR.keys()).index(st.session_state.secili_sinif))
    if secili != st.session_state.secili_sinif:
        st.session_state.secili_sinif = secili
        st.session_state.foto_idx = 0
        st.session_state.noktalar = []
        st.session_state.maskeler = None
        st.rerun()
    
    # Bu sinifin fotolarini listele, preview'da olanlari (etiketlenmis) atla
    klasor = RAW_KLASOR / secili
    tum_fotolar = sorted(klasor.glob("*.jpg"))
    preview_klasor = PREVIEW / secili
    preview_klasor.mkdir(parents=True, exist_ok=True)
    etiketli = {p.stem for p in preview_klasor.glob("*.jpg")}
    fotolar = [f for f in tum_fotolar if f.stem not in etiketli]
    
    st.metric("Toplam foto", len(tum_fotolar))
    st.metric("Etiketli", len(etiketli & {f.stem for f in tum_fotolar}))
    st.metric("Kalan", len(fotolar))
    
    if fotolar:
        st.metric("Suanki", f"{st.session_state.foto_idx + 1}/{len(fotolar)}")
 
# Hazirla
CIKTI_IMG.mkdir(parents=True, exist_ok=True)
CIKTI_LBL.mkdir(parents=True, exist_ok=True)
(PREVIEW / secili).mkdir(parents=True, exist_ok=True)
 
if not fotolar:
    st.success(f"✅ {secili} sinifinda etiketlenecek foto kalmadi!")
    st.stop()
 
# Idx kontrol
if st.session_state.foto_idx >= len(fotolar):
    st.session_state.foto_idx = 0
 
foto_path = fotolar[st.session_state.foto_idx]
img_bgr = cv2.imread(str(foto_path))
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
h, w = img_bgr.shape[:2]
 
col1, col2 = st.columns([3, 1])
 
with col2:
    st.write(f"**Foto:** {foto_path.name}")
    st.write(f"**Sinif:** {secili}")
    st.write(f"**Boyut:** {w}x{h}")
    st.write(f"**Noktalar:** {len(st.session_state.noktalar)}")
    
    st.divider()
    
    # Butonlar
    if st.button("🎯 SAM2 Maskele", type="primary", use_container_width=True,
                 disabled=len(st.session_state.noktalar) == 0):
        with st.spinner("Maskeleniyor..."):
            sam = sam_yukle()
            points_arr = np.array(st.session_state.noktalar)
            labels_arr = np.ones(len(st.session_state.noktalar))
            
            results = sam(str(foto_path),
                         points=points_arr.tolist(),
                         labels=labels_arr.tolist(),
                         verbose=False)
            
            if results and results[0].masks is not None:
                st.session_state.maskeler = results[0].masks.data.cpu().numpy().astype(bool)
                st.success(f"{len(st.session_state.maskeler)} maske olusturuldu")
            else:
                st.error("Maske olusturulamadi")
        st.rerun()
    
    if st.button("✅ Kabul Et ve Kaydet", type="primary", use_container_width=True,
                 disabled=st.session_state.maskeler is None):
        sinif_id = SINIFLAR[secili]
        etiket_satirlari = []
        gecerli_maskeler = []
        
        for m in st.session_state.maskeler:
            if m.shape != (h, w):
                m = cv2.resize(m.astype(np.uint8), (w, h),
                             interpolation=cv2.INTER_NEAREST).astype(bool)
            if m.sum() < 100:
                continue
            polygon = maske_to_polygon(m)
            if polygon is None:
                continue
            satir = f"{sinif_id} " + " ".join(f"{c:.6f}" for c in polygon)
            etiket_satirlari.append(satir)
            gecerli_maskeler.append(m)
        
        if etiket_satirlari:
            base = foto_path.stem
            shutil.copy(foto_path, CIKTI_IMG / f"{base}.jpg")
            with open(CIKTI_LBL / f"{base}.txt", "w") as f:
                f.write("\n".join(etiket_satirlari) + "\n")
            
            preview_img = overlay_olustur(img_bgr, gecerli_maskeler, secili)
            cv2.imwrite(str(PREVIEW / secili / f"{base}.jpg"), preview_img,
                       [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            st.success(f"Kaydedildi: {base}")
            st.session_state.noktalar = []
            st.session_state.maskeler = None
            st.session_state.foto_idx += 1
            st.rerun()
        else:
            st.error("Gecerli maske yok")
    
    if st.button("⏭️ Atla", use_container_width=True):
        st.session_state.noktalar = []
        st.session_state.maskeler = None
        st.session_state.foto_idx += 1
        st.rerun()
    
    if st.button("🗑️ Noktalari Sifirla", use_container_width=True):
        st.session_state.noktalar = []
        st.session_state.maskeler = None
        st.rerun()
    
    if st.button("↩️ Son Noktayi Sil", use_container_width=True,
                 disabled=len(st.session_state.noktalar) == 0):
        st.session_state.noktalar.pop()
        st.session_state.maskeler = None
        st.rerun()
 
with col1:
    st.write("**Yemek uzerine tiklayin** (her ayri parca icin ayri nokta)")
    
    # Goruntu olustur
    display_img = overlay_olustur(img_bgr, st.session_state.maskeler,
                                   secili, st.session_state.noktalar)
    display_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(display_rgb)
    
    # Genislik sinirla (cok buyuk fotolar icin)
    max_w = 800
    if pil_img.width > max_w:
        oran = max_w / pil_img.width
        yeni_h = int(pil_img.height * oran)
        pil_img_display = pil_img.resize((max_w, yeni_h))
    else:
        pil_img_display = pil_img
        oran = 1.0
    
    # Tiklanabilir image
    koord = streamlit_image_coordinates(pil_img_display, key=f"img_{st.session_state.foto_idx}")
    
    if koord is not None:
        # Tiklama varsa orijinal koordinatlara cevir
        x_orig = int(koord["x"] / oran)
        y_orig = int(koord["y"] / oran)
        
        # Ayni noktaya cift tiklama olmasin
        son_nokta = st.session_state.noktalar[-1] if st.session_state.noktalar else None
        if son_nokta is None or abs(son_nokta[0] - x_orig) > 5 or abs(son_nokta[1] - y_orig) > 5:
            st.session_state.noktalar.append([x_orig, y_orig])
            st.session_state.maskeler = None  # yeni nokta, maske sifirlansin
            st.rerun()
