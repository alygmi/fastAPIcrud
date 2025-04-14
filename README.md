# FastAPI CRUD API dengan PostgreSQL untuk User dan Jabatan

Proyek ini adalah implementasi sederhana dari API CRUD (Create, Read, Update, Delete) menggunakan framework FastAPI dan database PostgreSQL. API ini mengelola data User dan Jabatan.

## Struktur Proyek

my_project/
├── database.py # Konfigurasi koneksi database PostgreSQL dengan SQLAlchemy
├── main.py # Definisi aplikasi FastAPI dan semua endpoint API
├── models.py # Definisi model database SQLAlchemy (tabel dan relasi)
├── schemas.py # Definisi skema data Pydantic untuk validasi dan serialisasi
└── .env # File untuk menyimpan variabel lingkungan (misalnya, URL database)

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
