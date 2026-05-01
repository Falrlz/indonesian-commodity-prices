import duckdb
import pandas as pd
from config.settings import DB_PATH


# =========================================================
# DATA LOADING → DATA WAREHOUSE (DUCKDB)
# =========================================================
def load_to_db(csv_path):
    """
    Memuat data CSV ke DuckDB dan membangun skema data warehouse (star schema).

    Args:
        csv_path (str): path ke file CSV hasil staging

    Output Tables:
        - dim_provinsi : dimensi provinsi
        - dim_variant  : dimensi komoditas/variant (+ unit)
        - dim_date     : dimensi waktu
        - fact_harga   : tabel fakta harga

    Processing Steps:
        1. Load & casting tipe data
        2. Data validation (drop null penting)
        3. Deduplication (granularitas: tanggal-provinsi-variant)
        4. Register ke DuckDB
        5. Build dimension & fact tables

    Notes:
        - Menggunakan CREATE OR REPLACE → overwrite tiap run
        - Skema mengikuti pendekatan star schema untuk analytics
    """
    con = duckdb.connect(DB_PATH)

    # ======================
    # LOAD & PREPROCESS
    # ======================
    df = pd.read_csv(csv_path)

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df["harga"] = pd.to_numeric(df["harga"], errors="coerce")
    df["harga_sebelumnya"] = pd.to_numeric(df.get("harga_sebelumnya"), errors="coerce")
    df["disparitas_pct"] = pd.to_numeric(df.get("disparitas_pct"), errors="coerce")

    # drop null penting (integritas fact table)
    df = df.dropna(subset=["tanggal", "kode_provinsi", "variant_id", "harga"])

    # dedup sesuai grain: 1 record per (tanggal, provinsi, variant)
    df = df.drop_duplicates(
        subset=["tanggal", "kode_provinsi", "variant_id"]
    )

    con.register("df", df)

    # ======================
    # DIMENSION: PROVINSI
    # ======================
    # 1 row per kode_provinsi
    con.execute("""
    CREATE OR REPLACE TABLE dim_provinsi AS
    SELECT
        kode_provinsi,
        ANY_VALUE(provinsi) AS provinsi
    FROM df
    GROUP BY kode_provinsi
    """)

    # ======================
    # DIMENSION: VARIANT
    # ======================
    # 1 row per variant_id
    # unit diturunkan dari nama komoditas (rule-based)
    con.execute("""
    CREATE OR REPLACE TABLE dim_variant AS
    SELECT
        variant_id,
        ANY_VALUE(variant_nama) AS variant_nama,
        ANY_VALUE(komoditas) AS komoditas,

        CASE 
            WHEN LOWER(ANY_VALUE(komoditas)) LIKE '%minyak%' THEN 'lt'
            ELSE 'kg'
        END AS unit

    FROM df
    GROUP BY variant_id
    """)

    # ======================
    # DIMENSION: DATE
    # ======================
    # date_id: surrogate key (YYYYMMDD)
    con.execute("""
    CREATE OR REPLACE TABLE dim_date AS
    SELECT DISTINCT
        CAST(strftime('%Y%m%d', tanggal) AS INTEGER) AS date_id,
        tanggal
    FROM df
    """)

    # ======================
    # FACT TABLE: HARGA
    # ======================
    # grain: (date_id, kode_provinsi, variant_id)
    con.execute("""
    CREATE OR REPLACE TABLE fact_harga AS
    SELECT
        CAST(strftime('%Y%m%d', tanggal) AS INTEGER) AS date_id,
        kode_provinsi,
        variant_id,
        harga,
        harga_sebelumnya,
        disparitas_pct
    FROM df
    """)

    con.close()