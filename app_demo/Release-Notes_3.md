# 🛠️ Update- & Funktionsbeschreibung: Data Wrangling, Tab 2 & Data Mapping

Dieses Update markiert den Übergang von der reinen Datenbeschaffung zur echten **Data-Science-Analyse**. Wir haben die historischen Wetterdaten erfolgreich mit den Schadstoffwerten verknüpft, das Dashboard um den analytischen zweiten Tab erweitert und einen Übersetzungs-Layer für neue Datenquellen integriert.

## 1. Neu: Data Mapping & Harmonisierung (Translation Layer)
Unterschiedliche Datenquellen (z. B. Meteostat vs. DWD-Direktdownloads) nutzen oft verschiedene Spaltennamen und Formate. Um den Code des Dashboards stabil zu halten, wurde ein "Translation Layer" beim Laden der Daten integriert:
* **Spalten-Renaming:** Mithilfe eines Dictionaries (`rename_logic`) werden abweichende Spaltennamen (wie `Temperatur` oder `Windgeschwindigkeit`) beim Laden automatisch in die vom Dashboard erwarteten internen Variablen (wie `Temperatur_C` oder `Wind_kmh`) übersetzt.
* **Datetime-Parsing:** Spezielle Datumsformate in den Rohdaten (wie `1955040700` für Jahr-Monat-Tag-Stunde) werden nun über das Argument `format='%Y%m%d%H'` präzise in echte Pandas-Datetime-Objekte umgewandelt.
* **Vorteil:** Neue oder abweichende Datensätze können nun einfach in den `data/`-Ordner gelegt werden, ohne dass die nachgelagerte Machine-Learning-Logik oder die Graphen-Architektur umgeschrieben werden müssen.

## 2. Data Wrangling: Die Daten-Hochzeit (`pd.merge`)
Damit Machine-Learning-Algorithmen später lernen können, müssen Wetter und Luftqualität in derselben Zeile stehen. 
* **Funktion:** `load_and_merge_data()`
* **Logik:** Wir nutzen einen `Inner Join` über die Spalte `Datum_Uhrzeit`. Pandas sucht sich exakt die Stunden heraus, für die wir *sowohl* Wetter- *als auch* UBA-Schadstoffdaten haben, und verschmilzt sie zu einem finalen DataFrame (`df_main`).

## 3. Ausfallsicherheit (Dummy-Data-Fallback)
Um zu verhindern, dass die App abstürzt, wenn Teammitglieder die UBA-CSV (`luftdaten_nurnberg.csv`) noch nicht lokal in ihrem `data`-Ordner liegen haben, wurde ein `try-except`-Block eingebaut:
* Findet die App die echte Datei nicht, generiert sie temporär realistische **Mock-Daten** (z. B. Ozonwerte, die bei hoher Temperatur steigen). 
* **Vorteil:** Die App und das Layout bleiben für alle Entwickler im Team jederzeit testbar.

## 4. Visuelle Analyse (Tab 2: Schadstoff-Analyse)
Der zweite Tab ist nun live und bietet interaktive Einsichten in das Verhalten der Schadstoffe.

### A. Der Zeitverlauf (Line Chart)
* **Darstellung:** Ein klassischer Plotly-Line-Chart über das ausgewählte Jahr.
* **Zweck:** Dient der Identifikation von saisonalen Mustern (z. B. "Gibt es im Hochsommer mehr Ozon-Spitzen?").

### B. Die Wetter-Korrelation (Scatter Plot mit Trendlinie)
* **Darstellung:** Ein Streudiagramm (Scatter Plot), bei dem die X-Achse dynamisch auf das wichtigste Wetter-Feature des gewählten Schadstoffs reagiert (Temperatur für Ozon, Wind für NO₂).
* **Zweck:** Das ist der wichtigste analytische Schritt! Die automatisch berechnete Trendlinie (OLS - Ordinary Least Squares) zeigt visuell, ob und wie stark das Wetter die Luftqualität treibt. 
* **Data Science Insight:** Wenn sich hier klare Cluster oder steile Linien zeigen, wissen wir sicher, dass unser Machine-Learning-Modell in Tab 3 hervorragende Vorhersagen treffen wird.
