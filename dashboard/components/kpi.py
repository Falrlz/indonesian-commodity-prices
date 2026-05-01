import streamlit as st
import pandas as pd


# =========================================================
# FORMAT UTILITIES
# =========================================================
def _rp(x) -> str:
    """
    Format angka ke Rupiah (IDR).

    Args:
        x (float | int): nilai numerik

    Returns:
        str: format "Rp 1.000.000"

    Notes:
        - Tanpa desimal
        - Menggunakan separator ribuan (.)
    """
    return f"Rp {x:,.0f}".replace(",", ".")


# =========================================================
# UI COMPONENT: KPI METRICS
# =========================================================
def render_kpi(df: pd.DataFrame):
    """
    Merender 3 metrik KPI harga:
        - Rata-rata (mean)
        - Tertinggi (max + provinsi)
        - Terendah (min + provinsi)

    Args:
        df (pd.DataFrame):
            dataset dengan kolom minimal:
            - harga (numeric)
            - provinsi (string)

    Behavior:
        - Jika data kosong → tampilkan placeholder "-"
        - Menggunakan metric card (Streamlit)

    Output:
        - 3 kolom KPI (st.metric)

    Use Case:
        - Ringkasan cepat kondisi harga
        - Insight distribusi antar provinsi
    """
    if not df.empty:
        avg = df.harga.mean()
        max_r = df.loc[df.harga.idxmax()]
        min_r = df.loc[df.harga.idxmin()]
    else:
        avg = max_r = min_r = None

    # ======================
    # KPI LABEL & VALUE
    # ======================
    titles = [
        "Rata-rata",
        f"Tertinggi ({max_r.provinsi})" if max_r is not None else "Tertinggi",
        f"Terendah ({min_r.provinsi})" if min_r is not None else "Terendah",
    ]

    values = [
        _rp(avg) if avg is not None else "-",
        _rp(max_r.harga) if max_r is not None else "-",
        _rp(min_r.harga) if min_r is not None else "-",
    ]

    # ======================
    # RENDER METRICS
    # ======================
    for col, title, val in zip(st.columns(3), titles, values):
        col.metric(title, val)