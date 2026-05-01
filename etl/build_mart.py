import duckdb
from config.settings import DB_PATH


# =========================================================
# DATA MART BUILDER
# =========================================================
def build_mart():
    """
    Membangun data mart berbasis agregasi dari fact_harga.

    Source:
        - fact_harga (table utama / granular)

    Output Tables:
        - mart_harga_nasional : agregasi harga rata-rata tingkat nasional
        - mart_harga_provinsi : agregasi harga rata-rata per provinsi

    Aggregation Logic:
        - metric utama: AVG(harga)
        - berbasis grain tertentu (lihat masing-masing mart)

    Notes:
        - Menggunakan CREATE OR REPLACE → overwrite tiap eksekusi
        - Ditujukan untuk kebutuhan analytics & dashboard (read-optimized)
    """
    con = duckdb.connect(DB_PATH)

    # ======================
    # MART: NASIONAL
    # ======================
    # grain: (date_id, variant_id)
    # merepresentasikan harga rata-rata nasional per hari
    con.execute("""
    CREATE OR REPLACE TABLE mart_harga_nasional AS
    SELECT
        date_id,
        variant_id,
        AVG(harga) AS harga_avg
    FROM fact_harga
    GROUP BY 1,2
    """)

    # ======================
    # MART: PROVINSI
    # ======================
    # grain: (date_id, kode_provinsi, variant_id)
    # merepresentasikan harga rata-rata per provinsi per hari
    con.execute("""
    CREATE OR REPLACE TABLE mart_harga_provinsi AS
    SELECT
        date_id,
        kode_provinsi,
        variant_id,
        AVG(harga) AS harga_avg
    FROM fact_harga
    GROUP BY 1,2,3
    """)

    con.close()