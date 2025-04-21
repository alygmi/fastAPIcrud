# FastAPI CRUD API dengan PostgreSQL untuk User dan Jabatan

Proyek ini adalah implementasi sederhana dari API CRUD (Create, Read, Update, Delete) menggunakan framework FastAPI dan database PostgreSQL. API ini mengelola data User dan Jabatan.

## Struktur Proyek

```
my_project/
├── database.py # Konfigurasi koneksi database PostgreSQL dengan SQLAlchemy
├── main.py # Definisi aplikasi FastAPI dan semua endpoint API
├── models.py # Definisi model database SQLAlchemy (tabel dan relasi)
├── schemas.py # Definisi skema data Pydantic untuk validasi dan serialisasi
└── .env # File untuk menyimpan variabel lingkungan (misalnya, URL database)
```

## Prasyarat

- **Python 3.7+** terinstal di sistem Anda.
- **PostgreSQL** terinstal dan berjalan.
- **pip** (Python package installer) terinstal.

## Instalasi

1.  **Clone repositori (jika ada) atau buat direktori proyek:**

    ```bash
    # Jika menggunakan git
    git clone <repository_url>
    cd <project_directory>
    # Jika tidak, buat direktori dan masuk ke dalamnya
    mkdir my_project
    cd my_project
    ```

2.  **Buat dan aktifkan virtual environment (direkomendasikan):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Untuk Linux/macOS
    venv\Scripts\activate  # Untuk Windows
    ```

3.  **Instal dependensi dari file `requirements.txt` (jika ada) atau instal dependensi yang diperlukan secara manual:**

    ```bash
    pip install fastapi uvicorn psycopg2-binary python-dotenv sqlalchemy
    ```

    Penjelasan dependensi:

    - `fastapi`: Framework web modern dan cepat untuk membangun API.
    - `uvicorn`: ASGI server untuk menjalankan aplikasi FastAPI.
    - `psycopg2-binary`: Adaptor PostgreSQL untuk Python.
    - `python-dotenv`: Untuk membaca variabel lingkungan dari file `.env`.
    - `sqlalchemy`: Toolkit SQL dan ORM Python yang kuat.

4.  **Buat file `.env` di root proyek Anda dan konfigurasi URL database PostgreSQL Anda:**

    ```
    DATABASE_URL=postgresql://username:password@host:port/database_name
    ```

    Ganti `username`, `password`, `host`, `port`, dan `database_name` dengan kredensial dan detail server PostgreSQL Anda.

## Menjalankan Aplikasi

1.  Pastikan Anda berada di direktori root proyek (`my_project`).

2.  Jalankan server Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

    Opsi `--reload` akan secara otomatis me-restart server setiap kali Anda membuat perubahan pada kode.

3.  Buka browser atau alat API client (seperti Postman) dan kunjungi `http://127.0.0.1:8000` untuk melihat dokumentasi interaktif API (Swagger UI) yang dihasilkan oleh FastAPI.

## Endpoint API

### Jabatan

- **`GET /jabatan/`**: Mendapatkan daftar semua jabatan (dengan dukungan pagination menggunakan query parameter `skip` dan `limit`).
- **`GET /jabatan/{jabatan_id}`**: Mendapatkan detail jabatan berdasarkan ID.

### User

- **`POST /users/`**: Membuat user baru. Membutuhkan body JSON sesuai dengan skema `UserCreate`.
- **`GET /users/`**: Mendapatkan daftar semua user (dengan dukungan pagination menggunakan query parameter `skip` dan `limit`).
- **`GET /users/{user_id}`**: Mendapatkan detail user berdasarkan ID.
- **`PUT /users/{user_id}`**: Memperbarui data user berdasarkan ID. Membutuhkan body JSON sesuai dengan skema `UserUpdate`.
- **`DELETE /users/{user_id}`**: Menghapus user berdasarkan ID.

## Penggunaan API dengan Postman (Contoh)

1.  **Mendapatkan Daftar Jabatan:**

    - Metode: `GET`
    - URL: `http://127.0.0.1:8000/jabatan/`

2.  **Mendapatkan Detail Jabatan:**

    - Metode: `GET`
    - URL: `http://127.0.0.1:8000/jabatan/1` (ganti `1` dengan ID jabatan)

3.  **Membuat User Baru:**

    - Metode: `POST`
    - URL: `http://127.0.0.1:8000/users/`
    - Body (raw - JSON):
      ```json
      {
        "nama": "John Doe",
        "alamat": "Jl. Contoh No. 123",
        "telepon": "081234567890",
        "id_jabatan": 1
      }
      ```
      (Pastikan `id_jabatan` yang Anda gunakan valid dan ada di tabel `jabatan`).

