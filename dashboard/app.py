import sys
import os

# inject root project ke PYTHONPATH (HARUS paling atas)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


import streamlit as st
import pandas as pd

from dashboard.services.data_service import load_geo, load_master, fetch_harga, fetch_trend
from dashboard.components.filters import render_filters
from dashboard.components.kpi import render_kpi
from dashboard.components.map import render_map
from dashboard.components.trend import render_trend
from dashboard.components.comparison import render_comparison
from dashboard.components.footer import render_footer

# =========================================================
# APP CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Monitor Harga Komoditas Indonesia",
    layout="wide",
)


# =========================================================
# DATA LOADING (CACHED VIA SERVICE LAYER)
# =========================================================
# - GeoJSON   : boundary peta Indonesia
# - Variants  : dim_variant (komoditas & tipe)
# - Dates     : dim_date
# - Prov List : dim_provinsi
geojson = load_geo()
variants, dates, prov_list = load_master()


# =========================================================
# HEADER
# =========================================================
st.title("Monitor Harga Komoditas Indonesia")
st.caption("Pemantauan tren, distribusi, dan dinamika harga komoditas lintas provinsi")


# =========================================================
# FILTER PANEL (UI CONTROL)
# =========================================================
# Output:
# - komoditas, variant, tanggal
# - df_var (subset variant)
# - is_ready (flag validasi input)
komoditas, variant, tanggal, df_var, is_ready = render_filters(variants)


# =========================================================
# DATA FETCHING (QUERY LAYER)
# =========================================================
if is_ready:
    # resolve variant_id dari selection
    variant_id = int(
        df_var[df_var.variant_nama == variant].variant_id.values[0]
    )

    # convert tanggal → surrogate key (YYYYMMDD)
    date_id = int(pd.to_datetime(tanggal).strftime("%Y%m%d"))

    # fetch data:
    # - df        : harga per provinsi (map & KPI)
    # - df_trend  : time-series nasional
    df = fetch_harga(variant_id, date_id)
    df_trend = fetch_trend(variant_id)

else:
    # fallback kosong (hindari error downstream)
    df = pd.DataFrame()
    df_trend = pd.DataFrame({"tanggal": [], "harga": []})
    variant_id = None


# =========================================================
# RENDER SECTIONS (PRESENTATION LAYER)
# =========================================================
# Urutan:
# 1. KPI ringkasan
# 2. Peta distribusi
# 3. Tren harga
# 4. Perbandingan antar tanggal

render_kpi(df)
render_map(df, geojson)
render_trend(
    df_trend,
    komoditas=komoditas or "",
    variant=variant or ""
)
render_comparison(prov_list)
render_footer()