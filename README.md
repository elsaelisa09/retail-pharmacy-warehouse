# Retail Pharmacy Sales & Stock Data Warehouse

Proyek data engineering untuk mengolah catatan penjualan dan pergerakan stok satu apotek di Indonesia menjadi data warehouse, laporan SQL, dan hasil pemeriksaan kualitas yang dapat ditelusuri.

Pipeline batch menerima pilihan bulan melalui `--period YYYY-MM`. Pengujian data mencakup Januari, Februari, dan Maret 2023.

## Hasil pengujian

Jumlah baris berikut sesuai antara raw, staging, dan tabel fakta:

| Periode | Detail penjualan | Pergerakan stok |
|---|---:|---:|
| Januari 2023 | 19.813 | 21.598 |
| Februari 2023 | 18.485 | 20.134 |
| Maret 2023 | 21.287 | 23.550 |

- Dimensi produk berisi **2.081 kode unik** dari ketiga bulan.
- Dimensi kalender berisi **1.096 tanggal** untuk 2023-2025.
- Versi terbaru menjalankan **15 pemeriksaan kualitas**: 10 penjualan dan 5 stok.
- Pipeline terbaru Maret menyelesaikan delapan tahap dengan **13 PASS, 2 WARN, dan kode keluar 0**.
- Pemuatan ulang batch Maret mempertahankan jumlah baris dan tidak menambahkan kode produk yang sudah tersedia.

Januari memiliki 10.918 nomor faktur unik. Jumlah `TotalPrice` Januari sebesar 369.527.611 telah direkonsiliasi antara staging dan fakta. Nilai ini merupakan nilai penjualan tercatat, bukan laba.

## Dataset

