
## Datenbasis & Datenbeschaffung (Data Sourcing)

Die Modellierung basiert auf einer Kombination aus historischen Wetterdaten und atmosphärischen Reanalysen, die über die **Open-Meteo API** (lizenzfrei für nicht-kommerzielle Nutzung, basierend auf Open-Data-Quellen) bezogen wurden.

### 1. Datenquellen & APIs
Aufgrund der unterschiedlichen Datenstruktur und Speicherorte wurden zwei separate Endpoints abgefragt und über den Zeitstempel (`timestamp`) zusammengeführt:

* **Meteorologische Treiber (Features):** 
  * **API:** `Historical Weather API` (`/v1/archive`)
  * **Datenbasis:** ERA5 und ERA5-Land Reanalysen (ECMWF).
  * **Variablen:** Temperatur ($2m$), relative Luftfeuchtigkeit, Direktstrahlung, Diffusstrahlung und Globalstrahlung (`shortwave_radiation`).
* **Luftschadstoffe & Zielvariablen:** 
  * **API:** `Air Quality API` (`/v1/air-quality`)
  * **Datenbasis:** CAMS (Copernicus Atmosphere Monitoring Service) Regional- und Globalkomponenten.
  * **Variablen:** $PM_{10}$, $PM_{2.5}$, Stickstoffdioxid ($NO_2$), Kohlenmonoxid ($CO$) und Ozon ($O_3$).

### 1.a. Zeitlicher Rahmen & Einschränkungen
* **Untersuchungszeitraum:** `2013-01-01` bis `[DEIN_ENDDATUM_HIER, z.B. 2023-12-31]`
* **Zeitliche Auflösung:** Stündlich (`hourly`)
* **Zeitzone:** `Europe/Berlin` (inkl. automatischer Berücksichtigung von Sommer-/Winterzeit)

> **⚠️ Wichtiger methodischer Hinweis (Data Science Insight):** 
> Während reine Wetterdaten (ERA5) lückenlos bis ins Jahr 1940 zurückreichen, stehen die hochwertigen, europäisch validierten Luftschadstoff-Reanalysen des Copernicus-Dienstes (CAMS) erst **ab dem Jahr 2013** verlässlich zur Verfügung. Für ein valides Feature-Engineering (Kombination aus Chemie und Wetter) ist das Startjahr des Gesamtdatensatzes daher fix auf 2013 begrenzt.

### 1.b.. Einheiten & Datenvorbereitung
* Alle Gase und Feinstäube ($PM_{10}, PM_{2.5}, NO_2, O_3$) werden standardmäßig in **$\mu g/m^3$** (Mikrogramm pro Kubikmeter) ausgegeben; Kohlenmonoxid ($CO$) in **$\mu g/m^3$**.
* Fehlende Werte (bedingt durch kleinere API-Ausfälle oder Reanalyse-Lücken) wurden im Zuge der Pipeline überprüft und [ergänze hier kurz deine Methode, z.B. *mittels linearer Interpolation bereinigt*].






## 2. Dynamische Datenerweiterung im RAM (Spalte: `Stadt`)

**Der Fallstrick:** Das manuelle Bearbeiten von Roh-CSV-Dateien bricht die Automatisierungskette (ETL) und macht das System starr für zukünftige Erweiterungen (z. B. Integration von München oder Augsburg).

**Die Lösung:** Die Spalte `Stadt` wird live während des Ladeprozesses in der Funktion `load_data()` im Arbeitsspeicher (RAM) erzeugt:

```python
df['Stadt'] = 'Nürnberg'
```

Durch die Manipulation der Spaltenliste mittels `cols.remove('Stadt')` und `cols.insert(1, 'Stadt')` wird die Spalte dynamisch an die zweite Position verschoben, direkt neben die Stationsnummer.

