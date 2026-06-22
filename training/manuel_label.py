import sys
from pathlib import Path
import shutil
import numpy as np
import cv2
import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates
 
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
 
def polygon_to_normalized(points, w, h):
    # [(x,y), ...] -> [x1/w, y1/h, x2/w, y2/h, ...]
    arr = np.array(points, dtype=np.float32)
    arr[:, 0] /= w
    arr[:, 1] /= h
    return arr.flatten()
 
def maske_to_polygon_norm(mask):
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
 
def polygon_to_mask(points, h, w):
    # Polygon noktalarini ikili maskeye cevirir
    mask = np.zeros((h, w), dtype=np.uint8)
    pts = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [pts], 1)
    return mask.astype(bool)
 
def overlay_olustur(img_bgr, polygons, sinif, aktif_noktalar=None, sam_maskeler=None):
    h, w = img_bgr.shape[:2]
    sonuc = img_bgr.copy()
    renk = RENKLER_BGR[sinif]
    
    # Tamamlanmis polygonlar (dolgu + sinir)
    if polygons:
        overlay = sonuc.copy()
        for poly in polygons:
            pts = np.array(poly, dtype=np.int32)
            cv2.fillPoly(overlay, [pts], renk)
        sonuc = cv2.addWeighted(sonuc, 0.55, overlay, 0.45, 0)
        for poly in polygons:
            pts = np.array(poly, dtype=np.int32)
            cv2.polylines(sonuc, [pts], True, renk, 3)
    
    # SAM maskeler (varsa)
    if sam_maskeler is not None and len(sam_maskeler) > 0:
        overlay = sonuc.copy()
        for m in sam_maskeler:
            if m.shape != (h, w):
                m = cv2.resize(m.astype(np.uint8), (w, h),
                             interpolation=cv2.INTER_NEAREST).astype(bool)
            overlay[m] = renk
        sonuc = cv2.addWeighted(sonuc, 0.55, overlay, 0.45, 0)
        for m in sam_maskeler:
            if m.shape != (h, w):
                m = cv2.resize(m.astype(np.uint8), (w, h),
                             interpolation=cv2.INTER_NEAREST).astype(bool)
            m_uint8 = (m.astype(np.uint8) * 255)
            konturlar, _ = cv2.findContours(m_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(sonuc, konturlar, -1, renk, 3)
    
    # Aktif (yari tamamlanmis) polygon noktalari
    if aktif_noktalar:
        # Noktalar arasi cizgiler
        if len(aktif_noktalar) > 1:
            pts = np.array(aktif_noktalar, dtype=np.int32)
            cv2.polylines(sonuc, [pts], False, (0, 255, 0), 2)
        # Her noktayi ciz
        for i, (px, py) in enumerate(aktif_noktalar):
            cv2.circle(sonuc, (px, py), 8, (0, 255, 0), -1)
            cv2.circle(sonuc, (px, py), 8, (0, 0, 0), 2)
            cv2.putText(sonuc, str(i+1), (px+12, py-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return sonuc
 
# State init
def reset_aktif():
    st.session_state.aktif_noktalar = []
    st.session_state.polygons = []
    st.session_state.sam_noktalar = []
    st.session_state.sam_maskeler = None
 
if "aktif_noktalar" not in st.session_state:
    st.session_state.aktif_noktalar = []
if "polygons" not in st.session_state:
    st.session_state.polygons = []
if "sam_noktalar" not in st.session_state:
    st.session_state.sam_noktalar = []
if "sam_maskeler" not in st.session_state:
    st.session_state.sam_maskeler = None
if "secili_sinif" not in st.session_state:
    st.session_state.secili_sinif = "baklava"
if "foto_idx" not in st.session_state:
    st.session_state.foto_idx = 0
if "modu" not in st.session_state:
    st.session_state.modu = "polygon"
 
st.title("Manuel Yemek Etiketleme")
 
with st.sidebar:
    st.header("Ayarlar")
    secili = st.selectbox("Sinif:", list(SINIFLAR.keys()),
                          index=list(SINIFLAR.keys()).index(st.session_state.secili_sinif))
    if secili != st.session_state.secili_sinif:
        st.session_state.secili_sinif = secili
        st.session_state.foto_idx = 0
        reset_aktif()
        st.rerun()
    
    st.divider()
    modu = st.radio("Mod:", ["polygon", "sam_nokta"],
                     index=0 if st.session_state.modu == "polygon" else 1,
                     help="Polygon: yemegin sinirina 4-8 nokta koy. SAM Nokta: yemek uzerine 1-2 nokta, SAM tahmin etsin.")
    if modu != st.session_state.modu:
        st.session_state.modu = modu
        reset_aktif()
        st.rerun()
    
    klasor = RAW_KLASOR / secili
    tum_fotolar = sorted(klasor.glob("*.jpg"))
    preview_klasor = PREVIEW / secili
    preview_klasor.mkdir(parents=True, exist_ok=True)
    etiketli = {p.stem for p in preview_klasor.glob("*.jpg")}
    fotolar = [f for f in tum_fotolar if f.stem not in etiketli]
    
    st.metric("Toplam", len(tum_fotolar))
    st.metric("Etiketli", len(etiketli & {f.stem for f in tum_fotolar}))
    st.metric("Kalan", len(fotolar))
    
    if fotolar:
        st.metric("Suanki", f"{st.session_state.foto_idx + 1}/{len(fotolar)}")
 
CIKTI_IMG.mkdir(parents=True, exist_ok=True)
CIKTI_LBL.mkdir(parents=True, exist_ok=True)
(PREVIEW / secili).mkdir(parents=True, exist_ok=True)
 
if not fotolar:
    st.success(f"{secili} sinifinda etiketlenecek foto kalmadi")
    st.stop()
 
if st.session_state.foto_idx >= len(fotolar):
    st.session_state.foto_idx = 0
 
foto_path = fotolar[st.session_state.foto_idx]
img_bgr = cv2.imread(str(foto_path))
h, w = img_bgr.shape[:2]
 
col1, col2 = st.columns([3, 1])
 
with col2:
    st.write(f"**Foto:** {foto_path.name}")
    st.write(f"**Sinif:** {secili}")
    st.write(f"**Mod:** {st.session_state.modu}")
    
    if st.session_state.modu == "polygon":
        st.write(f"**Aktif noktalar:** {len(st.session_state.aktif_noktalar)}")
        st.write(f"**Tamamlanmis polygons:** {len(st.session_state.polygons)}")
    else:
        st.write(f"**SAM noktalar:** {len(st.session_state.sam_noktalar)}")
    
    st.divider()
    
    if st.session_state.modu == "polygon":
        # Polygon tamamla butonu - aktif noktalari polygona cevir
        yeterli = len(st.session_state.aktif_noktalar) >= 3
        if st.button("Polygon'u Kapat", type="primary", use_container_width=True,
                     disabled=not yeterli,
                     help="3+ nokta varsa polygonu kapatir, yeni yemek icin baska noktalar koyabilirsin"):
            st.session_state.polygons.append(list(st.session_state.aktif_noktalar))
            st.session_state.aktif_noktalar = []
            st.rerun()
        
        # Kaydet butonu - tum polygonlar dosyaya yazilir
        kayit_aktif = (len(st.session_state.polygons) > 0 or
                       len(st.session_state.aktif_noktalar) >= 3)
        if st.button("Kabul Et ve Kaydet", type="primary", use_container_width=True,
                     disabled=not kayit_aktif):
            sinif_id = SINIFLAR[secili]
            
            # Aktif olan polygon varsa onu da ekle
            tum_polygons = list(st.session_state.polygons)
            if len(st.session_state.aktif_noktalar) >= 3:
                tum_polygons.append(list(st.session_state.aktif_noktalar))
            
            etiket_satirlari = []
            for poly in tum_polygons:
                norm = polygon_to_normalized(poly, w, h)
                satir = f"{sinif_id} " + " ".join(f"{c:.6f}" for c in norm)
                etiket_satirlari.append(satir)
            
            base = foto_path.stem
            shutil.copy(foto_path, CIKTI_IMG / f"{base}.jpg")
            with open(CIKTI_LBL / f"{base}.txt", "w") as f:
                f.write("\n".join(etiket_satirlari) + "\n")
            
            # Preview - tum polygonlari ciz
            preview_img = overlay_olustur(img_bgr, tum_polygons, secili)
            cv2.imwrite(str(PREVIEW / secili / f"{base}.jpg"), preview_img,
                       [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            st.success(f"Kaydedildi: {len(tum_polygons)} polygon")
            reset_aktif()
            st.session_state.foto_idx += 1
            st.rerun()
    else:
        # SAM nokta modu
        if st.button("SAM2 Maskele", type="primary", use_container_width=True,
                     disabled=len(st.session_state.sam_noktalar) == 0):
            with st.spinner("Maskeleniyor..."):
                sam = sam_yukle()
                points_arr = np.array(st.session_state.sam_noktalar)
                labels_arr = np.ones(len(st.session_state.sam_noktalar))
                results = sam(str(foto_path), points=points_arr.tolist(),
                             labels=labels_arr.tolist(), verbose=False)
                if results and results[0].masks is not None:
                    st.session_state.sam_maskeler = results[0].masks.data.cpu().numpy().astype(bool)
                    st.success(f"{len(st.session_state.sam_maskeler)} maske")
                else:
                    st.error("Maske olusturulamadi")
            st.rerun()
        
        if st.button("Kabul Et ve Kaydet", type="primary", use_container_width=True,
                     disabled=st.session_state.sam_maskeler is None):
            sinif_id = SINIFLAR[secili]
            etiket_satirlari = []
            gecerli_maskeler = []
            
            for m in st.session_state.sam_maskeler:
                if m.shape != (h, w):
                    m = cv2.resize(m.astype(np.uint8), (w, h),
                                 interpolation=cv2.INTER_NEAREST).astype(bool)
                if m.sum() < 100:
                    continue
                polygon = maske_to_polygon_norm(m)
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
                preview_img = overlay_olustur(img_bgr, [], secili, sam_maskeler=gecerli_maskeler)
                cv2.imwrite(str(PREVIEW / secili / f"{base}.jpg"), preview_img,
                           [cv2.IMWRITE_JPEG_QUALITY, 90])
                st.success(f"Kaydedildi: {base}")
                reset_aktif()
                st.session_state.foto_idx += 1
                st.rerun()
    
    if st.button("Atla", use_container_width=True):
        reset_aktif()
        st.session_state.foto_idx += 1
        st.rerun()
    
    if st.button("Sifirla", use_container_width=True):
        reset_aktif()
        st.rerun()
    
    if st.session_state.modu == "polygon":
        if st.button("Son Noktayi Sil", use_container_width=True,
                     disabled=len(st.session_state.aktif_noktalar) == 0):
            st.session_state.aktif_noktalar.pop()
            st.rerun()
    else:
        if st.button("Son Noktayi Sil", use_container_width=True,
                     disabled=len(st.session_state.sam_noktalar) == 0):
            st.session_state.sam_noktalar.pop()
            st.session_state.sam_maskeler = None
            st.rerun()
 
with col1:
    if st.session_state.modu == "polygon":
        st.write("**Yemegin sinirina nokta nokta tikla** (saat yonunde ya da rastgele), 3+ nokta toplaninca **'Polygon'u Kapat'** veya direkt **'Kabul Et'**")
    else:
        st.write("**Yemek uzerine 1-2 nokta tikla**, SAM2 maskeleyecek")
    
    if st.session_state.modu == "polygon":
        display_img = overlay_olustur(
            img_bgr, st.session_state.polygons, secili,
            aktif_noktalar=st.session_state.aktif_noktalar
        )
    else:
        display_img = overlay_olustur(
            img_bgr, [], secili,
            aktif_noktalar=st.session_state.sam_noktalar,
            sam_maskeler=st.session_state.sam_maskeler
        )
    
    display_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(display_rgb)
    
    max_w = 800
    if pil_img.width > max_w:
        oran = max_w / pil_img.width
        pil_img_display = pil_img.resize((max_w, int(pil_img.height * oran)))
    else:
        pil_img_display = pil_img
        oran = 1.0
    
    koord = streamlit_image_coordinates(pil_img_display, key=f"img_{st.session_state.foto_idx}")
    
    if koord is not None:
        x_orig = int(koord["x"] / oran)
        y_orig = int(koord["y"] / oran)
        
        if st.session_state.modu == "polygon":
            son = st.session_state.aktif_noktalar[-1] if st.session_state.aktif_noktalar else None
            if son is None or abs(son[0] - x_orig) > 5 or abs(son[1] - y_orig) > 5:
                st.session_state.aktif_noktalar.append((x_orig, y_orig))
                st.rerun()
        else:
            son = st.session_state.sam_noktalar[-1] if st.session_state.sam_noktalar else None
            if son is None or abs(son[0] - x_orig) > 5 or abs(son[1] - y_orig) > 5:
                st.session_state.sam_noktalar.append([x_orig, y_orig])
                st.session_state.sam_maskeler = None
                st.rerun()
