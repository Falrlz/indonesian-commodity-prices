import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# =========================================================
# FILE I/O UTILITIES
# =========================================================

def ensure_dir(path: str):
    """
    Memastikan direktori tujuan tersedia.

    Args:
        path (str): path file (bukan folder)

    Behavior:
        - Membuat parent directory jika belum ada
        - Tidak error jika sudah ada (idempotent)
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)


def save_csv(df: pd.DataFrame, path: str):
    """
    Menyimpan DataFrame ke file CSV secara aman.

    Args:
        df (pd.DataFrame): data yang akan disimpan
        path (str): lokasi file output

    Behavior:
        - Skip jika DataFrame kosong / None
        - Auto-create directory jika belum ada
        - Menyimpan tanpa index

    Logging:
        - WARNING jika data kosong
        - INFO jika berhasil disimpan (termasuk jumlah baris)
    """
    if df is None or df.empty:
        logger.warning(f"Data kosong, tidak disimpan: {path}")
        return

    ensure_dir(path)

    df.to_csv(path, index=False)

    logger.info(f"Saved CSV: {path} | rows={len(df)}")


def load_csv(path: str) -> pd.DataFrame:
    """
    Memuat file CSV dengan validasi eksistensi.

    Args:
        path (str): lokasi file CSV

    Returns:
        pd.DataFrame: hasil pembacaan CSV

    Raises:
        FileNotFoundError: jika file tidak ditemukan

    Logging:
        - INFO setelah berhasil load (jumlah baris)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    df = pd.read_csv(path)

    logger.info(f"Loaded CSV: {path} | rows={len(df)}")

    return df


def save_parquet(df: pd.DataFrame, path: str):
    """
    Menyimpan DataFrame ke format Parquet (columnar & efisien).

    Args:
        df (pd.DataFrame): data yang akan disimpan
        path (str): lokasi file output

    Behavior:
        - Skip jika DataFrame kosong / None
        - Auto-create directory jika belum ada
        - Menyimpan tanpa index

    Advantages:
        - Lebih cepat I/O dibanding CSV
        - Ukuran file lebih kecil
        - Optimal untuk analytics pipeline

    Logging:
        - WARNING jika data kosong
        - INFO jika berhasil disimpan (jumlah baris)
    """
    if df is None or df.empty:
        logger.warning(f"Data kosong, tidak disimpan: {path}")
        return

    ensure_dir(path)

    df.to_parquet(path, index=False)

    logger.info(f"Saved Parquet: {path} | rows={len(df)}")