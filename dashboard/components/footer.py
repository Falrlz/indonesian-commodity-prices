import streamlit as st
from datetime import datetime


def render_footer():
    current_year = datetime.now().year

    st.markdown("---")

    footer_html = f"""
    <div style="
        text-align: center;
        color: #6c757d;
        font-size: 0.85rem;
        line-height: 1.6;
        padding-top: 10px;
        padding-bottom: 20px;
    ">
        <b>Sumber Data:</b> Sistem Pemantauan Pasar dan Kebutuhan Pokok (SP2KP)<br><br>

        &copy; {current_year} Monitor Harga Komoditas Indonesia<br>

        <span style="font-size: 0.75rem;">
        Catatan: Data yang ditampilkan merupakan hasil agregasi dari sumber resmi dan dapat mengalami pembaruan sewaktu-waktu. 
        Periode data: 01 Januari 2026 – 30 April 2026.
        </span>
    </div>
    """

    st.html(footer_html)