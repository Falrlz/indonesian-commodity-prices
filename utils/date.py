from datetime import datetime, timedelta
from config.settings import START_DATE, END_DATE


# =========================================================
# DATE UTILITIES
# =========================================================

def generate_dates():
    """
    Generate daftar tanggal (string) dalam rentang [START_DATE, END_DATE].

    Source:
        - START_DATE, END_DATE (config.settings)

    Format:
        - Input  : YYYY-MM-DD
        - Output : List[str] dengan format YYYY-MM-DD

    Behavior:
        - Inclusive range (tanggal awal & akhir ikut)
        - Increment harian (1 hari)

    Raises:
        ValueError : jika format tanggal tidak valid
    """
    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.strptime(END_DATE, "%Y-%m-%d")

    dates = []

    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start += timedelta(days=1)

    return dates


def validate_date_format(date_str: str):
    """
    Validasi apakah string mengikuti format YYYY-MM-DD.

    Args:
        date_str (str): string tanggal

    Returns:
        bool:
            - True  → format valid
            - False → format tidak valid

    Note:
        - Tidak memvalidasi range/logika tanggal (hanya format)
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def today_str():
    """
    Menghasilkan tanggal hari ini dalam format string.

    Returns:
        str: tanggal hari ini (YYYY-MM-DD)

    Use Case:
        - Default value pada pipeline
        - Logging / timestamping
    """
    return datetime.today().strftime("%Y-%m-%d")