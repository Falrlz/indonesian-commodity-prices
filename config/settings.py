import os
from dotenv import load_dotenv

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================
# Memuat konfigurasi dari file .env ke environment runtime
load_dotenv()


# =========================================================
# API ENDPOINT CONFIGURATION
# =========================================================
# Endpoint untuk:
# - Perbandingan harga antar provinsi
# - Master data komoditas
BASE_URL_PROV = "https://api-sp2kp.kemendag.go.id/report/api/average-price/province-comparison"
BASE_URL_KOMODITAS = "https://api-sp2kp.kemendag.go.id/master/api/komoditas"


# =========================================================
# HTTP REQUEST HEADERS
# =========================================================
# Digunakan untuk:
# - Simulasi request dari browser (hindari blocking)
# - Autentikasi menggunakan cookie dari .env
#
# NOTE:
# - COOKIE wajib valid (cek jika terjadi 401/403)
# - User-Agent dapat disesuaikan jika diperlukan
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://sp2kp.kemendag.go.id/",
    "Origin": "https://sp2kp.kemendag.go.id",
    "Cookie": os.getenv("COOKIE")
}


# =========================================================
# DATE RANGE CONFIGURATION
# =========================================================
# Rentang tanggal pengambilan data (format: YYYY-MM-DD)
START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")


# =========================================================
# SCRAPING CONTROL
# =========================================================
# Delay antar request (detik) untuk menghindari:
# - Rate limiting
# - Server blocking
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", 0.3))


# =========================================================
# DEBUG / SAMPLING CONFIGURATION
# =========================================================
# Membatasi jumlah data untuk testing/debugging
# - None  : ambil seluruh data
# - int   : batasi jumlah variasi
MAX_VARIANTS = os.getenv("MAX_VARIANTS")
MAX_VARIANTS = int(MAX_VARIANTS) if MAX_VARIANTS else None


# =========================================================
# STORAGE CONFIGURATION
# =========================================================
# Path penyimpanan:
# - STAGING_PATH : hasil sementara (CSV)
# - DB_PATH      : database utama (DuckDB)
STAGING_PATH = os.getenv("STAGING_PATH")
DB_PATH = os.getenv("DB_PATH")