Sumber: [IRPD: Indonesian Retail Pharmacy Sales and Stock Transaction Dataset](https://data.mendeley.com/datasets/w6zjtdjk9m/1).

Dataset publik mencakup catatan 2023-2025 dari satu apotek di Indonesia. Proyek menggunakan versi **raw** untuk membangun dan memeriksa proses transformasi.

- Lisensi dataset: **CC BY 4.0**.
- Kredit: Nugroho, D. P., Sudargo, E. R., Liong, E. C. E., dan Sutoyo, R. (2026), Mendeley Data, versi 1.
- DOI: **10.17632/w6zjtdjk9m.1**.

Dataset dan hasil pengolahan lokal diabaikan melalui `.gitignore` dan tidak disertakan dalam repository. Unduh dataset dari sumber untuk menjalankan proyek.

## Teknologi

Lingkungan yang digunakan dalam pengujian:

- Windows dan PowerShell.
- Python 3.10.14 melalui Miniconda.
- PostgreSQL 18.6.
- pandas, SQLAlchemy, psycopg, dan python-dotenv.
- Git dan GitHub untuk pengelolaan versi kode.

Versi paket Python tersedia pada `requirements.txt`.

## Arsitektur data

| Schema | Fungsi |
|---|---|
| `raw` | Menyimpan nilai sumber dan metadata batch |
| `staging` | Menyeragamkan tipe dan format data |
| `warehouse` | Menyimpan dimensi produk, dimensi tanggal, dan dua tabel fakta |
| `marts` | Menyediakan view laporan penjualan dan stok |
| `audit` | Menyimpan hasil pemeriksaan kualitas dan riwayat pipeline |

Tabel utama pada schema `warehouse`:

- `dim_product`: satu produk per `drug_code`.
- `dim_date`: kalender harian.
- `fact_sales`: satu detail penjualan dari sumber per baris; satu faktur dapat memiliki beberapa baris.
- `fact_stock_movements`: satu catatan pergerakan stok dari sumber per baris.

Identitas sumber pada staging dan fakta menggunakan kombinasi `source_file`, `source_period`, dan `source_row_number`.

## Alur pipeline

`run_pipeline.py` menjalankan delapan tahap:

1. Memuat ulang raw stok untuk bulan yang dipilih.
2. Memuat ulang raw penjualan untuk bulan yang dipilih.
3. Mentransformasikan raw menjadi staging.
4. Memeriksa penjualan antara raw dan staging.
5. Memeriksa konsistensi atribut dan menambahkan kode produk baru ke dimensi.
6. Memuat kedua tabel fakta.
7. Memeriksa penjualan antara staging dan fakta.
8. Memeriksa kualitas stok dan rekonsiliasi staging dengan fakta.

Dimensi produk mencakup seluruh data staging yang tersedia. Produk baru ditambahkan dengan mempertahankan `product_key` produk lama. Pembaruan atribut produk lama belum diimplementasikan.

Setiap tahap menggunakan transaksi tersendiri. Jika suatu tahap gagal, runner berhenti dan mencatat kegagalan; tahap sebelumnya yang sudah berhasil tetap tersimpan. Pemuatan kedua tabel staging berada dalam satu transaksi, demikian pula pemuatan kedua tabel fakta.

Pemuatan ulang mengganti batch dengan file dan periode yang sama. ID otomatis fakta dan waktu pemuatan dapat berubah; identitas sumber tetap menjadi acuan rekonsiliasi.

Runner menggunakan CSV bulanan yang sudah dibuat. Pembuatan CSV melalui `07_create_pilot.py` belum termasuk dalam delapan tahap tersebut.

## Pemeriksaan kualitas

### Penjualan: 10 pemeriksaan

Raw ke staging (9 pemeriksaan):

- Cakupan kunci baris antara raw dan staging.
- Kesamaan delapan nilai: quantity, unit price, discount amount, service fee, packaging fee, subtotal, additional fee, dan total price.

Staging ke fakta (1 pemeriksaan):

- `sales_staging_fact_reconciliation`: memeriksa baris yang hilang, berlebih, atau berbeda nilainya, termasuk waktu, nomor faktur, satuan, nilai numerik, serta pemetaan produk dan tanggal. Ketidaksesuaian menghasilkan FAIL; periode tanpa data menghasilkan NO_DATA.

View `audit.sales_fact_reconciliation` menyediakan ringkasan rekonsiliasi per periode. Script `21_run_sales_fact_quality_checks.py` memilih bulan dan menyimpan hasilnya ke tabel audit.

### Stok: 5 pemeriksaan

| Pemeriksaan | Tujuan | Status jika ditemukan masalah |
|---|---|---|
| `stock_continuity` | Membandingkan stok awal dengan saldo catatan sebelumnya | FAIL |
| `stock_timestamp_ambiguity` | Menandai timestamp sama dalam kelompok produk, gudang, dan satuan | WARN |
| `stock_monthly_balance` | Memeriksa saldo awal + masuk - keluar terhadap saldo terakhir | FAIL |
| `stock_negative_balance` | Menandai saldo awal atau akhir negatif | WARN |
| `stock_staging_fact_reconciliation` | Membandingkan kunci dan nilai stok serta pemetaan produk dan tanggal | FAIL |

Kesinambungan stok dihitung dari catatan yang tersedia, termasuk lintas bulan jika terdapat catatan sebelumnya.

### Status dan pencatatan

Hasil tersimpan pada `audit.data_quality_results`:

| Status | Makna dan tindakan |
|---|---|
| PASS | Tidak ditemukan masalah pada pemeriksaan tersebut |
| WARN | Temuan disimpan untuk ditinjau; audit stok mengizinkan proses berlanjut |
| FAIL | Ada kesalahan yang menghentikan proses |
| NO_DATA | Tidak ada data yang dapat diperiksa; proses dihentikan |

`issue_rows` mencatat kesalahan, sedangkan `warning_rows` mencatat peringatan. Hasil audit disimpan sebelum statusnya dievaluasi.

Riwayat pipeline tersimpan pada `audit.pipeline_runs`, dengan status `RUNNING`, `SUCCESS`, atau `FAILED`. `SUCCESS` menunjukkan eksekusi selesai sesuai aturan pemeriksaan; peringatan data tetap perlu ditinjau.

Run ID audit dan Pipeline Run ID merupakan identitas terpisah. Keduanya belum dihubungkan melalui foreign key. Catatan kegagalan sebelumnya tetap dipertahankan ketika pipeline dijalankan ulang.

## Temuan data

| Periode | Baris bertimestamp sama | Baris dengan saldo awal atau akhir negatif |
|---|---:|---:|
| Januari 2023 | 0 | 69 |
| Februari 2023 | 0 | 19 |
| Maret 2023 | 16 | 106 |

Enam belas baris bertimestamp sama pada Maret membentuk delapan pasangan yang ditinjau. Dalam setiap pasangan, nomor dokumennya berbeda dan saldonya berkesinambungan. Pengurutan menggunakan timestamp dan identitas sumber. Urutan ini konsisten dengan saldo yang ditampilkan, tetapi tidak membuktikan urutan waktu fisik transaksi.

Pada contoh produk `SW2106001997`, catatan raw menunjukkan penjualan 10 kapsul dari saldo awal 0 sehingga saldo akhirnya -10. Nilai sumber dipertahankan dan ditandai untuk ditinjau. Penyebab operasional saldo negatif belum dapat dipastikan dari pemeriksaan tersebut.

Angka di atas menghitung catatan pergerakan. Angka tersebut tidak menunjukkan jumlah produk yang stok fisiknya saat ini negatif. Satu baris dapat memicu beberapa pemeriksaan sehingga jumlah peringatan antar pemeriksaan tidak otomatis menunjukkan jumlah baris unik.

## Laporan SQL

| View | Kegunaan |
|---|---|
| `marts.daily_sales` | Ringkasan detail penjualan, faktur, produk, dan nilai penjualan tercatat per hari |
| `marts.monthly_sales` | Ringkasan bulanan, rata-rata nilai per faktur, dan perubahan nilai terhadap bulan sebelumnya |
| `marts.monthly_sales_daily_average` | Rata-rata nilai penjualan berdasarkan hari kalender dan hari yang memiliki catatan |
| `marts.monthly_stock_movements` | Ringkasan stok masuk, stok keluar, dan pergerakan bersih per bulan |
| `marts.monthly_stock_position` | Saldo awal tercatat, total pergerakan, saldo terakhir tercatat, dan selisih rekonsiliasi |

### Temuan penjualan Januari-Maret 2023

| Bulan | Nilai penjualan tercatat | Rata-rata per hari kalender | Rata-rata per hari dengan catatan |
|---|---:|---:|---:|
| Januari | 369.527.611 | 11.920.245,52 | 12.317.587,03 |
| Februari | 341.210.070 | 12.186.073,93 | 12.186.073,93 |
| Maret | 402.989.425 | 12.999.658,87 | 12.999.658,87 |

Total nilai Februari turun 7,66% dibanding Januari. Namun, rata-rata per hari kalender meningkat, sedangkan rata-rata per hari yang memiliki catatan sedikit menurun. Kedua ukuran memberikan konteks berbeda karena Januari memiliki 31 hari kalender dan 30 hari dengan catatan, sementara Februari memiliki 28 hari pada kedua ukuran.

Jumlah faktur Februari turun dari 10.918 menjadi 10.087, sementara rata-rata nilai per faktur hampir tetap, yaitu 33.845,72 menjadi 33.826,71.

Total nilai Maret meningkat 18,11% dibanding Februari. Maret juga memiliki rata-rata nilai harian tertinggi di antara ketiga bulan yang diuji.

Hari dengan catatan penjualan belum tentu sama dengan hari operasional. Penyebab tanggal tanpa catatan perlu dikonfirmasi sebelum menarik kesimpulan mengenai operasional apotek.

### Catatan penggunaan laporan

Laporan stok dikelompokkan berdasarkan produk, gudang, dan satuan. Kuantitas dengan satuan berbeda tidak dijumlahkan sebagai satu ukuran stok.

`last_recorded_stock` adalah saldo pada catatan terakhir yang tersedia, dengan waktu pada `last_movement_at`. Nilai tersebut bukan hasil verifikasi stok fisik.

Jumlah faktur unik pada laporan bulanan dihitung langsung dari fakta. Jumlah faktur unik harian tidak otomatis dapat dijumlahkan sebagai jumlah faktur unik suatu periode.

## Instalasi awal pada database baru

Bagian ini digunakan untuk menyiapkan proyek dari awal. Database yang sudah berjalan cukup menggunakan perintah pada bagian **Menjalankan pipeline**.

Jalankan seluruh perintah dari folder utama repository. Contoh menggunakan Miniconda dan lokasi instalasi PostgreSQL 18 di Windows; sesuaikan lokasi psql jika berbeda.

### 1. Siapkan environment Python

```powershell
conda create -n pharmacy-warehouse python=3.10.14
conda activate pharmacy-warehouse
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Sesuaikan konfigurasi database pada `.env`:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=retail_pharmacy_dw
DB_USER=postgres
```

Password diminta saat eksekusi jika environment variable `DB_PASSWORD` belum tersedia. Runner meneruskannya melalui environment proses anak. File `.env` diabaikan oleh Git.

### 2. Siapkan dataset bulanan

Unduh dan ekstrak dataset sehingga file sumber tersedia pada:

```text
Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025/raw_dataset/sales_raw.csv
Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025/raw_dataset/stock_raw.csv
```

Buat CSV untuk tiga bulan pengujian:

```powershell
python 07_create_pilot.py --period 2023-01
python 07_create_pilot.py --period 2023-02
python 07_create_pilot.py --period 2023-03
```

Hasil disimpan pada `data/pilot/YYYY-MM/`. Nilai sumber tetap dipertahankan; parsing tanggal pada tahap ini digunakan untuk memilih bulan.

### 3. Buat database dan schema

Dari PowerShell, masuk ke psql:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5432 -U postgres -d postgres -W
```

Jalankan di psql:

```text
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

Kedua script membuat tabel raw dan memuat pilot Januari untuk pertama kali. Jalankan sekali ketika tabel belum tersedia. Pemuatan berikutnya menggunakan script reload melalui runner.

### 5. Buat tabel dan view lainnya

Hubungkan ke database proyek dari PowerShell:

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
\i sql/27_check_sales_fact_reconciliation.sql
\i sql/16_build_daily_sales_mart.sql
\i sql/25_build_monthly_sales_mart.sql
\i sql/26_build_monthly_sales_daily_average.sql
\i sql/17_build_monthly_stock_mart.sql
\i sql/18_check_stock_continuity.sql
\i sql/19_build_monthly_stock_position.sql
\i sql/20_create_quality_audit.sql
\i sql/24_add_quality_warnings.sql
\i sql/23_create_pipeline_runs.sql
\q
```

Pada tahap ini staging dan fakta masih kosong. SQL 08 membuat tabel dimensi produk; produknya akan diisi oleh pipeline setelah staging dimuat.

SQL dengan placeholder seperti `:period_date` atau `:period_text` dijalankan melalui script Python yang memasok parameter. File tersebut tidak dijalankan langsung melalui `\i`.

### 6. Jalankan pipeline

Ikuti bagian berikut untuk memuat ketiga bulan secara berurutan.

## Menjalankan pipeline

Pada database yang sudah selesai diinisialisasi, jalankan dari PowerShell:

```powershell
python run_pipeline.py --period 2023-01
python run_pipeline.py --period 2023-02
python run_pipeline.py --period 2023-03
```

Jalankan satu per satu dan lanjutkan setelah eksekusi sebelumnya berhasil. Tanpa `--period`, nilai bawaan adalah `2023-01`.

Password dimasukkan sekali untuk setiap eksekusi runner. Periksa kode keluar segera setelah suatu eksekusi:

```powershell
Write-Host "Kode keluar pipeline: $LASTEXITCODE"
```

Kode 0 menunjukkan runner selesai. Hasil audit dapat tetap mengandung `WARN` yang perlu ditinjau.

### Memproses bulan berikutnya

Contoh penggunaan untuk April:

```powershell
python 07_create_pilot.py --period 2023-04
python run_pipeline.py --period 2023-04
```

Hasil data April belum diuji pada versi ini. Tinjau hasil setiap tahap sebelum melanjutkan bulan berikutnya.

## Pengujian yang telah dilakukan

- Data Januari, Februari, dan Maret 2023 telah dimuat melalui pipeline bulanan.
- Audit stok terbaru, termasuk peringatan saldo negatif, telah dijalankan untuk ketiga bulan.
- Pipeline Maret delapan tahap dengan aturan audit terbaru selesai dengan 13 PASS, 2 WARN, dan kode keluar 0.
- Rekonsiliasi penjualan staging ke fakta PASS untuk Januari (19.813 baris), Februari (18.485 baris), dan Maret (21.287 baris).
- Uji script rekonsiliasi untuk periode tanpa data, 2022-12, menghasilkan NO_DATA dan kode keluar 1. Uji ini menambahkan catatan audit tanpa mengubah data penjualan.
- Jumlah baris raw, staging, dan fakta sesuai untuk ketiga bulan.
- Dimensi bertambah dari 1.760 menjadi 1.961, kemudian 2.081 produk. Pada pemuatan awal Maret, runner menambahkan 120 produk secara otomatis.
- Pemuatan ulang dimensi tidak menambah kode yang sudah tersedia.
- Pada pilot Januari, simulasi file input hilang menghasilkan FAILED; setelah file dipulihkan, eksekusi kembali SUCCESS.
- Riwayat kegagalan tetap tersedia setelah pemulihan dan eksekusi ulang.

## Batasan dan pengembangan berikutnya

- Pengujian data baru mencakup Januari sampai Maret 2023; seluruh periode dataset belum diproses.
- Sejumlah SQL eksplorasi di luar runner masih menggunakan periode tetap.
- Pemeriksaan otomatis belum mencakup seluruh kolom sumber.
- Saldo negatif dan timestamp sama telah ditandai; penyebab operasionalnya belum seluruhnya terverifikasi.
- Dimensi produk belum menangani pembaruan atribut atau riwayat perubahan atribut.
- Transaksi berlaku per tahap, bukan untuk seluruh pipeline sekaligus. Data suatu bulan dapat sudah dimuat ketika audit akhir menghentikan runner.
- Penjadwalan, REST API, Docker, dan dashboard visual belum diimplementasikan. Pipeline dijalankan manual dan menggunakan data historis.
- Definisi bisnis seluruh diskon, pajak, dan biaya masih memerlukan validasi.
- Dataset tidak menyediakan biaya pembelian untuk menghitung laba.
- Posisi stok bulanan hanya mencakup kelompok yang memiliki pergerakan pada bulan tersebut.
