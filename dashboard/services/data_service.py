import duckdb
import json
import streamlit as st

DB_PATH = "data/db/komoditas.duckdb"
GEO_PATH = "data/geo/indonesia-38-provinces.geojson"


# =========================================================
# CONNECTION & RESOURCE MANAGEMENT
# =========================================================
@st.cache_resource
def get_connection():
    """
    Membuat dan meng-cache koneksi DuckDB.

    Returns:
        duckdb.DuckDBPyConnection

    Behavior:
        - Singleton per session (efisien untuk query berulang)
        - Menghindari overhead koneksi berulang di Streamlit
    """
    return duckdb.connect(DB_PATH)


# =========================================================
# STATIC DATA LOADER
# =========================================================
@st.cache_data
def load_geo():
    """
    Memuat file GeoJSON untuk visualisasi peta.

    Returns:
        dict: struktur GeoJSON

    Notes:
        - Digunakan untuk choropleth mapping
        - Cache untuk menghindari reload file besar
    """
    return json.load(open(GEO_PATH, encoding="utf-8"))


@st.cache_data
def load_master():
    """
    Memuat data master dari data warehouse.

    Returns:
        tuple:
            - variants (pd.DataFrame) : dim_variant
            - dates (pd.DataFrame)    : dim_date
            - prov (pd.DataFrame)     : dim_provinsi

    Use Case:
        - Populate dropdown/filter UI
        - Lookup metadata (nama, unit, dll)
    """
    con = get_connection()

    variants = con.execute("SELECT * FROM dim_variant").df()
    dates = con.execute("SELECT tanggal FROM dim_date").df()
    prov = con.execute("SELECT provinsi FROM dim_provinsi").df()

    return variants, dates, prov


# =========================================================
# QUERY SERVICES (READ LAYER)
# =========================================================
def fetch_harga(variant_id: int, date_id: int):
    """
    Mengambil harga komoditas per provinsi pada tanggal tertentu.

    Args:
        variant_id (int): ID varian komoditas
        date_id (int): format YYYYMMDD (surrogate key)

    Returns:
        pd.DataFrame:
            - harga
            - provinsi

    Use Case:
        - Choropleth map (warna berdasarkan harga)
    """
    con = get_connection()

    return con.execute("""
        SELECT harga, p.provinsi
        FROM fact_harga f
        JOIN dim_provinsi p USING(kode_provinsi)
        WHERE variant_id = ? AND date_id = ?
    """, [variant_id, date_id]).df()


def fetch_trend(variant_id: int):
    """
    Mengambil tren harga (time series) untuk suatu komoditas.

    Args:
        variant_id (int): ID varian komoditas

    Returns:
        pd.DataFrame:
            - tanggal
            - harga (rata-rata nasional per hari)

    Aggregation:
        - AVG(harga) per tanggal

    Use Case:
        - Line chart (trend harga)
    """
    con = get_connection()

    return con.execute("""
        SELECT d.tanggal, AVG(f.harga) harga
        FROM fact_harga f
        JOIN dim_date d USING(date_id)
        WHERE variant_id = ?
        GROUP BY d.tanggal
        ORDER BY d.tanggal
    """, [variant_id]).df()


def fetch_comparison(provinsi: str, date_id: int):
    """
    Mengambil perbandingan harga antar komoditas dalam satu provinsi.

    Args:
        provinsi (str): nama provinsi
        date_id (int): format YYYYMMDD

    Returns:
        pd.DataFrame:
            - variant_id
            - variant_nama
            - unit
            - harga

    Use Case:
        - Tabel perbandingan harga (multi-komoditas)
    """
    con = get_connection()

    return con.execute("""
        SELECT v.variant_id, v.variant_nama, v.unit, f.harga
        FROM fact_harga f
        JOIN dim_variant v USING(variant_id)
        JOIN dim_provinsi p USING(kode_provinsi)
        WHERE p.provinsi = ? AND f.date_id = ?
    """, [provinsi, date_id]).df()