4.  **Mendapatkan Daftar User:**

    - Metode: `GET`
    - URL: `http://127.0.0.1:8000/users/`

5.  **Mendapatkan Detail User:**

    - Metode: `GET`
    - URL: `http://127.0.0.1:8000/users/1` (ganti `1` dengan ID user)

6.  **Memperbarui User:**

    - Metode: `PUT`
    - URL: `http://127.0.0.1:8000/users/1` (ganti `1` dengan ID user)
    - Body (raw - JSON):
      ```json
      {
        "alamat": "Jl. Contoh Baru No. 456",
        "telepon": "089876543210",
        "id_jabatan": 2
      }
      ```
      (Field yang tidak disertakan dalam body tidak akan diubah).

7.  **Menghapus User:**
    - Metode: `DELETE`
    - URL: `http://127.0.0.1:8000/users/1` (ganti `1` dengan ID user)

## Lanjutan: Implementasi Fitur One-Time Password (OTP)

Bagian ini menjelaskan implementasi fitur One-Time Password (OTP) menggunakan Redis untuk penyimpanan dan verifikasi.

### 3.1 Endpoint untuk Generate OTP (`POST /otp/generate`)

```python
import random
from typing import Dict
from fastapi import FastAPI, Depends, HTTPException, Body
from redis import Redis
from redis_config import get_redis

# ... (kode-kode endpoint lain di main.py)

@app.post("/otp/generate", response_model=Dict[str, str])
async def generate_otp(id: int = Body(..., embed=True), redis_client: Redis = Depends(get_redis)):
    """Menghasilkan kode OTP untuk ID tertentu."""
    otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
    otp_key = f"otp:{id}"
    redis_client.setex(otp_key, 300, otp)  # Simpan OTP di Redis selama 5 menit (300 detik)
    attempts_key = f"otp:attempts:{id}"
    redis_client.delete(attempts_key)  # Reset jumlah percobaan gagal jika OTP baru digenerate
    return {"otp": otp}
```

- @app.post("/otp/generate", response_model=Dict[str, str]): Mendefinisikan endpoint HTTP POST di path /otp/generate. Endpoint ini mengharapkan input id melalui body request dan akan mengembalikan respons berupa dictionary JSON yang berisi kode OTP yang dihasilkan.

- async def generate_otp(id: int = Body(..., embed=True), redis_client: Redis = Depends(get_redis)):: Mendefinisikan fungsi asinkron untuk endpoint ini.

  - id: int = Body(..., embed=True): Mendeklarasikan parameter id yang diharapkan ada di body request. Body(...) menandakan bahwa field ini wajib ada. embed=True akan membuat body request berupa JSON dengan key id (contoh: {"id": 123}). Tipe datanya diharapkan integer (int).
  - redis_client: Redis = Depends(get_redis): Mendeklarasikan dependency redis_client. FastAPI akan secara otomatis memanggil fungsi get_redis untuk mendapatkan instance klien Redis yang sudah terkonfigurasi.

- otp = str(random.randint(100000, 999999)): Menghasilkan kode OTP acak 6 digit (antara 100000 dan 999999) dan mengonversinya menjadi string.

- otp_key = f"otp:{id}": Membuat key unik untuk menyimpan OTP di Redis. Key ini menggunakan format otp: diikuti dengan id yang diterima. Ini memastikan setiap ID memiliki OTP-nya sendiri.

- redis_client.setex(otp_key, 300, otp): Menyimpan kode OTP ke Redis dengan key otp:{id}. setex digunakan untuk menyimpan nilai dengan waktu kedaluwarsa. 300 adalah waktu kedaluwarsa dalam detik (5 menit), setelah itu Redis akan otomatis menghapus key ini.

- attempts_key = f"otp:attempts:{id}": Membuat key unik untuk menyimpan jumlah percobaan verifikasi yang gagal untuk id tertentu.
  redis_client.delete(attempts_key): Menghapus key yang menyimpan jumlah percobaan gagal untuk id jika OTP baru berhasil digenerate. Tujuannya adalah untuk mereset counter percobaan gagal setiap kali OTP baru diminta.
  return {"otp": otp}: Mengembalikan respons JSON yang berisi kode OTP yang baru dihasilkan dengan key otp.

### 3.2 Endpoint untuk Verifikasi OTP (POST /otp/verify)

