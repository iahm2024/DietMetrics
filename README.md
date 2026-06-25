# 🍽️ DietMetrics – Yapay Zeka Destekli Diyetisyen Takip Platformu

**Prompt Engineers** ekibi tarafından geliştirilen DietMetrics; diyetisyen-danışan ilişkisini dijital ortama taşıyan, yapay zeka (Görüntü İşleme & Yerel LLM) destekli **B2B2C** odaklı bir uzaktan beslenme takip platformudur. 

Tabağınızın fotoğrafını çekin, gerisini yapay zekaya bırakın. Sistem, YOLO mimarisi ile tabağınızdaki yemeği tanır, referans nesneler üzerinden porsiyon tahmini yapar ve günlüğünüze işler. Ayrıca dolabınızdaki malzemelere göre **RAG (Retrieval-Augmented Generation)** kullanarak size özel tarifler üretir. 
Danışanların manuel kalori hesabı yapma derdini ortadan kaldırır, diyetisyenlere ise klinik seansları dışında danışanlarının gelişimini anlık izleme imkanı sunar. Sistem tamamen **çevrimdışı (offline)** çalışacak şekilde tasarlanmış olup, veri gizliliğini maksimum seviyede tutar.

## ✨ Öne Çıkan Özellikler

* 📸 **Instance Segmentation ile Görsel Tabak Analizi:** Custom eğitilmiş YOLO11m-seg mimarisi ile Türk mutfağına özgü yemekleri (Baklava, Kebap, Lahmacun, Pirinç Pilavı) tespit eder. COCO YOLOv8n referans nesne algılaması ile porsiyon/gramaj hesabı yapar.
* 🧠 **RAG Destekli Akıllı Öğün Önerisi:** Qwen2.5-7B yerel dil modeli ve FAISS vektör veritabanı kullanılarak, danışanın evindeki malzemelere ve o günkü *kalan kalori hedefine* uygun kişiselleştirilmiş sağlıklı öğün alternatifleri üretilir.
* 🩺 **Çok Rollü B2B2C Ekosistemi:**
  * **Danışan (Client):** Tabak analizi yapar, günlüğünü tutar, AI asistanından hedefine uygun tarifler alır.
  * **Diyetisyen (Dietitian):** Kendisine atanan danışanların günlük kalori/makro alımlarını, hedefe uyum yüzdelerini ve glisemik profillerini tek ekrandan anlık takip eder.
  * **Klinik Yöneticisi (Admin):** Sistemdeki profilleri yönetir, diyetisyen-danışan atamalarını gerçekleştirir.
* 📊 **MLP Karar Ağı ve Glisemik Profil:** Tabağın glisemik yükünü hesaplar. Eğitilmiş MLP modeli ile danışanın anlık durumuna göre ("Zengin içerik, sonraki öğünde dengeleyin" gibi) uzman görüşüyle uyumlu, yönlendirici bildirimler sunar.

## 🛠️ Kullanılan Teknolojiler

* **Arayüz & Backend:** Python, Streamlit
* **Görüntü İşleme (Computer Vision):** Ultralytics YOLO11, OpenCV, PIL
* **Doğal Dil İşleme (NLP & LLM):** Ollama (Qwen2.5:7b), FAISS, SentenceTransformers
* **Makine Öğrenmesi (Tabular):** Scikit-learn (MLP Classifier)

---

## 📈 Model Başarımı ve Eğitim Süreci (YOLO)

> **Geliştirici Notu:** Bu projede hazır bir yemek tanıma modeli kullanmak yerine, Türk mutfağına özgü yemekleri tanıyabilmesi için YOLO11m mimarisi üzerinde Transfer Learning ve Fine-Tuning yöntemleriyle kendi custom modelimizi eğittik.

Model eğitim sürecine dair detaylar ve metrikler:

* **Model Mimarisi:** YOLO11m
* **Veri Seti:** TurkishFoods-25 (Kayıkçı vd., IEEE UBMK 2019)
* **Eğitim Sonuçları:**
  * **mAP50 (Mask):** %82.3
  * **Sınıf Bazlı mAP50:** Baklava: %62.2 | Kebap: %81.7 | Lahmacun: %97.9 | Pilav: %87.5
  * **MLP Karar Ağı:** Test Accuracy: %96.3

### Örnek Tahminler (Predictions)
Aşağıda modelimizin tabaktaki yemekleri ve referans nesneleri nasıl tespit ettiğini görebilirsiniz:

<img width="1920" height="1280" alt="val_batch0_pred" src="https://github.com/user-attachments/assets/549fdb01-2f8c-4ef2-9730-5fdbbdee5cf2" />

### Analiz Grafikleri
Modelin öğrenme eğrisi ve sınıfları birbirinden ne kadar iyi ayırabildiğini gösteren matris tablosu:

<img width="4000" height="1200" alt="results" src="https://github.com/user-attachments/assets/58813218-c296-4a39-bfec-1da80f741f4f" />

<img width="3000" height="2250" alt="confusion_matrix" src="https://github.com/user-attachments/assets/cf702b04-e66d-49c1-981d-de909c5a7f18" />

---

## 🚀 Kurulum ve Projeyi Ayağa Kaldırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz.

### 1. Gereksinimler
* Python 3.9+
* [Ollama](https://ollama.ai/) (Lokal LLM için gereklidir)

### 2. Adımlar

Depoyu klonlayın ve bağımlılıkları yükleyin:
```bash
git clone https://github.com/iahm2024/DietMetrics.git
cd DietMetrics
pip install -r requirements.txt
```

Ollama'yı başlatın ve Qwen modelini indirin (Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir):

```bash
ollama run qwen2.5:7b
```

Projeyi başlatın:
```bash
streamlit run app/main.py
```

## 👥 Ekip: Prompt Engineers

Proje geliştirme sürecindeki görev dağılımımız:

  * İbrahim: Computer Vision & Proje Mimarisi

  * Eyüp: Arayüz (UI/UX) Tasarımı & Streamlit

  * Mehmet Emin: İş Modeli, Proje Fikri & Raporlama

  * Esad: Yerel Dil Modeli (LLM) & RAG Entegrasyonu

  * Sami: Veri Seti Toplama, Etiketleme & Optimizasyon

## 📸 Ekran Görüntüleri


## 📄 Lisans

Görüntü veri setimiz Apache 2.0 lisanslı olup ticari kullanıma uygundur. Projenin MVP aşamasında kullanılan Ultralytics modülleri gereği mevcut demomuz AGPL-3.0 lisans kuralları çerçevesinde sunulmaktadır.
