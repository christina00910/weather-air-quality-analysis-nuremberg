# Analyse und Vorhersage von Wetter- und Luftqualitätsdaten in Nürnberg

## Projektbeschreibung

Dieses Projekt untersucht den Zusammenhang zwischen meteorologischen Einflussfaktoren und der Luftqualität in Nürnberg.

Dazu wurden historische Wetterdaten des Deutschen Wetterdienstes (DWD) mit Luftschadstoffdaten des Bayerischen Landesamtes für Umwelt (LfU) zusammengeführt, aufbereitet und analysiert.

Im Fokus stehen die Luftschadstoffe:

- Ozon (O₃)
- Stickstoffdioxid (NO₂)
- Feinstaub PM10
- Feinstaub PM2.5

Zur Analyse werden verschiedene statistische Verfahren sowie Machine-Learning-Modelle eingesetzt. Zusätzlich wurde eine interaktive Streamlit-Webanwendung entwickelt.

### Datengrundlage

- Analysezeitraum: 1980–2024
- Messintervall: Stündliche Messdaten
- Untersuchungsregion: Nürnberg
- PM2.5-Daten vollständig verfügbar ab 2008

---

## Projektziele

- Untersuchung des Zusammenhangs zwischen Wetter und Luftqualität
- Analyse meteorologischer Einflussfaktoren
- Vorhersage von Luftschadstoffkonzentrationen
- Entwicklung einer interaktiven Analyseplattform

---

## Projektstruktur

```text
Abschlussprojekt_DSI202512_Final
│
├── app                  # Streamlit-Anwendung
│   ├── app.py           # Hauptdatei der App
│   ├── data             # Verarbeitete Datensätze
│   ├── Bilder           # Bildmaterial für die App
│   └── .streamlit       # Streamlit-Konfiguration
│
├── datenbeschaffung     # Datenimport und Datenquellen
├── datenaufbereitung    # Datenbereinigung, Transformation und Modellierung
└── README.md
```

---

## Verwendete Datenquellen

### Deutscher Wetterdienst (DWD)

- Temperatur
- Windgeschwindigkeit
- Windrichtung
- Luftdruck
- Relative Luftfeuchtigkeit
- Niederschlagshöhe
- Sonnenscheindauer
- Gesamtbewölkung

### Bayerisches Landesamt für Umwelt (LfU)

- Ozon (O₃)
- Stickstoffdioxid (NO₂)
- PM10
- PM2.5

### Open-Meteo API

Aktuelle Wetterdaten für die Live-Prognose

---

## Eingesetzte Methoden

### Explorative Datenanalyse

- Jahresverläufe
- Saisonale Muster
- Rush-Hour-Effekte
- Inversionslagen
- Wochenendanalysen
- Silvester-Effekt

### Korrelationsanalyse

Analyse der Zusammenhänge zwischen Wettervariablen und Luftschadstoffen.

### Multiple lineare Regression

Statistische Untersuchung signifikanter Einflussfaktoren.

### Random Forest

Bestimmung wichtiger Einflussgrößen und Vorhersagemodellierung.

### Vorhersagemodelle

- Random Forest Regressor
- XGBoost Regressor
- Zeitreihen-Lags historischer Schadstoffwerte
- Live-Prognosen auf Basis aktueller Wetterdaten der Open-Meteo API

---

## Dashboard-Funktionen

- Startseite
- Wetterdaten
- Explorative Analyse
- Korrelationsanalyse
- Multiple Regression
- Random Forest
- Vorhersage Live
- Vorhersage
- Fazit
- Technische Insights

---

## Verwendete Technologien

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- Scikit-Learn
- XGBoost
- Streamlit
- Open-Meteo API

---

## Projektteam

- Christina Dürbeck
- Markus Edelhoff

Data Science Institute  
Abschlussprojekt Mai 2026

---

## Anwendung starten

```bash
pip install -r app/requirements.txt
streamlit run app/app.py