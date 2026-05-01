import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# =========================================================
# VISUAL CONFIGURATION
# =========================================================
COLOR_SCALE = ["#15803d", "#4ade80", "#fde047", "#fb923c", "#dc2626"]
LABELS = ["Sangat rendah", "Rendah", "Sedang", "Tinggi", "Sangat tinggi"]


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def _norm(x: str) -> str:
    """
    Normalisasi string untuk matching antar sumber data.

    Args:
        x (str): input string

    Returns:
        str: lower-case, tanpa simbol, trimmed

    Use Case:
        - Menyamakan nama provinsi antara DB dan GeoJSON
    """
    return x.lower().replace(".", "").replace("-", " ").strip()


def _build_price_map(df: pd.DataFrame, geojson: dict) -> tuple[dict, float, float]:
    """
    Membangun mapping provinsi → harga rata-rata.

    Args:
        df (pd.DataFrame): data harga (kolom: provinsi, harga)
        geojson (dict): data GeoJSON

    Returns:
        tuple:
            - price_map (dict): {provinsi_geo: harga}
            - mn (float): harga minimum
            - mx (float): harga maksimum

    Behavior:
        - Normalisasi nama provinsi untuk matching
        - Menggunakan fallback manual untuk kasus khusus
        - Drop provinsi yang tidak match
    """
    geo_lookup = {
        _norm(f["properties"]["PROVINSI"]): f["properties"]["PROVINSI"]
        for f in geojson["features"]
    }

    # mapping manual untuk edge-case naming
    manual_map = {
        "dki jakarta": "DKI Jakarta",
        "di yogyakarta": "Daerah Istimewa Yogyakarta",
        "kep bangka belitung": "Kepulauan Bangka Belitung",
    }

    df_map = df.groupby("provinsi", as_index=False).harga.mean()

    df_map["provinsi_fix"] = df_map.provinsi.map(
        lambda x: geo_lookup.get(_norm(x)) or manual_map.get(_norm(x))
    )

    df_map = df_map.dropna(subset=["provinsi_fix"])

    price_map = dict(zip(df_map.provinsi_fix, df_map.harga))
    mn, mx = df_map.harga.min(), df_map.harga.max()

    return price_map, mn, mx


def _get_color(harga, mn: float, mx: float) -> str | None:
    """
    Menghasilkan warna berdasarkan skala harga.

    Args:
        harga (float): nilai harga
        mn (float): nilai minimum
        mx (float): nilai maksimum

    Returns:
        str | None: kode warna hex atau None jika tidak ada data

    Logic:
        - Normalisasi ke range [0,1]
        - Mapping ke 5 bucket warna
    """
    if harga is None:
        return None

    r = (harga - mn) / (mx - mn + 1e-9)
    return COLOR_SCALE[min(int(r * 5), 4)]


def _build_legend(mn: float, mx: float) -> str:
    """
    Membuat HTML legend untuk interpretasi warna.

    Args:
        mn (float): harga minimum
        mx (float): harga maksimum

    Returns:
        str: HTML legend (overlay pada peta)

    Notes:
        - Dibagi menjadi 5 interval
        - Menampilkan label + range harga
    """
    step = (mx - mn) / 5
    items = ""

    for i, (color, label) in enumerate(zip(COLOR_SCALE, LABELS)):
        low = mn + i * step
        high = mn + (i + 1) * step
        range_str = f"Rp {low:,.0f} – {high:,.0f}".replace(",", ".")

        items += f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px;">
                <div style="width:14px; height:14px; border-radius:3px;
                            background:{color}; flex-shrink:0;"></div>
                <div>
                    <div style="font-size:11px; font-weight:600; color:#1e293b;">{label}</div>
                    <div style="font-size:10px; color:#64748b;">{range_str}</div>
                </div>
            </div>
        """

    return f"""
        <div style="
            position: absolute; bottom: 24px; right: 10px; z-index: 1000;
            background: rgba(255,255,255,0.92); backdrop-filter: blur(4px);
            padding: 10px 12px; border-radius: 8px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.15);
            font-family: sans-serif; pointer-events: none;">
            <div style="font-size:11px; font-weight:700; color:#0f172a;
                        margin-bottom:8px; letter-spacing:0.3px;">Harga</div>
            {items}
            <div style="font-size:10px; color:#94a3b8; margin-top:6px;
                        border-top:1px solid #e2e8f0; padding-top:5px;">
                Abu-abu = tidak ada data
            </div>
        </div>
    """


# =========================================================
# MAIN COMPONENT: CHOROPLETH MAP
# =========================================================
def render_map(df: pd.DataFrame, geojson: dict):
    """
    Merender peta distribusi harga per provinsi (choropleth).

    Args:
        df (pd.DataFrame):
            kolom minimal:
            - provinsi
            - harga
        geojson (dict): boundary provinsi Indonesia

    Behavior:
        - Menggunakan warna berdasarkan range harga
        - Tooltip menampilkan provinsi + harga
        - Menampilkan legend jika data tersedia

    Output:
        - Interactive map (Folium + Streamlit)

    Use Case:
        - Visualisasi spasial harga komoditas
        - Identifikasi disparitas antar wilayah
    """
    st.subheader("Distribusi Harga Komoditas per Provinsi")
    st.caption("Visualisasi spasial harga untuk mengidentifikasi disparitas regional")

    if not df.empty:
        price_map, mn, mx = _build_price_map(df, geojson)
    else:
        price_map, mn, mx = {}, 0.0, 1.0

    # ======================
    # STYLE FUNCTION
    # ======================
    def style_fn(feature):
        harga = price_map.get(feature["properties"]["PROVINSI"])
        color = _get_color(harga, mn, mx)

        return {
            "fillColor": color or "#ffffff",
            "color": "#94a3b8",
            "weight": 0.8,
            "fillOpacity": 0.85 if color else 0.0,
        }

    # ======================
    # TOOLTIP
    # ======================
    def tooltip_html(prov: str) -> str:
        harga = price_map.get(prov)
        harga_str = f"Rp {harga:,.0f}".replace(",", ".") if harga else "-"
        return f"<b>{prov}</b><br>Harga: {harga_str}"

    # ======================
    # BASE MAP
    # ======================
    m = folium.Map(
        location=[-2.5, 118],
        zoom_start=5,
        tiles=None,
        prefer_canvas=True,
        min_zoom=4,
        max_zoom=7,
        scrollWheelZoom=False,
    )

    # remove default tiles (clean background)
    m.get_root().html.add_child(folium.Element("""
        <style>
            .leaflet-container { background: transparent !important; }
            .leaflet-tile-pane  { display: none !important; }
        </style>
    """))

    # ======================
    # RENDER GEO FEATURES
    # ======================
    for feature in geojson["features"]:
        prov = feature["properties"]["PROVINSI"]

        folium.GeoJson(
            feature,
            style_function=style_fn,
            tooltip=folium.Tooltip(tooltip_html(prov), sticky=True),
        ).add_to(m)

    # ======================
    # LEGEND
    # ======================
    if not df.empty:
        m.get_root().html.add_child(folium.Element(_build_legend(mn, mx)))

    st_folium(m, height=450, use_container_width=True)