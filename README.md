# Indonesian Commodity Prices

**Never analyze commodity prices blindly again.**

Have you ever struggled to understand commodity prices in Indonesia due to scattered and hard-to-compare data?

**Indonesian Commodity Prices** helps you monitor trends, distribution, and dynamics of commodity prices across provinces using an end-to-end data pipeline and an interactive dashboard.

## Live Demo

https://indonesian-commodity-prices.streamlit.app

## Preview

![Dashboard](assets\preview.gif)

## What It Does

- **Trend Analysis** → Track price movements over time  
- **Geospatial Mapping** → Compare prices across provinces  
- **Price Comparison** → Analyze price changes across dates  
- **Fast Analytics** → High-performance queries using DuckDB  
- **ETL Pipeline** → End-to-end data pipeline (extract → transform → load)  

## How It Works

### 1. Data Extraction
- Fetches commodity price data from official sources (SP2KP)
- Uses HTTP requests with retry and delay control

### 2. Data Transformation
- Cleans raw data
- Normalizes structure
- Generates features for analysis

### 3. Data Storage
- Data is stored in **DuckDB**
- Structured using:
  - `fact_harga`
  - `dim_variant`
  - `dim_provinsi`
  - `dim_date`

### 4. Data Visualization
- Interactive Streamlit dashboard
- Charts and geospatial mapping
- Direct querying from DuckDB

## Key Features

### Analytics
- Time-series price trends  
- National average price metrics  
- Automated insights (highest, lowest, average prices)  

### Visualization
- Indonesia choropleth map  
- Dynamic filtering (commodity, date)  
- Responsive layout  

### Performance
- DuckDB (no external database required)  
- Streamlit caching  
- Efficient querying  

### Data Engineering
- Modular ETL pipeline  
- Retry mechanism & request throttling  
- Environment-based configuration  

## Project Architecture

```
indonesian-commodity-prices/
├── dashboard/          # Streamlit application (presentation layer)
│ ├── components/       # Reusable UI components
│ │ ├── filters.py      # Filter controls (komoditas, tanggal)
│ │ ├── kpi.py          # KPI summary metrics
│ │ ├── map.py          # Choropleth map visualization
│ │ ├── trend.py        # Time-series chart
│ │ ├── comparison.py   # Price comparison table
│ │ └── footer.py       # Footer & metadata
│ │
│ ├── services/         # Data access layer
│ │ └── data_service.py # Query DuckDB + caching
│ │
│ └── app.py            # Main Streamlit entry point
│
├── etl/                # Data engineering pipeline
│ ├── extract.py        # Fetch data from API
│ ├── transform.py      # Data cleaning & preprocessing
│ ├── load_db.py        # Load data into DuckDB
│ ├── build_mart.py     # Data mart preparation
│ └── pipeline.py       # Orchestration of ETL flow
│
├── scripts/            # Utility scripts
│ ├── run_etl.py        # Run full ETL pipeline
│ ├── check_db.py       # Validate database integrity
│ └── check_geojson.py  # Validate geo data
│
├── data/               # Data storage layer
│ ├── db/               # Analytical database (DuckDB)
│ ├── geo/              # Map boundary
│ └── staging/          # ETL output
│
├── config/
│ └── settings.py       # Configuration settings
│
├── utils/              # Helper utilities
│ ├── date.py           # Date utilities
│ └── io.py             # File handling utilities
│
├── assets/             # Static assets (for README)
│ └── dashboard.png
│
├── .env.example        # Environment template
├── .gitignore
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Technology Stack

### Data & Analytics
- **DuckDB** → Analytical database engine (in-process OLAP)
- **Pandas** → Data manipulation & preprocessing
- **NumPy** → Numerical computation
- **PyArrow** → Efficient columnar data processing

### Data Pipeline (ETL)
- **Python** → Core language for ETL pipeline
- **Requests** → Data extraction from API
- **python-dotenv** → Environment configuration

### Visualization & Dashboard
- **Streamlit** → Interactive web dashboard
- **Plotly** → Interactive charts & visualizations
- **Folium + streamlit-folium** → Geospatial visualization (map)

### Deployment
- **Streamlit Cloud** → Hosting & deployment

## Quick Start

### 1. Clone Repo
```bash
git clone https://github.com/Falrlz/indonesian-commodity-prices.git
cd indonesian-commodity-prices
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment
```bash
cp .env.example .env
```

### 4. Run ETL Pipeline
```bash
py -m scripts.run_etl
```

### 5. Run Dashboard
```bash
py -m streamlit run dashboard/app.py
```

## Environment Configuration

```bash
COOKIE=your_cookie_here
START_DATE=YYYY-MM-DD
END_DATE=YYYY-MM-DD
REQUEST_DELAY=1.0
MAX_VARIANTS=
DB_PATH=data/db/komoditas.duckdb
```
## Acknowledgements

This project utilizes publicly available data and resources:

- **SP2KP (Sistem Pemantauan Pasar dan Kebutuhan Pokok)**  
  Commodity price data is sourced from official monitoring systems.  
  Special thanks for providing accessible and valuable public data.

- **Indonesia GeoJSON (38 Provinces)**  
  https://github.com/denyherianto/indonesia-geojson-topojson-maps-with-38-provinces  
  Used for geospatial visualization of Indonesia provinces.

## Disclaimer

- This project is intended for educational and analytical purposes.  
- Data accuracy depends on the original source and may change over time.  