> **Präsentations-Nutzen:** Nachweis von vorausschauendem Software-Design (Skalierbarkeit). Die Datenpipeline bleibt komplett automatisiert, die Rohdaten unangetastet. Bei einer Erweiterung auf andere Städte muss kein Datensatz händisch manipuliert werden.

---

## 3. Die Filter-Bedingung des Sliders

```python
df['Datum_Uhrzeit'].dt.year == selected_year
df['Datum_Uhrzeit']: Greift auf die Spalte zu, in der unsere Datumsangaben stehen.
```
*.dt.year* ist ein sogenannter Accessor. Er sagt Pandas: „Behandle diese Spalte wie ein Datum und ziehe mir von jedem Eintrag nur das Kalenderjahr heraus“ (z. B. 2026).

*== selected_year* vergleicht jedes dieser Jahre mit der Variable *selected_year* (das Jahr, das der Nutzer im Slider angeklickt hat). Das Ergebnis ist eine Liste von True (Jahr stimmt überein) und False (Jahr stimmt nicht überein).

### 3.a. Das Filtern (Die äußere Klammer)
```Python
df[...]
```
Pandas nutzt diese True/False-Liste ales *booleschen Filter*. Es wirft alle Zeilen raus, die False sind, und behält nur die Zeilen, bei denen die Bedingung True war.

### 3.b. Das .copy() am Ende

```Python
.copy()
```
Das ist ein wichtiger Best-Practice-Schritt in Pandas. Ohne .copy() hätten wir nur eine „Sicht“ (eine Verknüpfung) auf den alten Datensatz. Wenn wir später versuchen, df_year zu verändern, würde Pandas eine Warnung ausgeben (SettingWithCopyWarning). Das .copy() erstellt einen komplett neuen, unabhängigen Datensatz im Arbeitsspeicher.

Wichtig für Streamlit: Da diese Zeile jedes Mal von oben nach unten ausgeführt wird, wenn ein Nutzer den Slider bewegt, sorgt sie dafür, dass unsere Diagramme oder Tabellen darunter blitzschnell und dynamisch aktualisiert werden.

---

## 4. Dynamische Slider-Grenzen mittels Datetime-Auswertung

**Der Fallstrick:** Werden die Min- und Max-Werte eines Jahres-Sliders fest im Quellcode verankert (Hardcoding, z. B. `min_value=1980`, `max_value=2024`), stürzt die App ab, wirft Fehler oder ignoriert Daten, sobald der Datensatz in der Zukunft erweitert wird.

**Die Lösung:** Nach dem Parsen der Datetime-Spalte ermittelt Pandas die Grenzen vollautomatisch aus den Echtdaten:

```python
min_year = int(df['Datum_Uhrzeit'].dt.year.min())
max_year = int(df['Datum_Uhrzeit'].dt.year.max())
```

> **Präsentations-Nutzen:** Die App ist absolut wartungsfrei. Kommen neue historische Daten oder zukünftige Jahre hinzu, passt sich das User Interface (der Slider) beim nächsten Start der App vollautomatisch an – ohne dass eine einzige Zeile Code geändert werden muss.

---

## 5. Optisches Feintuning: `config.toml` vs. CSS-Injection

**Der Fallstrick:** Streamlits Standard-Design sieht für wissenschaftliche Dashboards oft zu großflächig aus. Die Standard-KPI-Karten (`st.metric`) nehmen extrem viel Platz weg. Standardthemen lassen sich über die `config.toml` nur grob steuern (Hintergrundfarbe, Primärfarbe), nicht aber auf granularer Elementebene.

**Die Lösung:** Für das globale App-Thema wird die `config.toml` genutzt. Für chirurgisch präzises Anpassen von Schriftgrößen und Abständen wird gezielt CSS über `st.markdown(..., unsafe_allow_html=True)` direkt in die jeweiligen Tabs injiziert:

