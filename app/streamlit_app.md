# 🌬️ Luftqualität & Wetter Dashboard (Bayern)

Dieses Streamlit-Dashboard ist das interaktive Frontend eines Data-Science-Projekts zur Analyse historischer Wetter- und Luftqualitätsdaten in Bayern (1980–2023). Es verbindet meteorologische Messwerte mit Schadstoffdaten, um Umweltfaktoren visuell zu explorieren und durch Machine-Learning-Modelle vorherzusagen.

## 🚀 Kernfunktionen & Aufbau

Die App ist in eine globale Seitenleiste zur Steuerung und drei analytische Hauptbereiche (Tabs) unterteilt:

### ⚙️ Globale Filter (Sidebar)
* **Dynamische Datenauswahl:** Filterung der gesamten Analyse nach spezifischen Städten (z. B. Nürnberg, München) und Jahren über interaktive Slider.
* **Performance-Optimierung:** Effizientes Caching (`@st.cache_data`) der umfangreichen historischen Datensätze (ca. 400.000 Zeilen pro Stadt), um flüssige Interaktionen zu gewährleisten.

### 📊 Tab 1: Wetter-Exploration
* **KPI-Metriken:** Schneller Überblick über Jahresdurchschnittstemperaturen und Windspitzen.
* **Zeitreihenanalyse:** Interaktiver Plotly-Graph zur Visualisierung des stündlichen Temperatur- und Wetterverlaufs eines ausgewählten Jahres.
* **Rohdaten-Inspektion:** Optionales Einblenden des zugrundeliegenden Pandas-DataFrames für Transparenz.

### 🧪 Tab 2: Schadstoff-Analyse *(in Entwicklung)*
* **Visualisierung der Luftqualität:** Analyse von Feinstaub (PM2.5, PM10), Stickstoffdioxid (NO₂) und Ozon (O₃).
* **Mustererkennung:** Identifikation saisonaler und tageszeitlicher "Fingerabdrücke" (z. B. Rush-Hour-Peaks oder hitzegetriebene Ozonbildung).

### 🤖 Tab 3: ML-Labor *(in Entwicklung)*
* **Prädiktive Modellierung:** Einsatz von Regressionsmodellen (wie Random Forest) zur Vorhersage von Schadstoffkonzentrationen basierend auf Wetterparametern.
* **Feature Importance:** Visuelle Auswertung, welche Faktoren (Sonnenschein, Wind, Temperatur) den stärksten Einfluss auf die Luftqualität haben.

---

## 🛠️ Tech Stack & Datenquellen
* **Frontend/App:** Streamlit
* **Datenverarbeitung:** Pandas, Datetime
* **Visualisierung:** Plotly Express
* **Machine Learning:** Scikit-Learn (geplant)
* **Datenquellen:** * Wetterdaten: Deutscher Wetterdienst (DWD) via `meteostat`
  * Luftdaten: Umweltbundesamt (UBA) / European Environment Agency (EEA)