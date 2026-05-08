import requests
import pandas as pd

def fetch_uba_data(station_id, component_id, date_from, date_to):
    """
    Holt Luftqualitätsdaten von der UBA-API und gibt einen Pandas DataFrame zurück.
    """
    # 1. Die Basis-URL der UBA-API (Version 2)
    base_url = "https://www.umweltbundesamt.de/api/air_data/v2/measures/json"
    
    # 2. Parameter für unsere Suchanfrage definieren
    params = {
        "date_from": date_from,   # Startdatum (Format: YYYY-MM-DD)
        "date_to": date_to,       # Enddatum (Format: YYYY-MM-DD)
        "station": station_id,    # ID der Messstation (z.B. 74 für eine Station in München)
        "component": component_id,# Schadstoff-ID (z.B. 5 für NO2)
        "time": "1h"              # Auflösung (z.B. 1h für Stundenwerte, 1SM für Tagesmittel)
    }
    
    print(f"Sende Anfrage an UBA-API für Station {station_id}...")
    
    # 3. Den GET-Request absenden
    response = requests.get(base_url, params=params)
    
    # 4. Prüfen, ob die Anfrage erfolgreich war (HTTP Statuscode 200 = OK)
    if response.status_code == 200:
        json_data = response.json()
        
        # Die UBA-API verschachtelt die eigentlichen Messwerte im Dictionary unter 'data'
        # Wir müssen also etwas tiefer in die Struktur greifen
        try:
            # Extrahiere die Datenstruktur
            raw_data = json_data.get("data", {})
            
            # Die API gibt die Daten oft als verschachteltes Dictionary zurück. 
            # Wir formen das in eine flache Liste um, die Pandas gut lesen kann.
            records = []
            for date, values in raw_data.items():
                # Jeder Eintrag enthält in der Regel die Messwerte als Liste
                if isinstance(values, list) and len(values) >= 3:
                    records.append({
                        "Datum": date,
                        "Wert": values[2], # Der eigentliche Messwert steht meist an Index 2
                    })
                    
            # 5. Umwandlung in einen Pandas DataFrame
            df = pd.DataFrame(records)
            
            # Datumssäule in ein echtes Datetime-Objekt umwandeln (wichtig für spätere Plots!)
            if not df.empty:
                df["Datum"] = pd.to_datetime(df["Datum"])
                
            return df
            
        except KeyError:
            print("Fehler beim Parsen der Datenstruktur.")
            return None
            
    else:
        print(f"Fehler bei der API-Anfrage: HTTP {response.status_code}")
        return None

# ==========================================
# TESTLAUF
# ==========================================
if __name__ == "__main__":
    # Beispiel: Wir holen NO2-Werte (ID 5) für eine spezifische Station für den Januar 2023
    df_no2 = fetch_uba_data(
        station_id=74, 
        component_id=5, 
        date_from="2023-01-01", 
        date_to="2023-01-31"
    )
    
    if df_no2 is not None and not df_no2.empty:
        print("\nDaten erfolgreich geladen! Hier sind die ersten 5 Zeilen:")
        print(df_no2.head())
        
        # Optional: Direkt als CSV für die Streamlit-App speichern
        # df_no2.to_csv("data/raw/uba_no2_jan2023.csv", index=False)
    else:
        print("Keine Daten gefunden.")