```css
    st.markdown(
        f"""
        <div style="background-color: rgba(3, 149, 176, 0.1); padding: 12px; border-radius: 0.5rem; border: 1px solid rgba(1, 132, 157, 0.8);">
            <span style="font-family: 'Courier New', Courier, monospace; font-size: 11px; color: #FAFAFA;">
                ✅ Daten erfolgreich geladen: {len(df):,} Zeilen!
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
```

> **Präsentations-Nutzen:** Nachweis von fortgeschrittenem UI/UX-Engineering. Framework-Limitierungen werden sauber umgangen, um eine kompakte, professionelle Datendichte zu erzielen, die auf Dashboards im Industrie-Standard abgestimmt ist.

---

## 6. Die `if-elif`-Logik in Tab 2 & Invertierte Delta-Farben

### 6.a. Das Re-Rendering-Problem bei verschachtelten Strukturen

In traditionellen Web-Frameworks müsste man komplexe Event-Listener in JavaScript schreiben, um Inhalte dynamisch auszutauschen. Streamlit arbeitet radikal anders: Sobald ein UI-Element (z. B. ein Radio-Button) bedient wird, läuft das gesamte Skript von oben nach unten neu durch. Durch die `if-elif`-Struktur:

```python
if schadstoff_auswahl == "Übersicht aller Stoffe":
    # zeige WHO-Metriken und globale Auswertungen
elif schadstoff_auswahl == "Ozon (O₃)":
    # zeige spezifische Ozon-Grafiken
```

…wird das Rendering hocheffizient gesteuert. Es wird im Arbeitsspeicher nur der HTML-Code für das aktive Unterthema generiert – das spart Rechenleistung im Browser des Nutzers und hält das Interface übersichtlich.

### 6.b. Die „Börsenkurs-Inversion" bei Umweltmetriken

Standardmäßig interpretiert `st.metric` einen positiven Delta-Wert als *gut/steigend* (grün) und einen negativen als *schlecht/sinkend* (rot) – perfekt für Aktienkurse oder Umsatzstatistiken.

Bei Schadstoffen gilt jedoch das genaue Gegenteil: **Mehr Schadstoffe sind ein Alarmzeichen!**

| Situation | Differenz | Gewünschte Farbe |
|---|---|---|
| Jahresmittelwert **über** WHO-Limit | positiv (+4,2 µg/m³) | Dreieck hoch, **ROT** |
| Jahresmittelwert **unter** WHO-Limit | negativ (−5,1 µg/m³) | Dreieck runter, **GRÜN** |

Die technische Umsetzung:

```python
diff_ozon = mean_ozon - 100  # positiv bei Überschreitung

c1.metric(
    label="Ø Ozon (Ziel: ≤100)",
    value=f"{mean_ozon:.1f} µg/m³",
    delta=f"{diff_ozon:+.1f} µg/m³ vs. WHO",
    delta_color="inverse"  # Plus = Rot, Minus = Grün
)
```

> **Präsentations-Nutzen:** Exzellentes Beispiel für fachspezifische Anpassung. Es wird der Prüfungskommission bewiesen, dass Business-Logiken (Umweltrichtwerte) vollständig verstanden und in technische Parameter (`delta_color="inverse"`) übersetzt wurden.

---

## 7. Kaskadierende Filterung: Slider, RAM-Kopie und Unter-Tabs

Die Daten werden im RAM hierarchisch in drei Stufen gefiltert:

| Stufe | Auslöser | Aktion |
|---|---|---|
| **1 – Global** | App-Start | Gesamtdatensatz (~400.000 Zeilen) wird via `@st.cache_data` unveränderlich gecacht |
| **2 – User-Interaktion** | Slider-Bewegung | `df_year = df[df[...]].copy()` erstellt eine isolierte Jahreskopie im RAM; `.copy()` unterdrückt `SettingWithCopyWarning` |
| **3 – Lokal in Tab 2** | Radio-Button-Klick | `if-elif`-Logik greift blitzschnell auf das bereits vorgefilterte `df_year` zu |