```
@app.post("/otp/verify", response_model=Dict[str, str])
async def verify_otp(id: int = Body(..., embed=True), otp: str = Body(..., embed=True), redis_client: Redis = Depends(get_redis)):
    """Memverifikasi kode OTP untuk ID tertentu."""
    otp_key = f"otp:{id}"
    stored_otp = redis_client.get(otp_key)
    attempts_key = f"otp:attempts:{id}"
    attempts = redis_client.get(attempts_key)
    max_attempts = 3

    if stored_otp is None:
        raise HTTPException(status_code=404, detail="OTP tidak ditemukan atau sudah kedaluwarsa.")

    if attempts is not None and int(attempts) >= max_attempts:
        redis_client.delete(otp_key)  # Reset OTP setelah 3 kali gagal
        raise HTTPException(status_code=429, detail="Percobaan verifikasi OTP melebihi batas. OTP telah direset.")

    if stored_otp == otp:
        redis_client.delete(otp_key)  # Hapus OTP setelah verifikasi berhasil
        return {"message": "OTP berhasil diverifikasi.")
    else:
        redis_client.incr(attempts_key)  # Increment jumlah percobaan gagal
        raise HTTPException(status_code=400, detail="OTP wrong")
```

- @app.post("/otp/verify", response_model=Dict[str, str]): Mendefinisikan endpoint HTTP POST di path /otp/verify. Endpoint ini mengharapkan input id dan otp melalui body request dan akan mengembalikan respons berupa dictionary JSON yang berisi status verifikasi.

- async def verify_otp(id: int = Body(..., embed=True), otp: str = Body(..., embed=True), redis_client: Redis = Depends(get_redis)):: Mendefinisikan fungsi asinkron untuk endpoint ini.

  - id: int = Body(..., embed=True): Mendeklarasikan parameter id yang diharapkan ada di body request (integer).
  - otp: str = Body(..., embed=True): Mendeklarasikan parameter otp yang diharapkan ada di body request (string).
  - redis_client: Redis = Depends(get_redis): Mendapatkan instance klien Redis melalui dependency injection.

- otp_key = f"otp:{id}": Membuat key Redis untuk mengambil OTP yang tersimpan berdasarkan id. Harus sama dengan key saat menyimpan OTP.

- stored_otp = redis_client.get(otp_key): Mengambil nilai OTP yang tersimpan dari Redis berdasarkan key. Jika key tidak ada atau sudah kedaluwarsa, stored_otp akan bernilai None.

- attempts_key = f"otp:attempts:{id}": Membuat key Redis untuk menyimpan jumlah percobaan verifikasi gagal untuk id.

- attempts = redis_client.get(attempts_key): Mengambil jumlah percobaan gagal yang tersimpan dari Redis. Jika key tidak ada, attempts akan bernilai None.

- max_attempts = 3: Mendefinisikan konstanta max_attempts sebagai batas maksimum percobaan verifikasi yang diizinkan.

- if stored_otp is None:: Memeriksa apakah OTP tidak ditemukan di Redis. Jika ya, mengindikasikan bahwa OTP belum digenerate atau sudah kedaluwarsa, sehingga mengembalikan error HTTP 404 (Not Found) dengan pesan detail.

- if attempts is not None and int(attempts) >= max_attempts:: Memeriksa apakah jumlah percobaan gagal sudah mencapai atau melebihi batas maksimum.

- redis_client.delete(otp_key): Jika batas percobaan terlampaui, OTP di-reset (dihapus dari Redis) untuk alasan keamanan.

- raise HTTPException(status_code=429, detail="..."): Mengembalikan error HTTP 429 (Too Many Requests) dengan pesan detail bahwa percobaan verifikasi telah melebihi batas dan OTP telah direset.

- if stored_otp == otp:: Membandingkan OTP yang diterima dari request (otp) dengan OTP yang diambil dari Redis (stored_otp).

- redis_client.delete(otp_key): Jika OTP cocok, OTP dihapus dari Redis setelah verifikasi berhasil untuk mencegah penggunaan berulang.

- return {"message": "OTP berhasil diverifikasi."}: Mengembalikan respons JSON sukses.
  else:: Jika OTP yang diterima tidak cocok dengan yang tersimpan.
  redis_client.incr(attempts_key): Mengincrement (menambah 1) nilai counter percobaan gagal di Redis untuk id tersebut. Jika key attempts_key belum ada, Redis akan membuatnya dan menginisialisasinya dengan 1.
  raise HTTPException(status_code=400, detail="OTP wrong"): Mengembalikan error HTTP 400 (Bad Request) dengan pesan detail bahwa OTP yang dimasukkan salah.

