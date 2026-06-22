import numpy as np
import cv2
from PIL import Image
 
RENKLER_BGR = {
    "baklava":       (10, 112, 212),
    "kebap":         (60, 90, 200),
    "lahmacun":      (50, 170, 240),
    "pirinc_pilavi": (180, 180, 180)
}
 
def maskeli_goruntu_olustur(orijinal_pil_img, maskeler, tespitler, alfa=0.45):
    # PIL Image -> BGR numpy
    img_rgb = np.array(orijinal_pil_img.convert("RGB"))
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    h, w = img_bgr.shape[:2]
    
    if maskeler is None or len(maskeler) == 0:
        return orijinal_pil_img
    
    overlay = img_bgr.copy()
    
    # Her maskeyi ilgili sinif rengiyle ciz
    for i, m in enumerate(maskeler):
        # Maskeyi orijinal boyuta resize et
        if m.shape != (h, w):
            m_resized = cv2.resize(m.astype(np.uint8), (w, h),
                                  interpolation=cv2.INTER_NEAREST).astype(bool)
        else:
            m_resized = m.astype(bool)
        
        # Sinif adini bul
        sinif = "baklava"  # default
        if i < len(tespitler):
            sinif = tespitler[i].get("sinif", "baklava")
        
        renk = RENKLER_BGR.get(sinif, (10, 112, 212))
        overlay[m_resized] = renk
    
    # Yari saydam birlestir
    sonuc = cv2.addWeighted(img_bgr, 1 - alfa, overlay, alfa, 0)
    
    # Kontur ciz (sinir cizgileri)
    for i, m in enumerate(maskeler):
        if m.shape != (h, w):
            m_resized = cv2.resize(m.astype(np.uint8), (w, h),
                                  interpolation=cv2.INTER_NEAREST).astype(bool)
        else:
            m_resized = m.astype(bool)
        
        sinif = tespitler[i].get("sinif", "baklava") if i < len(tespitler) else "baklava"
        renk = RENKLER_BGR.get(sinif, (10, 112, 212))
        
        m_uint8 = (m_resized.astype(np.uint8) * 255)
        konturlar, _ = cv2.findContours(m_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(sonuc, konturlar, -1, renk, 3)
    
    # BGR -> PIL
    sonuc_rgb = cv2.cvtColor(sonuc, cv2.COLOR_BGR2RGB)
    return Image.fromarray(sonuc_rgb)