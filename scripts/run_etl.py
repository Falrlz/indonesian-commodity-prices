import logging

from etl.extract import get_komoditas, extract_variants
from etl.pipeline import run_extraction
from etl.transform import clean_data, standardize_data
from etl.load_db import load_to_db
from etl.build_mart import build_mart
from utils.io import save_csv
from config.settings import MAX_VARIANTS, STAGING_PATH

# =========================================================
# LOGGING CONFIGURATION
# =========================================================
logging.basicConfig(level=logging.INFO)


# =========================================================
# MAIN ETL ORCHESTRATION
# =========================================================
def main():
    """
    Entry point untuk menjalankan pipeline ETL end-to-end.

    Pipeline Flow:
        1. Extract:
           - Ambil master komoditas
           - Ekstrak variant_id
           - Fetch data harga (API)

        2. Transform:
           - Data cleaning (type casting, filtering, dedup)
           - Standardization (format konsisten)

        3. Load:
           - Simpan ke staging (CSV)
           - Load ke DuckDB (data warehouse)

        4. Data Mart:
           - Bangun tabel agregasi untuk analytics

    Configuration:
        - MAX_VARIANTS : limit data (debug/testing)
        - STAGING_PATH : lokasi penyimpanan sementara

    Output:
        - File CSV (staging layer)
        - Database DuckDB (dim + fact + mart)

    Logging:
        - INFO pada setiap tahap pipeline
    """

    # ======================
    # EXTRACT: MASTER DATA
    # ======================
    logging.info("GET KOMODITAS")
    df_komoditas = get_komoditas()

    logging.info("EXTRACT VARIANT")
    df_variant = extract_variants(df_komoditas)

    # ======================
    # EXTRACT: TRANSACTIONAL DATA
    # ======================
    logging.info("RUN EXTRACTION")
    df_raw = run_extraction(df_variant, max_variants=MAX_VARIANTS)

    # ======================
    # TRANSFORM
    # ======================
    logging.info("TRANSFORM")
    df_clean = clean_data(df_raw)
    df_clean = standardize_data(df_clean)

    # ======================
    # LOAD: STAGING
    # ======================
    # Single source of truth untuk downstream process
    save_csv(df_clean, STAGING_PATH)

    # ======================
    # LOAD: DATA WAREHOUSE
    # ======================
    logging.info("LOAD TO DB")
    load_to_db(STAGING_PATH)

    # ======================
    # BUILD DATA MART
    # ======================
    logging.info("BUILD MART")
    build_mart()

    logging.info("ETL DONE 🚀")


# =========================================================
# SCRIPT ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    main()