### Cara Mengetes Endpoint OTP di Postman

1.  **Pastikan Server FastAPI Berjalan:**

    - Jalankan aplikasi FastAPI Anda menggunakan Uvicorn (misalnya, `uvicorn main:app --reload`).

2.  **Uji Endpoint Generate OTP (`/otp/generate`):**

    - **Metode:** `POST`
    - **URL:** `http://127.0.0.1:8000/otp/generate` (sesuaikan port jika perlu)
    - **Headers:** `Content-Type: application/json` (Postman akan menambahkannya secara otomatis saat Anda memilih format JSON di body)
    - **Body (raw - JSON):**
      ```json
      {
        "id": "user123"
      }
      ```
      - Ganti `"user123"` dengan ID yang ingin Anda tes. Jika endpoint Anda menerima `id` sebagai integer, gunakan:
      ```json
      {
        "id": 123
      }
      ```
    - **Kirim:** Klik tombol **"Send"**.
    - **Respons Sukses (Status 200 OK):**
      ```json
      {
        "otp": "123456"
      }
      ```
      - Catat nilai OTP yang diterima.
    - **Verifikasi di Redis (Opsional):** Gunakan Redis Insight untuk melihat key `otp:user123` (atau sesuai ID Anda) dan nilai OTP yang tersimpan. Periksa juga TTL (Time To Live).

3.  **Uji Endpoint Verifikasi OTP (`/otp/verify`):**

    - **Metode:** `POST`
    - **URL:** `http://127.0.0.1:8000/otp/verify` (sesuaikan port jika perlu)
    - **Headers:** `Content-Type: application/json` (Postman akan menambahkannya secara otomatis saat Anda memilih format JSON di body)
    - **Body (raw - JSON) - Verifikasi Berhasil:**
      ```json
      {
        "id": "user123",
        "otp": "123456"
      }
      ```
      - Ganti `"user123"` dengan ID yang sama seperti saat generate.
      - Ganti `"123456"` dengan OTP yang Anda terima dari respons generate.
    - **Kirim:** Klik tombol **"Send"**.
    - **Respons Sukses (Status 200 OK):**

      ```json
      {
        "message": "OTP berhasil diverifikasi."
      }
      ```

      - **Verifikasi di Redis (Opsional):** Periksa Redis Insight, key `otp:user123` seharusnya sudah hilang.

    - **Body (raw - JSON) - Verifikasi Gagal (OTP Salah):**

      ```json
      {
        "id": "user123",
        "otp": "wrongotp"
      }
      ```

      - Kirim request.
      - **Respons Gagal (Status 400 Bad Request):**

      ```json
      {
        "detail": "OTP wrong"
      }
      ```

      - **Verifikasi di Redis (Opsional):** Periksa key `otp:attempts:user123` di Redis Insight, nilainya akan bertambah.

    - **Body (raw - JSON) - Verifikasi Setelah Batas Percobaan Gagal:**
      - Lakukan beberapa kali percobaan verifikasi dengan OTP yang salah (misalnya, 3 kali).
      - Kemudian kirim request verifikasi lagi (dengan OTP yang benar atau salah):
      ```json
      {
        "id": "user123",
        "otp": "anyotp"
      }
      ```
      - **Respons Batas Terlampaui (Status 429 Too Many Requests):**
      ```json
      {
        "detail": "Percobaan verifikasi OTP melebihi batas. OTP telah direset."
      }
      ```
      - **Verifikasi di Redis (Opsional):** Periksa Redis Insight, key `otp:user123` seharusnya sudah hilang.

## Catatan

- Pastikan database PostgreSQL Anda berjalan dan konfigurasi di file `.env` sudah benar.
- Anda perlu membuat tabel `jabatan` dan `user` di database PostgreSQL Anda sesuai dengan definisi model di `models.py` sebelum menjalankan aplikasi. Anda bisa menggunakan alat seperti `psql` atau pgAdmin untuk membuat tabel. Contoh perintah SQL untuk membuat tabel:

  ```sql
  CREATE TABLE jabatan (
      id_jabatan SERIAL PRIMARY KEY,
      nama_jabatan VARCHAR(100),
      deskripsi TEXT
  );

  CREATE TABLE "user" (
      id_user SERIAL PRIMARY KEY,
      nama VARCHAR(255),
      alamat TEXT,
      telepon VARCHAR(20),
      id_jabatan INTEGER REFERENCES jabatan(id_jabatan)
  );
  ```
