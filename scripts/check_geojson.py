import json
import duckdb

GEO_PATH = "data/geo/id.geojson"
DB_PATH = "data/db/harga.duckdb"


# =========================================================
# GEOJSON UTILITIES
# =========================================================
def detect_key(props):
    """
    Mendeteksi nama field yang merepresentasikan provinsi pada GeoJSON.

    Args:
        props (dict): dictionary properties dari feature GeoJSON

    Returns:
        str | None:
            - nama key yang cocok
            - None jika tidak ditemukan

    Strategy:
        - Mencoba beberapa kandidat umum lintas dataset GeoJSON
    """
    candidates = [
        "PROVINSI",
        "state",        # fallback umum (beberapa dataset internasional)
        "name",
        "NAME_1",
        "province",
        "Propinsi"
    ]

    for c in candidates:
        if c in props:
            return c

    return None


def normalize(s):
    """
    Normalisasi string untuk keperluan matching.

    Args:
        s (Any): input string

    Returns:
        str: string dalam format lower-case dan trimmed

    Use Case:
        - Menghindari mismatch karena case / whitespace
    """
    return str(s).lower().strip()


# =========================================================
# GEO ↔ DATABASE VALIDATION SCRIPT
# =========================================================
def main():
    """
    Script validasi kesesuaian nama provinsi antara:
        - GeoJSON (layer peta)
        - Database (dim_provinsi)

    Validation Scope:
        1. Deteksi field provinsi pada GeoJSON
        2. Ekstraksi nama provinsi dari GeoJSON
        3. Ekstraksi nama provinsi dari database
        4. Bidirectional comparison:
           - DB → GeoJSON
           - GeoJSON → DB

    Output:
        - Daftar provinsi yang tidak match
        - Summary tingkat kesesuaian

    Use Case:
        - Validasi sebelum visualisasi peta (choropleth)
        - Debug mismatch nama wilayah
        - Quality check integrasi data geospasial

    Notes:
        - Matching berbasis string normalization (case-insensitive)
        - Tidak menangani fuzzy matching / alias kompleks
    """

    print("🔍 Checking GeoJSON...\n")

    # =========================
    # LOAD GEOJSON
    # =========================
    try:
        with open(GEO_PATH, encoding="utf-8") as f:
            geojson = json.load(f)
    except FileNotFoundError:
        print("❌ File tidak ditemukan:", GEO_PATH)
        return

    features = geojson.get("features", [])

    if not features:
        print("❌ GeoJSON kosong / tidak valid")
        return

    props = features[0]["properties"]

    print("📦 Struktur properties:")
    print(props, "\n")

    # =========================
    # DETECT PROPERTY KEY
    # =========================
    key = detect_key(props)

    if not key:
        print("❌ Tidak bisa detect key provinsi")
        return

    print(f"✅ Property key detected: {key}\n")

    # =========================
    # EXTRACT GEO PROVINCES
    # =========================
    geo_names = [f["properties"][key] for f in features]

    print(f"📊 Total Provinsi GeoJSON: {len(geo_names)}\n")

    print("📍 Sample (10 pertama):")
    for name in geo_names[:10]:
        print("-", name)

    # =========================
    # LOAD DB PROVINCES
    # =========================
    print("\n🔗 Checking DB...\n")

    con = duckdb.connect(DB_PATH)

    df = con.execute("""
        SELECT DISTINCT provinsi
        FROM dim_provinsi
        ORDER BY provinsi
    """).df()

    db_names = df["provinsi"].tolist()

    print(f"📊 Total Provinsi DB: {len(db_names)}\n")

    print("📍 DB Sample:")
    for name in db_names[:10]:
        print("-", name)

    # =========================
    # COMPARE: DB → GEOJSON
    # =========================
    print("\n⚠️ TIDAK MATCH (DB → GEOJSON):")

    geo_norm = {normalize(n): n for n in geo_names}
    missing = []

    for n in db_names:
        if normalize(n) not in geo_norm:
            print("-", n)
            missing.append(n)

    if not missing:
        print("✔ Semua provinsi match!")

    # =========================
    # COMPARE: GEOJSON → DB
    # =========================
    print("\n⚠️ TIDAK MATCH (GEOJSON → DB):")

    db_norm = {normalize(n): n for n in db_names}
    missing_geo = []

    for n in geo_names:
        if normalize(n) not in db_norm:
            print("-", n)
            missing_geo.append(n)

    if not missing_geo:
        print("✔ Semua provinsi match!")

    # =========================
    # SUMMARY
    # =========================
    print("\n📌 SUMMARY:")

    if not missing and not missing_geo:
        print("✅ PERFECT MATCH (100%)")
    else:
        print(f"⚠️ DB missing: {len(missing)}")
        print(f"⚠️ GEO missing: {len(missing_geo)}")

    con.close()


# =========================================================
# SCRIPT ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    main()