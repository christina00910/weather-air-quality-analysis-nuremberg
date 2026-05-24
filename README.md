# Schadstoff- & Wetter-Korrelationsanalyse – Nürnberg
### Air Pollution & Weather Correlation Analysis – Nuremberg

> **Abschlussprojekt** | Data Science Institut – Abschlussklasse Dezember 2025  
> **Authors:** Christina Dürrbeck · Markus Edelhoff · Frank Hasdorf

---

## Sprachauswahl / Language

- [Deutsch](#deutsch)
- [English](#english)

---

## Deutsch

### Projektbeschreibung

Dieses Projekt analysiert den Zusammenhang zwischen Wetterbedingungen und Luftschadstoffkonzentrationen (Ozon O₃, Stickstoffdioxid NO₂, Feinstaub PM10) in der Stadt Nürnberg. Grundlage sind stündliche Messdaten von 1980 bis 2026 (~400.000 Datensätze).

Das Ergebnis ist ein interaktives **Streamlit-Dashboard**, das Zeitreihen, WHO-Grenzwertvergleiche und Machine-Learning-basierte Trendanalysen visualisiert.

### Features

- Interaktive Zeitreihendiagramme mit Jahres-Slider (1980–2026)
- Vergleich der gemessenen Jahresmittelwerte mit WHO-Grenzwerten
- Korrelationsanalyse: Temperatur, Luftfeuchtigkeit, Solarstrahlung vs. Schadstoffe
- Random-Forest-Modell zur Analyse von Einflussfaktoren
- Vollautomatische ETL-Pipeline – Rohdaten bleiben unangetastet
- Skalierbares Design (weitere Städte einfach integrierbar)

### Tech-Stack

| Kategorie | Technologien |
|---|---|
| Web-App | Streamlit, Plotly |
| Datenverarbeitung | pandas, NumPy |
| Machine Learning | scikit-learn (Random Forest, Regression) |
| Datenbeschaffung | Open-Meteo API, UBA API, Meteostat, Destatis |
| Umgebung | Python 3.x, Jupyter Notebooks |

### Projektstruktur

```
Abschlussprojekt/
│
├── 01_extract/                  # Datenbeschaffung & Import
│   ├── import_meteostat_pandas.ipynb
│   └── df_colums.ipynb
│
├── 02_transform/                # EDA, Feature Engineering & Modelltraining
│   ├── 01_EDA_und_Feature_Engineering.ipynb
│   ├── 02_Model_Training_und_Evaluation.ipynb
│   ├── 03_Model_Export_Pipeline.ipynb
│   ├── random_forest.py
│   └── regression_analyse.py
│
├── 03_app/                      # Streamlit-Webanwendung
│   ├── app.py                   # Haupt-App
│   ├── requirements.txt         # Abhängigkeiten
│   ├── .streamlit/config.toml   # Theme-Konfiguration
│   └── data/                   # Verarbeitete Datensätze (CSV)
│
├── docs/                        # Projektdokumentation
├── nogithub/                    # Lokale Skripte (nicht im Repo)
└── README.md
```

### Installation & Ausführung

**Voraussetzungen:** Python 3.8+

```bash
# 1. Repository klonen
git clone https://github.com/fhasdorf/Abschlussprojekt_DSI202512.git
cd Abschlussprojekt_DSI202512

# 2. Virtuelle Umgebung erstellen und aktivieren
python -m venv dsi_env
# Windows:
dsi_env\Scripts\activate
# macOS/Linux:
source dsi_env/bin/activate

# 3. Abhängigkeiten installieren
pip install -r 03_app/requirements.txt

# 4. Streamlit-App starten
streamlit run 03_app/app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`.

### Datenquellen

| Quelle | Inhalt |
|---|---|
| [Umweltbundesamt (UBA)](https://www.umweltbundesamt.de/) | Schadstoffmessdaten (O₃, NO₂, PM10) – Station Nürnberg |
| [Open-Meteo Historical Archive API](https://open-meteo.com/) | Stündliche Wetterdaten 1980–2026 (Temperatur, Luftfeuchtigkeit, Strahlung) |
| [Meteostat](https://meteostat.net/) | Ergänzende meteorologische Daten |
| [Destatis](https://www.destatis.de/) | Statistische Referenzdaten |

### Autoren

| Name | Rolle |
|---|---|
| Christina Dürrbeck | Datenanalyse & Modellierung |
| Markus Edelhoff | Feature Engineering & Auswertung |
| Frank Hasdorf | App-Entwicklung & Architektur |

---

## English

### Project Description

This project analyzes the relationship between weather conditions and air pollutant concentrations (Ozone O₃, Nitrogen Dioxide NO₂, Particulate Matter PM10) in the city of Nuremberg, Germany. It is based on hourly measurement data from 1980 to 2026 (~400,000 records).

The result is an interactive **Streamlit dashboard** that visualizes time series, WHO threshold comparisons, and machine-learning-based trend analyses.

### Features

- Interactive time series charts with year slider (1980–2026)
- Comparison of measured annual averages against WHO limit values
- Correlation analysis: temperature, humidity, solar radiation vs. pollutants
- Random Forest model for feature importance analysis
- Fully automated ETL pipeline – raw data remains untouched
- Scalable design (additional cities can be easily integrated)

### Tech Stack

| Category | Technologies |
|---|---|
| Web App | Streamlit, Plotly |
| Data Processing | pandas, NumPy |
| Machine Learning | scikit-learn (Random Forest, Regression) |
| Data Sources | Open-Meteo API, UBA API, Meteostat, Destatis |
| Environment | Python 3.x, Jupyter Notebooks |

### Project Structure

```
Abschlussprojekt/
│
├── 01_extract/                  # Data extraction & import
│   ├── import_meteostat_pandas.ipynb
│   └── df_colums.ipynb
│
├── 02_transform/                # EDA, feature engineering & model training
│   ├── 01_EDA_und_Feature_Engineering.ipynb
│   ├── 02_Model_Training_und_Evaluation.ipynb
│   ├── 03_Model_Export_Pipeline.ipynb
│   ├── random_forest.py
│   └── regression_analyse.py
│
├── 03_app/                      # Streamlit web application
│   ├── app.py                   # Main app
│   ├── requirements.txt         # Dependencies
│   ├── .streamlit/config.toml   # Theme configuration
│   └── data/                   # Processed datasets (CSV)
│
├── docs/                        # Project documentation
├── nogithub/                    # Local scripts (not tracked in repo)
└── README.md
```

### Installation & Usage

**Prerequisites:** Python 3.8+

```bash
# 1. Clone the repository
git clone https://github.com/fhasdorf/Abschlussprojekt_DSI202512.git
cd Abschlussprojekt_DSI202512

# 2. Create and activate a virtual environment
python -m venv dsi_env
# Windows:
dsi_env\Scripts\activate
# macOS/Linux:
source dsi_env/bin/activate

# 3. Install dependencies
pip install -r 03_app/requirements.txt

# 4. Launch the Streamlit app
streamlit run 03_app/app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

### Data Sources

| Source | Content |
|---|---|
| [Umweltbundesamt (UBA)](https://www.umweltbundesamt.de/) | Air pollutant measurements (O₃, NO₂, PM10) – Nuremberg station |
| [Open-Meteo Historical Archive API](https://open-meteo.com/) | Hourly weather data 1980–2026 (temperature, humidity, radiation) |
| [Meteostat](https://meteostat.net/) | Supplementary meteorological data |
| [Destatis](https://www.destatis.de/) | Statistical reference data |

### Authors

| Name | Role |
|---|---|
| Christina Dürrbeck | Data Analysis & Modelling |
| Markus Edelhoff | Feature Engineering & Evaluation |
| Frank Hasdorf | App Development & Architecture |

---

*Abschlussprojekt – Data Science Institut, Abschlussklasse Dezember 2025*
