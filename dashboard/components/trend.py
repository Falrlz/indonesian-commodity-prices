import streamlit as st
import plotly.express as px
import pandas as pd


# =========================================================
# UI COMPONENT: TREND CHART
# =========================================================
def render_trend(df_trend: pd.DataFrame, komoditas: str = "", variant: str = ""):
    """
    Merender grafik tren harga nasional (time series).

    Args:
        df_trend (pd.DataFrame):
            dataset dengan kolom:
            - tanggal (datetime)
            - harga (numeric, hasil agregasi)
        komoditas (str, optional): nama komoditas (label UI)
        variant (str, optional): nama varian (label UI)

    Behavior:
        - Menampilkan line chart dengan marker
        - Format axis mengikuti konvensi Indonesia (Rp, ribuan titik)
        - Tooltip menampilkan tanggal + harga (tanpa desimal)

    Output:
        - Interactive chart (Plotly)

    Use Case:
        - Analisis tren harga dari waktu ke waktu
        - Identifikasi pola (naik/turun/fluktuasi)
    """
    st.subheader("Tren Harga Nasional")
    st.caption("Pergerakan harga rata-rata komoditas dalam periode waktu tertentu")

    # ======================
    # CONTEXT LABEL
    # ======================
    if komoditas and variant:
        st.caption(f"{komoditas} — {variant}")

    # ======================
    # BUILD CHART
    # ======================
    fig = px.line(df_trend, x="tanggal", y="harga", markers=True)

    fig.update_layout(
        separators=",.",  # format angka Indonesia
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(
            tickformat="%-d %b",
            tickangle=0,
        ),
        yaxis=dict(
            tickprefix="Rp ",
            tickformat=",.0f",  # tanpa desimal
        ),
    )

    # ======================
    # TOOLTIP CONFIG
    # ======================
    fig.update_traces(
        hovertemplate="<b>%{x|%-d %b %Y}</b><br>Rp %{y:,.0f}<extra></extra>",
    )

    # ======================
    # RENDER
    # ======================
    st.plotly_chart(fig, use_container_width=True)