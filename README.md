# 🌍 Air Quality Monitor

A Python-based desktop application for monitoring air quality in Poland. It connects to the official GIOŚ API, allows users to search for cities and monitoring stations, fetches pollution data, stores it locally, and visualizes trends interactively.

---

## 🚀 Features

- 🔎 City search with station auto-suggestions
- 📡 Live air quality data from [GIOŚ](https://powietrze.gios.gov.pl/pjp/content/api)
- 🗃️ SQLite local database for historical storage
- 📊 Data analysis: min, max, average, trend
- 📈 Interactive data visualization with Matplotlib
- 🧪 Modular structure with unit testing

---

## 🗂️ Project Structure

air_quality_monitor/
├── air_quality/
│ ├── init.py
│ ├── api.py # Fetches data from GIOŚ API
│ ├── db.py # Database creation and storage
│ ├── analysis.py # Calculates min, max, average
│ ├── visualization.py # Matplotlib visualizations
│ └── main.py # GUI and application logic
├── data/ # SQLite database file
├── tests/ # Unit tests for modules
├── requirements.txt
└── README.md