**Der Vorteil:** Wechselt der Nutzer zwischen „Ozon" und „Feinstaub", muss nicht neu gefiltert werden – die Daten für das gewählte Jahr stehen bereits im RAM bereit. Erst eine Slider-Bewegung triggert ein neues globales Re-Rendering.

> **Präsentations-Nutzen:** Nachweis von tiefem Verständnis für Performance-Optimierung, State-Management und RAM-Ressourcenschonung in modernen Web-Apps.


## 8. Technische Insights: Speicherstrategie & Performance-Optimierung

### Ausgangslage & Hybrid-Architektur
Für die Plattform wird ein hybrider Speicheransatz implementiert, der nun auf **zwei getrennten Datengrundlagen** basiert:
1. **Basis-CSV:** Wird weiterhin für die allgemeinen Kernfunktionen und Standard-Datenstrukturen der Anwendung genutzt.
2. **Parquet-Datei (Ozon-Tab):** Wird exklusiv für das Analyse-Modul des *Ozon-Paradoxons* eingesetzt. Da hier massiv verdichtete, stündliche Klimadaten seit 1980 für den Stadt-Land-Vergleich (Nürnberg vs. Schleswig) verarbeitet werden, stößt das CSV-Format an funktionale Grenzen. Der Wechsel auf ein spaltenorientiertes Format löst die daraus resultierenden Performance-Engpässe.

---

### Die Vorteile von Parquet im Ozon-Modul

#### 1. Speicherkapazität (Komprimierung)
CSV-Dateien speichern Daten zeilenweise als Klartext ab, was bei Millionen von Zeilen zu immensem Overhead führt. Parquet nutzt eine **spaltenorientierte (columnar) Speicherarchitektur**. Da in einer Spalte immer derselbe Datentyp liegt (z. B. Fließkommazahlen für die Temperatur), greifen Komprimierungsalgorithmen (wie Snappy) extrem effizient. 
* **Effekt:** Die Dateigröße schrumpft im Vergleich zu einer unkomprimierten CSV um **70–90 %**. Das schont den lokalen Festplattenspeicher und reduziert den RAM-Verbrauch beim Einlesen drastisch.

#### 2. Ladezeitvorteil & Streamlit-Performance
In Streamlit führt jede Benutzerinteraktion (z. B. das Umschalten zwischen Nürnberg und Schleswig) zu einem vollständigen Rerun des Skripts. 
* **I/O-Schnittgeschwindigkeit:** Während bei einer CSV immer die *gesamte* Datei sequenziell von der Festplatte gelesen werden muss, erlaubt Parquet das gezielte Laden einzelner Spalten (`columns=['timestamp', 'stadt', 'temperatur_c']`). 
* **Typsicherheit:** Zeitaufwendiges Parsen von Datums- und Zeitzonen-Strings entfällt komplett. Das vordefinierte Schema übergibt die Datentypen nativ an Pandas. Das Laden und Filtern der Daten geschieht in Streamlit dadurch nahezu **in Echtzeit (Faktor 10x bis 100x schneller als CSV)**.

#### 3. Nahtlose Skalierung in der Cloud (AWS Athena)
Für eine spätere Überführung des Projekts in eine Cloud-Infrastruktur legt Parquet das fundamentale Design fest:
* **Serverless Analytics mit AWS Athena:** Athena berechnet die Abfragekosten exklusiv basierend auf der Menge der von S3 gescannten Daten. 
* **Kosteneffizienz in der Praxis:** Führt man eine SQL-Abfrage aus, die nur den Mittelwert der Temperatur berechnet, scannt Athena dank des spaltenbasierten Parquet-Formats auch *nur diese eine Spalte* (und überspringt Windrichtung, Strahlung etc.). Zusammen mit der starken Komprimierung senkt dies die Datenmenge pro Abfrage im Vergleich zu CSV oft um **über 90 %**, was die Cloud-Infrastruktur extrem kosteneffizient und performant macht.