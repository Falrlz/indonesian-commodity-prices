import streamlit as st
import pandas as pd
from services.data_service import fetch_comparison


# =========================================================
# FORMAT UTILITIES
# =========================================================
def _format_harga(harga) -> str:
    """
    Format nilai harga ke Rupiah (IDR).

    Args:
        harga (float | int | NaN)

    Returns:
        str: "Rp 1.000.000" atau "-" jika null
    """
    if pd.isna(harga):
        return "-"
    return f"Rp {harga:,.0f}".replace(",", ".")


def _format_with_arrow(x) -> str:
    """
    Format persentase perubahan dengan indikator arah.

    Args:
        x (float | NaN): nilai persentase

    Returns:
        str:
            - "▲ +x.xx%" (naik)
            - "▼ x.xx%"  (turun)
            - "= 0.00%"  (stabil)
            - "-"        (null)
    """
    if pd.isna(x):
        return "-"

    arrow = "▲" if x > 0 else ("▼" if x < 0 else "=")
    sign = "+" if x > 0 else ""

    return f"{arrow} {sign}{x:.2f}%"


def _style_pct(val):
    """
    Styling visual untuk kolom persentase perubahan.

    Args:
        val (str): formatted percentage string

    Returns:
        str: CSS inline style

    Logic:
        - Positif → hijau
        - Negatif → merah
        - Nol     → abu
    """
    if val == "-" or pd.isna(val):
        return ""

    try:
        num = float(
            val.replace("%", "")
               .replace("+", "")
               .replace("▲", "")
               .replace("▼", "")
               .replace("=", "")
               .strip()
        )
    except:
        return ""

    if num > 0:
        return "color: #16a34a; font-weight: 600;"
    elif num < 0:
        return "color: #dc2626; font-weight: 600;"
    else:
        return "color: #64748b;"


# =========================================================
# DATA PREPARATION
# =========================================================
def _build_comparison_df(provinsi: str, d1_id: int, d2_id: int) -> pd.DataFrame:
    """
    Membangun dataset perbandingan harga antar dua tanggal.

    Args:
        provinsi (str): nama provinsi
        d1_id (int): date_id awal (YYYYMMDD)
        d2_id (int): date_id akhir (YYYYMMDD)

    Returns:
        pd.DataFrame:
            - variant_id
            - variant_nama
            - unit
            - harga_awal
            - harga_akhir
            - Perubahan (%)

    Process:
        - Fetch data dua tanggal
        - Outer join (agar semua komoditas tetap muncul)
        - Hitung delta dan persentase perubahan
    """
    df1 = fetch_comparison(provinsi, d1_id)
    df2 = fetch_comparison(provinsi, d2_id)

    df_cmp = df1.merge(
        df2,
        on="variant_id",
        how="outer",
        suffixes=("_awal", "_akhir")
    )

    if df_cmp.empty:
        return df_cmp

    # resolve metadata (fallback antar tanggal)
    df_cmp["variant_nama"] = df_cmp["variant_nama_awal"].combine_first(df_cmp["variant_nama_akhir"])
    df_cmp["unit"] = df_cmp["unit_awal"].combine_first(df_cmp["unit_akhir"])

    df_cmp = df_cmp.drop(
        columns=["variant_nama_awal", "variant_nama_akhir", "unit_awal", "unit_akhir"]
    )

    # delta & percentage change
    df_cmp["_delta_rp"] = df_cmp["harga_akhir"] - df_cmp["harga_awal"]
    df_cmp["Perubahan (%)"] = (df_cmp["_delta_rp"] / df_cmp["harga_awal"]) * 100

    return df_cmp


# =========================================================
# UI COMPONENT: COMPARISON TABLE
# =========================================================
def render_comparison(prov_list: pd.DataFrame):
    """
    Merender tabel perbandingan harga antar dua tanggal dalam satu provinsi.

    Args:
        prov_list (pd.DataFrame):
            kolom: provinsi

    UI Elements:
        - Dropdown provinsi
        - Date picker (awal & akhir)
        - Tabel perbandingan harga

    Behavior:
        - Menampilkan placeholder jika input belum lengkap
        - Menampilkan info jika data kosong
        - Styling warna berdasarkan perubahan (%)

    Output:
        - DataFrame styled (Streamlit)
    """
    st.subheader("Analisis Perubahan Harga Antar Waktu")

    c1, c2, c3 = st.columns(3)

    # ======================
    # INPUTS
    # ======================
    prov = c1.selectbox(
        "Provinsi",
        options=sorted(prov_list.provinsi.dropna().unique()),
        index=None,
        placeholder="Silakan pilih provinsi",
    )

    d1 = c2.date_input("Tanggal Awal", value=None)
    d2 = c3.date_input("Tanggal Akhir", value=None)

    empty_cols = ["Tipe Komoditas", "Harga Awal", "Harga Akhir", "Perubahan (%)"]

    # ======================
    # VALIDATION
    # ======================
    if not (prov and d1 and d2):
        st.dataframe(pd.DataFrame(columns=empty_cols), use_container_width=True)
        return

    d1_id = int(pd.to_datetime(d1).strftime("%Y%m%d"))
    d2_id = int(pd.to_datetime(d2).strftime("%Y%m%d"))

    df_cmp = _build_comparison_df(prov, d1_id, d2_id)

    if df_cmp.empty:
        st.info("Tidak ada data.")
        return

    # ======================
    # DISPLAY DATA
    # ======================
    df_display = pd.DataFrame({
        "Tipe Komoditas": df_cmp["variant_nama"],
        "Unit": df_cmp["unit"],
        "Harga Awal": df_cmp["harga_awal"].map(_format_harga),
        "Harga Akhir": df_cmp["harga_akhir"].map(_format_harga),
        "Perubahan (%)": df_cmp["Perubahan (%)"].map(_format_with_arrow),
    }).sort_values("Tipe Komoditas")

    # ======================
    # STYLE
    # ======================
    styled = df_display.style.map(_style_pct, subset=["Perubahan (%)"])

    st.dataframe(styled, use_container_width=True, hide_index=True)