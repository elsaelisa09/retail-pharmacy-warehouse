# Retail Pharmacy Sales & Stock Data Warehouse

Proyek data engineering untuk mengolah catatan penjualan dan pergerakan stok apotek Indonesia menjadi data warehouse, laporan SQL, dan hasil pemeriksaan kualitas yang dapat ditelusuri.

Versi saat ini merupakan pipeline batch untuk **pilot Januari 2023**.

## Dataset

Sumber: [IRPD: Indonesian Retail Pharmacy Sales and Stock Transaction Dataset](https://data.mendeley.com/datasets/w6zjtdjk9m/1).

Dataset publik mencakup catatan tahun 2023–2025 dari satu apotek. Proyek menggunakan versi raw agar proses transformasinya dapat dibangun dan diperiksa.

Dataset berlisensi **CC BY 4.0**. Kredit dataset: Nugroho, D. P., Sudargo, E. R., Liong, E. C. E., dan Sutoyo, R. (2026), Mendeley Data, versi 1. DOI: **10.17632/w6zjtdjk9m.1**.

Dataset dan hasil pengolahan lokal diabaikan melalui `.gitignore`.

## Hasil pilot

| Komponen | Jumlah |
|---|---:|
| Detail penjualan | 19.813 |
| Nomor faktur unik | 10.918 |
| Pergerakan stok | 21.598 |
| Produk pada dimensi produk | 1.760 |
| Tanggal pada dimensi kalender 2023–2025 | 1.096 |
| Pemeriksaan kualitas otomatis | 12 |

Jumlah `TotalPrice` penjualan Januari 2023 sebesar **369.527.611** berhasil direkonsiliasi antara staging dan fakta.

## Arsitektur

| Schema | Fungsi |
|---|---|
| `raw` | Nilai sumber dan metadata batch |
| `staging` | Data dengan tipe dan format yang diseragamkan |
| `warehouse` | Dimensi produk, dimensi tanggal, dan dua tabel fakta |
| `marts` | View laporan penjualan dan stok |
| `audit` | Pemeriksaan kualitas dan riwayat eksekusi pipeline |

Tabel fakta mempertahankan identitas sumber melalui kombinasi file, periode, dan nomor baris.

## Alur pipeline

`run_pipeline.py` menjalankan enam tahap:

1. Memuat ulang raw stok.
2. Memuat ulang raw penjualan.
3. Mentransformasikan raw menjadi staging.
4. Memeriksa kualitas penjualan antara raw dan staging.
5. Memuat kedua tabel fakta.
6. Memeriksa kualitas stok.

Setiap tahap menggunakan transaksi tersendiri. Jika suatu tahap gagal, runner berhenti dan mencatat tahap tersebut. Tahap sebelumnya yang sudah berhasil tetap tersimpan.

Pemuatan ulang mengganti batch file dan periode yang sama. Jumlah baris dan identitas sumber tetap konsisten; ID otomatis fakta serta waktu pemuatan dapat berubah.

## Laporan yang tersedia

- `marts.daily_sales`
- `marts.monthly_stock_movements`
- `marts.monthly_stock_position`

Laporan stok dipisahkan berdasarkan produk, gudang, dan satuan.

`last_recorded_stock` merupakan saldo pada catatan terakhir yang tersedia. Waktu pencatatannya tersedia pada `last_movement_at`.

## Teknologi

Lingkungan pengujian:

- Windows dan PowerShell
- Python 3.10.14
- PostgreSQL 18.6
- pandas, SQLAlchemy, psycopg, dan python-dotenv

Versi paket tercantum di `requirements.txt`.

## Instalasi awal

Jalankan perintah dari folder utama repository.

### 1. Siapkan Python

Contoh menggunakan Miniconda:

```powershell
conda create -n pharmacy-warehouse python=3.10.14
conda activate pharmacy-warehouse
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Sesuaikan konfigurasi database di `.env`. Runner meminta password saat dijalankan jika environment variable `DB_PASSWORD` belum tersedia.

### 2. Siapkan dataset

Unduh dan ekstrak dataset sehingga kedua file tersedia pada lokasi berikut:

```text
Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025/raw_dataset/sales_raw.csv
Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025/raw_dataset/stock_raw.csv
```

Buat salinan pilot:

```powershell
python 07_create_pilot.py
```

### 3. Buat database dan schema

Contoh koneksi memakai lokasi instalasi standar PostgreSQL 18 di Windows:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5432 -U postgres -d postgres -W
```

Di dalam `psql`:

```sql
CREATE DATABASE retail_pharmacy_dw;
\connect retail_pharmacy_dw

CREATE SCHEMA raw;
CREATE SCHEMA staging;
CREATE SCHEMA warehouse;
CREATE SCHEMA marts;
CREATE SCHEMA audit;

\q
```

### 4. Muat raw untuk pertama kali

```powershell
python 12_load_raw_stock.py
python 13_load_raw_sales.py
```

Kedua script ini digunakan untuk inisialisasi tabel raw.

### 5. Inisialisasi staging, warehouse, laporan, dan audit

Hubungkan kembali ke database proyek:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5432 -U postgres -d retail_pharmacy_dw -W
```

Jalankan urutan berikut di dalam `psql`:

```text
\i sql/01_create_staging_stock.sql
\i sql/02_load_staging_stock.sql
\i sql/03_create_staging_sales.sql
\i sql/04_load_staging_sales.sql
\i sql/08_build_dim_product.sql
\i sql/09_build_dim_date.sql
\i sql/10_create_fact_sales.sql
\i sql/12_load_fact_sales.sql
\i sql/13_create_fact_stock.sql
\i sql/14_load_fact_stock.sql
\i sql/16_build_daily_sales_mart.sql
\i sql/17_build_monthly_stock_mart.sql
\i sql/18_check_stock_continuity.sql
\i sql/19_build_monthly_stock_position.sql
\i sql/20_create_quality_audit.sql
\i sql/23_create_pipeline_runs.sql
\q
```

Urutan ini digunakan sekali pada database baru.

## Menjalankan pipeline

Setelah instalasi awal selesai:

```powershell
python run_pipeline.py
```

Password dimasukkan sekali dan diteruskan melalui environment proses anak.

Hasil akhir yang diharapkan:

```text
PIPELINE PILOT BERHASIL: status SUCCESS tersimpan.
```

## Pemeriksaan kualitas

### Penjualan: 9 pemeriksaan

- Kelengkapan identitas baris raw–staging.
- Kesesuaian quantity, unit price, discount amount, service fee, packaging fee, subtotal, additional fee, dan total price.

### Stok: 3 pemeriksaan

- Kesinambungan saldo antarcatatan.
- Waktu pencatatan yang sama dalam kelompok produk, gudang, dan satuan.
- Rekonsiliasi saldo bulanan.

Hasil tersimpan pada `audit.data_quality_results`.

Riwayat eksekusi pipeline tersimpan pada `audit.pipeline_runs`, dengan status `RUNNING`, `SUCCESS`, atau `FAILED`.

## Pengujian yang sudah dilakukan

- Pemuatan ulang raw, staging, dan fakta tanpa pertambahan duplikasi pada identitas sumber.
- Rekonsiliasi jumlah baris dan nilai antar lapisan.
- Pemeriksaan kesinambungan saldo stok.
- Simulasi file input hilang: pipeline berhenti dan mencatat `FAILED`.
- Pemulihan file input: pipeline kembali mencatat `SUCCESS`.

## Batasan versi saat ini

- Pemrosesan masih khusus Januari 2023; sejumlah script SQL menggunakan periode tetap.
- Dimensi produk dibentuk dari produk pada pilot tersebut.
- Penjadwalan, REST API, Docker, dan dashboard visual belum diimplementasikan.
- Pemeriksaan otomatis penjualan saat ini mencakup raw–staging.
- Definisi bisnis total setelah seluruh diskon, pajak, dan biaya masih memerlukan validasi.
- Dataset tidak menyediakan biaya pembelian untuk perhitungan laba.
- Posisi stok bulanan mencakup kelompok yang memiliki pergerakan pada bulan tersebut.