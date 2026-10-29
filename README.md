# Retail Pharmacy Sales & Stock Data Warehouse

Proyek data engineering untuk mengolah catatan penjualan dan pergerakan stok apotek Indonesia menjadi data warehouse, laporan SQL, dan pemeriksaan kualitas yang dapat ditelusuri.

Pipeline batch menerima pilihan bulan melalui `--period YYYY-MM`. Pengujian saat ini mencakup Januari dan Februari 2023.

## Dataset

Sumber: [IRPD: Indonesian Retail Pharmacy Sales and Stock Transaction Dataset](https://data.mendeley.com/datasets/w6zjtdjk9m/1).

Dataset publik mencakup catatan 2023-2025 dari satu apotek di Indonesia. Proyek menggunakan versi raw untuk membangun dan memeriksa proses transformasi.

Lisensi dataset: **CC BY 4.0**.

Kredit: Nugroho, D. P., Sudargo, E. R., Liong, E. C. E., dan Sutoyo, R. (2026), Mendeley Data, versi 1. DOI: **10.17632/w6zjtdjk9m.1**.

Dataset dan hasil pengolahan lokal tidak disertakan dalam repository.

## Hasil yang sudah diuji

Jumlah berikut cocok antara raw, staging, dan fakta:

| Periode | Detail penjualan | Pergerakan stok |
|---|---:|---:|
| Januari 2023 | 19.813 | 21.598 |
| Februari 2023 | 18.485 | 20.134 |
| Maret 2023 | 21.287 | 23.550 |

- Dimensi produk: 2.081 kode unik dari ketiga bulan.
- Dimensi kalender: 1.096 tanggal untuk 2023-2025.
- Pemeriksaan kualitas: 14 pemeriksaan per eksekusi pipeline.
- Pipeline berhasil dijalankan untuk Januari, Februari, dan Maret.
- Eksekusi terbaru Maret selesai dengan 12 PASS dan 2 WARN serta kode keluar 0.

Januari memiliki 10.918 nomor faktur unik. Jumlah `TotalPrice` Januari sebesar 369.527.611 telah direkonsiliasi antara staging dan fakta. Nilai ini merupakan nilai penjualan tercatat, bukan laba.

## Arsitektur

| Schema | Fungsi |
|---|---|
| `raw` | Nilai sumber dan metadata batch |
| `staging` | Data dengan tipe dan format yang diseragamkan |
| `warehouse` | Dimensi produk, dimensi tanggal, dan dua tabel fakta |
| `marts` | View laporan penjualan dan stok |
| `audit` | Hasil pemeriksaan kualitas dan riwayat pipeline |

Identitas sumber pada tabel fakta menggunakan kombinasi file, periode, dan nomor baris.

Satu baris fakta penjualan merepresentasikan detail penjualan dari sumber, bukan satu faktur. Satu baris fakta stok merepresentasikan satu catatan pergerakan stok.

## Alur pipeline

`run_pipeline.py` menjalankan tujuh tahap:

1. Memuat ulang raw stok untuk bulan yang dipilih.
2. Memuat ulang raw penjualan untuk bulan yang dipilih.
3. Mentransformasikan raw menjadi staging.
4. Memeriksa penjualan antara raw dan staging.
5. Memeriksa konsistensi atribut dan menambahkan produk baru ke dimensi.
6. Memuat kedua tabel fakta.
7. Memeriksa kualitas stok dan rekonsiliasi staging dengan fakta.

Dimensi produk mencakup seluruh data staging yang tersedia. Penambahan kode produk mempertahankan `product_key` produk yang sudah ada. Pembaruan atribut produk lama belum diimplementasikan.

Setiap tahap memiliki transaksi tersendiri. Jika suatu tahap gagal, runner berhenti dan mencatat kegagalan. Tahap sebelumnya yang sudah berhasil tetap tersimpan.

Pemuatan ulang mengganti batch dengan file dan periode yang sama. ID otomatis fakta dan waktu pemuatan dapat berubah.

## Laporan SQL

- `marts.daily_sales`
- `marts.monthly_stock_movements`
- `marts.monthly_stock_position`

Laporan stok dikelompokkan berdasarkan produk, gudang, dan satuan.

`last_recorded_stock` adalah saldo pada catatan terakhir yang tersedia, dengan waktu pada `last_movement_at`. Nilai tersebut bukan hasil verifikasi stok fisik.

## Teknologi

Lingkungan yang digunakan:

- Windows dan PowerShell
- Python 3.10.14
- PostgreSQL 18.6
- pandas, SQLAlchemy, psycopg, dan python-dotenv

Versi paket tersedia pada `requirements.txt`.

## Instalasi awal pada database baru

Jalankan perintah dari folder utama repository.

### 1. Siapkan environment

Contoh menggunakan Miniconda:

```powershell
conda create -n pharmacy-warehouse python=3.10.14
conda activate pharmacy-warehouse
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Sesuaikan konfigurasi database pada `.env`.

Password diminta saat eksekusi jika environment variable `DB_PASSWORD` belum tersedia. Runner meneruskannya melalui environment proses anak.

### 2. Siapkan dataset bulanan

Unduh dan ekstrak dataset sehingga file sumber berada pada:

```text
Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025/raw_dataset/sales_raw.csv
Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025/raw_dataset/stock_raw.csv
```

Buat CSV untuk dua bulan pengujian:

```powershell
python 07_create_pilot.py --period 2023-01
python 07_create_pilot.py --period 2023-02
```

Hasil disimpan pada `data/pilot/YYYY-MM/`.

### 3. Buat database dan schema

Contoh lokasi psql untuk PostgreSQL 18 di Windows:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5432 -U postgres -d postgres -W
```

Jalankan di psql:

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

### 4. Inisialisasi tabel raw

Dari PowerShell:

```powershell
python 12_load_raw_stock.py
python 13_load_raw_sales.py
```

Kedua script membuat tabel raw dan memuat pilot Januari untuk pertama kali. Jalankan sekali ketika tabel belum tersedia.

Eksekusi berikutnya menggunakan script reload melalui runner.

### 5. Buat tabel dan view lainnya

Hubungkan ke database proyek:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5432 -U postgres -d retail_pharmacy_dw -W
```

Jalankan urutan berikut di psql:

```text
\i sql/01_create_staging_stock.sql
\i sql/03_create_staging_sales.sql
\i sql/08_build_dim_product.sql
\i sql/09_build_dim_date.sql
\i sql/10_create_fact_sales.sql
\i sql/13_create_fact_stock.sql
\i sql/16_build_daily_sales_mart.sql
\i sql/17_build_monthly_stock_mart.sql
\i sql/18_check_stock_continuity.sql
\i sql/19_build_monthly_stock_position.sql
\i sql/20_create_quality_audit.sql
\i sql/23_create_pipeline_runs.sql
\q
```

Pada tahap ini staging dan fakta masih kosong. SQL 08 membuat tabel dimensi produk; produknya akan diisi oleh pipeline setelah staging dimuat.

SQL yang menggunakan placeholder seperti `:period_date` atau `:period_text` dijalankan melalui script Python yang memasok parameter, bukan langsung melalui `\i`.

### 6. Jalankan pipeline

Dari PowerShell:

```powershell
python run_pipeline.py --period 2023-01
python run_pipeline.py --period 2023-02
```

Jalankan perintah kedua setelah perintah pertama berhasil.

Tanpa `--period`, nilai bawaan adalah `2023-01`.

Runner menggunakan CSV bulanan yang sudah dibuat. Pembuatan CSV belum menjadi bagian dari tujuh tahap runner.

## Memproses bulan berikutnya

Contoh untuk Maret:

```powershell
python 07_create_pilot.py --period 2023-03
python run_pipeline.py --period 2023-03
```

Contoh tersebut menunjukkan cara penggunaan. Hasil data Maret belum diuji pada versi ini.

## Pemeriksaan kualitas

### Penjualan: 9 pemeriksaan

- Cakupan kunci baris antara raw dan staging.
- Kesamaan quantity, unit price, discount amount, service fee, packaging fee, subtotal, additional fee, dan total price.

### Stok: 4 pemeriksaan

- Kesinambungan saldo antarcatatan, termasuk lintas bulan jika catatan sebelumnya tersedia.
- Waktu pencatatan sama dalam kelompok produk, gudang, dan satuan.
- Rekonsiliasi saldo bulanan.
- Rekonsiliasi kunci dan nilai stok antara staging dan fakta, termasuk pemetaan produk dan tanggal.

Hasil tersimpan pada `audit.data_quality_results`. Status pemeriksaan dapat berupa PASS, FAIL, atau NO_DATA. Runner menghentikan proses jika script audit tidak berhasil.

Riwayat pipeline tersimpan pada `audit.pipeline_runs` dengan status RUNNING, SUCCESS, atau FAILED. Run ID audit dan Pipeline Run ID merupakan identitas terpisah.

### Stok: 5 pemeriksaan

- Kesinambungan saldo antarcatatan, termasuk lintas bulan jika catatan sebelumnya tersedia.
- Timestamp sama dalam kelompok produk, gudang, dan satuan.
- Rekonsiliasi saldo bulanan.
- Saldo awal atau akhir negatif.
- Rekonsiliasi kunci dan nilai stok antara staging dan fakta, termasuk pemetaan produk dan tanggal.

Hasil tersimpan pada `audit.data_quality_results`.

| Status | Makna dan tindakan |
|---|---|
| PASS | Tidak ditemukan masalah pada pemeriksaan tersebut |
| WARN | Temuan disimpan untuk ditinjau; proses dapat berlanjut |
| FAIL | Ditemukan kesalahan yang menghentikan proses |
| NO_DATA | Tidak ada data yang dapat diperiksa; proses dihentikan |

`issue_rows` mencatat kesalahan, sedangkan `warning_rows` mencatat peringatan.

### Temuan data

| Periode | Baris bertimestamp sama | Baris dengan saldo awal atau akhir negatif |
|---|---:|---:|
| Januari 2023 | 0 | 69 |
| Februari 2023 | 0 | 19 |
| Maret 2023 | 16 | 106 |

Catatan bertimestamp sama yang ditinjau memiliki nomor dokumen berbeda dan saldo berkesinambungan. Pengurutan memakai timestamp dan identitas sumber.

Pada contoh produk SW2106001997, saldo -10 juga ditemukan pada raw. Nilai sumber dipertahankan dan ditandai untuk ditinjau.

Satu baris dapat memicu beberapa pemeriksaan. Jumlah peringatan antar pemeriksaan tidak otomatis menunjukkan jumlah baris unik.

Riwayat pipeline tersimpan pada `audit.pipeline_runs` dengan status RUNNING, SUCCESS, atau FAILED. SUCCESS menunjukkan eksekusi selesai sesuai aturan pemeriksaan; peringatan data tetap perlu ditinjau.

Run ID audit dan Pipeline Run ID merupakan identitas terpisah.

## Batasan

- Pengujian data baru mencakup Januari dan Februari 2023.
- Sejumlah SQL eksplorasi di luar runner masih menggunakan periode tetap.
- Pemeriksaan otomatis penjualan mencakup raw ke staging; rekonsiliasi seluruh nilai penjualan staging ke fakta belum menjadi pemeriksaan otomatis.
- Pemeriksaan otomatis belum mencakup seluruh kolom sumber.
- Dimensi produk belum menangani pembaruan atribut atau riwayat perubahan atribut.
- Transaksi berlaku per tahap, bukan untuk seluruh pipeline sekaligus.
- Penjadwalan, REST API, Docker, dan dashboard visual belum diimplementasikan.
- Definisi bisnis seluruh diskon, pajak, dan biaya masih memerlukan validasi.
- Dataset tidak menyediakan biaya pembelian untuk menghitung laba.
- Posisi stok bulanan hanya mencakup kelompok yang memiliki pergerakan pada bulan tersebut.