import requests
import pandas as pd
import logging
import time

from config.settings import BASE_URL_KOMODITAS, BASE_URL_PROV, HEADERS

logger = logging.getLogger(__name__)

# =========================================================
# HTTP SESSION CONFIGURATION
# =========================================================
# Reusable session untuk:
# - Connection pooling (lebih efisien)
# - Reuse headers (auth + browser simulation)
session = requests.Session()
session.headers.update(HEADERS)


# =========================================================
# DATA FETCHING - KOMODITAS
# =========================================================
def get_komoditas():
    """
    Mengambil master data komoditas dari API.

    Returns:
        pd.DataFrame: daftar komoditas beserta metadata (termasuk variants)

    Behavior:
        - Mengambil seluruh data (limit besar)
        - Hanya komoditas aktif
        - Raise exception jika request gagal (non-200)

    Notes:
        - Field 'variants' berisi nested list untuk tiap komoditas
    """
    params = {
        "take": 1000000000,
        "tipe_komoditas_id": 1,
        "is_active": "true"
    }

    res = session.get(BASE_URL_KOMODITAS, params=params)
    res.raise_for_status()

    return pd.DataFrame(res.json().get("data", []))


# =========================================================
# TRANSFORMATION - VARIANT EXTRACTION
# =========================================================
def extract_variants(df_komoditas):
    """
    Mengekstrak variant_id dari struktur nested komoditas.

    Args:
        df_komoditas (pd.DataFrame): hasil dari get_komoditas()

    Returns:
        pd.DataFrame:
            kolom:
            - variant_id
            - komoditas (nama)

    Behavior:
        - Flatten field 'variants' (list → row-wise)
        - Skip jika format tidak valid
    """
    records = []

    for _, row in df_komoditas.iterrows():
        variants = row.get("variants", [])
        nama = row.get("nama")

        if not isinstance(variants, list):
            continue

        for v in variants:
            records.append({
                "variant_id": v.get("id"),
                "komoditas": nama
            })

    return pd.DataFrame(records)


# =========================================================
# DATA FETCHING - PROVINCE PRICE
# =========================================================
def fetch_province_price(variant_id, tanggal, retries=3):
    """
    Mengambil data harga komoditas per provinsi berdasarkan variant & tanggal.

    Args:
        variant_id (int | str): ID varian komoditas
        tanggal (str): format YYYY-MM-DD
        retries (int): jumlah percobaan ulang jika gagal

    Returns:
        pd.DataFrame | None:
            - DataFrame jika data tersedia
            - None jika tidak ada data / gagal total

    Behavior:
        - Retry mechanism untuk robustness (network/API instability)
        - Skip jika response kosong
        - Transform response menjadi tabular format

    Output Columns:
        - provinsi
        - harga (dari API)
        - variant_id
        - variant_nama
        - tanggal

    Logging:
        - WARNING saat retry gagal
        - ERROR jika semua percobaan gagal
    """
    params = {
        "variant_id": variant_id,
        "tanggal": tanggal
    }

    for attempt in range(retries):
        try:
            res = session.get(BASE_URL_PROV, params=params)

            if res.status_code != 200:
                time.sleep(1)
                continue

            data = res.json().get("data")
            if not data:
                return None

            items = data.get("items", [])
            if not items:
                return None

            df = pd.DataFrame(items)

            df["variant_id"] = data.get("variant_id")
            df["variant_nama"] = data.get("variant_nama")
            df["tanggal"] = data.get("tanggal")

            df.rename(columns={"nama_provinsi": "provinsi"}, inplace=True)

            return df

        except Exception as e:
            logger.warning(f"Retry {attempt+1} failed for {variant_id}")
            time.sleep(1)

    logger.error(f"Failed completely for {variant_id}")
    return None