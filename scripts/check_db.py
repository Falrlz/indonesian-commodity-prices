import duckdb
import pandas as pd

DB_PATH = "data/db/komoditas.duckdb"


# =========================================================
# DATABASE INSPECTION SCRIPT
# =========================================================
def main():
    """
    Script utilitas untuk inspeksi isi database DuckDB.

    Functionality:
        - Menampilkan daftar tabel dalam database
        - Menampilkan jumlah baris (row count) tiap tabel
        - Menampilkan preview data (limit 5 baris)

    Use Case:
        - Validasi hasil ETL (dim, fact, mart)
        - Debugging data pipeline
        - Quick data exploration tanpa BI tools

    Output:
        - Console print:
            * list tabel
            * jumlah data per tabel
            * sample data (head)

    Notes:
        - Tidak mengubah data (read-only operation)
        - Aman dijalankan berulang kali
    """

    # =========================
    # CONNECT DATABASE
    # =========================
    print("🔗 Connecting to database...")
    con = duckdb.connect(DB_PATH)

    # =========================
    # SHOW TABLES
    # =========================
    print("\n📋 Tables in DB:")
    tables = con.execute("SHOW TABLES").fetchall()

    for t in tables:
        print("-", t[0])

    # =========================
    # LOOP TABLES
    # =========================
    for t in tables:
        table_name = t[0]

        print(f"\n{'='*50}")
        print(f"📊 TABLE: {table_name}")
        print(f"{'='*50}")

        # row count (cardinality check)
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Rows: {count}")

        # data preview (sanity check)
        df = con.execute(f"SELECT * FROM {table_name} LIMIT 5").df()
        print(df)

    con.close()
    print("\n✅ Done")


# =========================================================
# SCRIPT ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    main()