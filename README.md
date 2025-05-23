
## Deskripsi Proyek
HealthierBot adalah chatbot dalam bidang kesehatan medis yang dirancang untuk membantu pengguna dalam berbagai aspek kesehatan dan nutrisi. Proyek ini menggunakan teknologi Natural Language Processing(NLP) dan Speech Recognition (SR) untuk menghasilkan chatbot sederhana berdasarkan gejala yang diinput pengguna.

## Fitur Utama
**Chatbot based on API AI** : Chatbot akan memberikan deskripsi sesuai dengan dataset symptom_Description dan memberikan output yang sesuai.


## Struktur Proyek

```
HEALTHYBOT_STREAMLIT/
├── __pycache__/
│   ├── __init__.py
│   ├── __init__.cpython-310.pyc
│   ├── utils.cpython-313.pyc
│   ├── utils.cpython-313.pyc
├── backend/
│   ├── __init__.py
├── main.py
├── models.py
├── routes.py
├── uiux.py
├── disease symptom prediction/
├── fine_tuned_model/
├── results/
├── .env
├── chatbot_medical_dataset.json
├── package-lock.json
├── package.json
└── README.md
```

---

## Persyaratan Sistem

### Python versi: `>=3.8`

### Library yang dibutuhkan:

Install terlebih dahulu semua dependensi berikut:

```bash
pip install fastapi uvicorn python-dotenv transformers torch librosa
```

---

## Setup & Menjalankan Aplikasi

### 1. Clone Repository (opsional jika disimpan di GitHub)

```bash
git clone https://github.com/owenp28/HealthierBot.git
cd HealthierBot
```

### 2. Siapkan File `.env`

Buat file `.env` di direktori root:

```
DB_HOST=localhost
DB_USER=root
DB_PASS=
DEBUG=True
PORT=8000
```

### 3. Siapkan File Dataset

* `chatbot_medical_dataset.json`
  Isinya sebagai berikut :

  ```json
  [
    "prompt":"what is drug reaction?",
    "response":"an adverse drug reaction (adr) is an injury caused by taking medication. adrs may occur following a single dose or prolonged   administration of a drug or result from the combination of two or more drugs."
  ]
  ```

* `symptom_Description.csv`
  Isinya sebagai berikut :

  ```
  Disease,Description
  Drug Reaction,An adverse drug reaction (ADR) is an injury caused by taking medication. ADRs may occur following a single dose or prolonged administration of a drug or result from the combination of two or more drugs.
  Malaria,An infectious disease caused by protozoan parasites from the Plasmodium family that can be transmitted by the bite of the Anopheles mosquito or by a contaminated needle or transfusion. Falciparum malaria is the most deadly type.
  Allergy,"An allergy is an immune system response to a foreign substance that's not typically harmful to your body.They can include certain foods, pollen, or pet dander. Your immune system's job is to keep you healthy by fighting harmful pathogens."
  ```

---

##  Menjalankan FastAPI Server

Jalankan dengan:

```bash
uvicorn main:app --reload
```

API akan berjalan di `http://127.0.0.1:8000`.

---

##  Endpoint API

###  Root

```http
GET /
```

**Response:**

```json
{ "message": "Welcome to HealthierBot!" }
```

---

###  Chat Gejala Penyakit

```http
POST /api/chat
```

**Request:**

```json
{ "input": "I have a fever and body ache" }
```

**Response:**

```json
{
  "response": { "disease_name": "flu" },
  "description": "Flu is a common viral infection that can be deadly for high-risk groups."
}
```

---

##  Model NLP (LLM) & Pelatihan

Model digunakan dari Huggingface (misal `llama4:scout`).

### 🔹 Untuk Melatih Model Baru:

```bash
python models.py
```

### 🔹 Untuk Inferensi Chatbot (tanpa pelatihan ulang):

```bash
RUN_INFERENCE=1 python models.py
```

---

## Fitur Speech Recognition: Transkripsi Teks menjadi Suara (Text to Speech)

Library `librosa` dan model `Wav2Vec2` digunakan untuk mengubah teks menjadi audio.

### Contoh:

```python
from models import transcribe_audio
transcribe_audio("path_to_your_audio_file.wav")
```

---

##  Catatan

* Endpoint `/diet` dan `/calories` masih menggunakan **template sederhana**. Dapat dikembangkan dengan LLM atau aturan berbasis data gizi.
* File `backends.py` dan `routes.py` memiliki fungsi mirip; pastikan kamu memilih salah satu integrasi endpoint secara konsisten.
* Endpoint `/process` dalam `routes.py` hanya akan aktif jika di-include ke dalam `main.py`.

---

## Testing API

Gunakan tools seperti:

* [Postman](https://www.postman.com/)
* [curl](https://curl.se/)
* atau akses `http://127.0.0.1:8000/docs` untuk **Swagger UI** otomatis dari FastAPI.

---

## UI/UX FrontEnd Dengan Streamlit 

## Instalasi

1. **Clone repositori** atau simpan project Anda.

2. Buka terminal dan buat environment baru (opsional):

   ```bash
   python -m venv venv
   source venv/bin/activate  # atau venv\Scripts\activate di Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   Jika belum ada `requirements.txt`, berikut dependensi yang dibutuhkan:

   ```bash
   pip install streamlit pandas transformers speechrecognition
   ```

   Pastikan juga Anda memiliki:
   * `ffmpeg` terinstal (untuk proses audio)
   * `PyAudio` (opsional, jika ingin gunakan input mikrofon)

---

## Menjalankan Aplikasi

Di terminal, jalankan perintah:

```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser, atau akses melalui `http://localhost:8501`

---

## Model ASR

Fitur **Speech-to-Text** menggunakan model:

```
facebook/wav2vec2-base-960h
```

Model ini dimuat dari **Hugging Face Transformers** untuk pengenalan suara otomatis.

---

## 📌 Catatan

* Format file audio harus `.wav`.
* Bahasa pengenalan suara bisa ke bahasa apa saja yang penting **terdengar dengan jelas**, jika tidak audio tidak akan dikenali
* Fitur diagnosis mendukung pencocokan sederhana berdasarkan string dari deskripsi gejala.

---
---

## Pengembangan Lanjutan

* Integrasi dengan basis data penyakit nyata (WHO/CDC).
* LLM fine-tuning lebih dalam dengan data medis yang lebih kaya.

---
