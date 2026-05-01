import pandas as pd


# =========================================================
# DATA CLEANING
# =========================================================
def clean_data(df):
    """
    Melakukan pembersihan data mentah hasil scraping.

    Args:
        df (pd.DataFrame): data mentah

    Returns:
        pd.DataFrame: data yang telah dibersihkan

    Cleaning Steps:
        1. Casting tipe data:
           - tanggal → datetime
           - harga & harga_sebelumnya → numeric
        2. Drop missing values pada kolom kritikal:
           - tanggal, harga, provinsi
        3. Filtering anomali harga:
           - harga < 100 atau > 500.000 akan dibuang
        4. Remove duplicate rows

    Behavior:
        - Menggunakan errors="coerce" untuk menghindari crash saat parsing
        - Mengembalikan DataFrame kosong jika input kosong
    """
    if df.empty:
        return df

    df = df.copy()

    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df["harga"] = pd.to_numeric(df["harga"], errors="coerce")
    df["harga_sebelumnya"] = pd.to_numeric(df.get("harga_sebelumnya"), errors="coerce")

    # drop null penting
    df = df.dropna(subset=["tanggal", "harga", "provinsi"])

    # validasi harga (hindari anomali ekstrem)
    df = df[(df["harga"] > 100) & (df["harga"] < 500_000)]

    df = df.drop_duplicates()

    return df


# =========================================================
# DATA STANDARDIZATION
# =========================================================
def standardize_data(df):
    """
    Menstandarisasi format data untuk konsistensi downstream processing.

    Args:
        df (pd.DataFrame): data hasil cleaning

    Returns:
        pd.DataFrame: data yang telah distandardisasi

    Standardization Rules:
        - provinsi  : trim whitespace
        - komoditas : title case (normalisasi teks)
        - harga     : pembulatan 2 desimal

    Behavior:
        - Tidak mengubah struktur kolom
        - Aman terhadap DataFrame kosong
    """
    if df.empty:
        return df

    df = df.copy()

    df["provinsi"] = df["provinsi"].str.strip()
    df["komoditas"] = df["komoditas"].str.title()
    df["harga"] = df["harga"].round(2)

    return df