import pandas as pd
import time
import logging

from etl.extract import fetch_province_price
from config.settings import REQUEST_DELAY
from utils.date import generate_dates

logger = logging.getLogger(__name__)


# =========================================================
# EXTRACTION PIPELINE
# =========================================================
def run_extraction(df_variant, max_variants=None):
    """
    Menjalankan proses ekstraksi data harga per provinsi
    untuk setiap kombinasi variant_id dan tanggal.

    Args:
        df_variant (pd.DataFrame):
            kolom wajib:
            - variant_id
            - komoditas
        max_variants (int | None):
            - None → proses semua variant
            - int  → batasi jumlah variant (debug/testing)

    Returns:
        pd.DataFrame:
            hasil gabungan seluruh data hasil fetch
            (empty DataFrame jika tidak ada data)

    Process Flow:
        1. Loop tanggal (generate_dates)
        2. Loop variant_id
        3. Fetch data dari API
        4. Enrichment (tambah kolom komoditas)
        5. Append ke buffer (list)
        6. Concatenate hasil akhir

    Behavior:
        - Skip jika response None / empty
        - Menggunakan delay antar request (REQUEST_DELAY)
        - Logging progress setiap 50 variant

    Logging:
        - INFO  : progress per tanggal & batch
        - WARNING : jika tidak ada data sama sekali
        - INFO  : total rows hasil ekstraksi
    """
    all_data = []

    # limit variant untuk debugging / sampling
    if max_variants is not None:
        df_variant = df_variant.head(max_variants)

    total = len(df_variant)

    # ======================
    # LOOP: DATE × VARIANT
    # ======================
    for tanggal in generate_dates():
        logger.info(f"[DATE] {tanggal}")

        for i, (_, row) in enumerate(df_variant.iterrows(), 1):
            df = fetch_province_price(row["variant_id"], tanggal)

            if df is None or df.empty:
                continue

            # enrichment metadata
            df["komoditas"] = row["komoditas"]
            all_data.append(df)

            # progress logging (batch-wise)
            if i % 50 == 0:
                logger.info(f"Progress: {i}/{total}")

            # rate limiting
            time.sleep(REQUEST_DELAY)

    # ======================
    # FINALIZE RESULT
    # ======================
    if not all_data:
        logger.warning("No data extracted")
        return pd.DataFrame()

    result = pd.concat(all_data, ignore_index=True)

    logger.info(f"Total rows extracted: {len(result)}")

    return result