import streamlit as st
import pandas as pd


# =========================================================
# UI COMPONENT: FILTER PANEL
# =========================================================
def render_filters(variants: pd.DataFrame):
    """
    Merender komponen filter utama pada dashboard.

    Args:
        variants (pd.DataFrame):
            dataset dim_variant dengan kolom minimal:
            - komoditas
            - variant_nama

    Returns:
        tuple:
            - komoditas (str | None)
            - variant (str | None)
            - tanggal (datetime.date | None)
            - df_var (pd.DataFrame) : subset variant terpilih
            - is_ready (bool)       : flag semua input sudah valid

    UI Structure:
        - Column 1: Komoditas (parent selection)
        - Column 2: Tipe Komoditas / Variant (dependent selection)
        - Column 3: Tanggal

    Behavior:
        - Dropdown variant bergantung pada komoditas yang dipilih
        - Jika komoditas belum dipilih → variant disabled (empty options)
        - Validasi sederhana berbasis kelengkapan input

    Use Case:
        - Control panel untuk query (map, trend, comparison)
    """
    c1, c2, c3 = st.columns(3)

    # ========================
    # KOMODITAS (PARENT)
    # ========================
    komoditas_list = sorted(variants.komoditas.dropna().unique())

    komoditas = c1.selectbox(
        "Komoditas",
        options=komoditas_list,
        index=None,
        placeholder="Silakan pilih komoditas",
    )

    # ========================
    # VARIANT (DEPENDENT)
    # ========================
    if komoditas:
        df_var = variants[variants.komoditas == komoditas]
        variant_list = df_var.variant_nama.tolist()

        variant = c2.selectbox(
            "Tipe Komoditas",
            options=variant_list,
            index=None,
            placeholder="Silakan pilih tipe komoditas",
        )
    else:
        df_var = pd.DataFrame()
        variant = c2.selectbox(
            "Tipe Komoditas",
            options=[],
            index=None,
            placeholder="Silakan pilih tipe komoditas",
        )

    # ========================
    # DATE INPUT
    # ========================
    tanggal = c3.date_input(
        "Tanggal",
        value=None,
        format="YYYY/MM/DD",  # format display
    )

    # ========================
    # VALIDATION FLAG
    # ========================
    is_ready = bool(komoditas and variant and tanggal)

    return komoditas, variant, tanggal, df_var, is_ready