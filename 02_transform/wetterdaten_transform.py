import pandas as pd

#Wetterdatensätze laden
#Temperatur
temperatur = pd.read_csv("Temperatur_stundenwerte/Temperatur.txt", sep=";")
print(temperatur.head())

# Windgeschwindigkeit
windgeschwindigkeit = pd.read_csv("Windgeschwindigkeit_stundenwerte/Windgeschwindigkeit.txt", sep=";")
print(windgeschwindigkeit.head())

# Luftfeuchtigkeit
luftfeuchtigkeit = pd.read_csv("Luftfeuchtigkeit_stundenwerte/Luftfeuchtigkeit.txt", sep=";")
print(luftfeuchtigkeit.head())

# Niederschlag
niederschlag = pd.read_csv("Niederschlag_stundenwerte/Niederschlag.txt", sep=";")
print(niederschlag.head())

# Sonneneinstrahlung
sonneneinstrahlung = pd.read_csv("Sonneneinstrahlung_stundenwerte/Sonneneinstrahlung.txt", sep=";")
print(sonneneinstrahlung.head())

# Bewölkung
bewoelkung = pd.read_csv("Bewoelkung_stundenwerte/Bewoelkung.txt", sep=";")
print(bewoelkung.head())

# Leerzeichen und versteckte Abstände in Spalten entfernen
temperatur.columns = temperatur.columns.str.strip()

windgeschwindigkeit.columns = windgeschwindigkeit.columns.str.strip()

luftfeuchtigkeit.columns = luftfeuchtigkeit.columns.str.strip()

niederschlag.columns = niederschlag.columns.str.strip()

sonneneinstrahlung.columns = sonneneinstrahlung.columns.str.strip()

bewoelkung.columns = bewoelkung.columns.str.strip()

# Spalten Temparatur umbennen 
temperatur = temperatur.rename(columns={
    "STATIONS_ID": "Stations_ID",
    "MESS_DATUM": "Datum",
    "QN_9": "Qualitaetsniveau_Temperatur",
    "TT_TU": "Temperatur",
    "RF_TU": "Luftfeuchtigkeit"})
print(temperatur.columns)

# Spalten Windgeschwindigkeit umbenennen
windgeschwindigkeit = windgeschwindigkeit.rename(columns={
    "STATIONS_ID": "Stations_ID",
    "MESS_DATUM": "Datum",
    "QN_3": "Qualitaetsniveau_Windgeschwindigkeit",
    "F": "Windgeschwindigkeit",
    "D": "Windrichtung"
})
print(windgeschwindigkeit.columns)

# Spalten Luftfeuchtigkeit umbennen
luftfeuchtigkeit = luftfeuchtigkeit.rename(columns={
    "STATIONS_ID": "Stations_ID",
    "MESS_DATUM": "Datum",
    "QN_8": "Qualitaetsniveau_Luftfeuchtigkeit",
    "ABSF_STD": "Absolute_Feuchtigkeit",
    "VP_STD": "Dampfdruck",
    "TF_STD": "Feuchttemperatur",
    "P_STD": "Luftdruck",
    "TT_STD": "Temperatur_in_2m_Höhe",
    "RF_STD": "Relative_Luftfeuchtigkeit",
    "TD_STD": "Taupunkttemperatur"
})
print(luftfeuchtigkeit.columns)

# Spalten Niederschlag umbenennen
niederschlag = niederschlag.rename(columns={
    "STATIONS_ID": "Stations_ID",
    "MESS_DATUM": "Datum",
    "QN_8": "Qualitaetsniveau_Niederschlag",
    "R1": "Niederschlagshoehe_mm",
    "RS_IND": "Niederschlag_Indikator",
    "WRTR": "Niederschlagsart"
})
print(niederschlag.columns)

# Spalten Sonneneinstrahlung umbenennen
sonneneinstrahlung = sonneneinstrahlung.rename(columns={
    "STATIONS_ID": "Stations_ID",
    "MESS_DATUM": "Datum",
    "QN_7": "Qualitaetsniveau_Sonneneinstrahlung",
    "SD_SO": "Sonnenscheindauer_Minuten"
})
print(sonneneinstrahlung.columns)

# Spalten Bewoelkung umbenennen
bewoelkung = bewoelkung.rename(columns={
    "STATIONS_ID": "Stations_ID",
    "MESS_DATUM": "Datum",
    "QN_8": "Qualitaetsniveau_Bewoelkung",
    "V_N": "Gesamtbewoelkung",
    "V_N_I": "Messart_Bewoelkung"
})
print(bewoelkung.columns)

# Spalte eor (End of Record) entferen
temperatur = temperatur.drop(columns=["eor"], errors="ignore")
windgeschwindigkeit = windgeschwindigkeit.drop(columns=["eor"], errors="ignore")
luftfeuchtigkeit = luftfeuchtigkeit.drop(columns=["eor"], errors="ignore")
niederschlag = niederschlag.drop(columns=["eor"], errors="ignore")
sonneneinstrahlung = sonneneinstrahlung.drop(columns=["eor"], errors="ignore")
bewoelkung = bewoelkung.drop(columns=["eor"], errors="ignore")

# Wetterdatensätze zusammenführen
wetterdaten_komplett = temperatur.merge(windgeschwindigkeit, on=["Stations_ID", "Datum"], how="outer")

wetterdaten_komplett = wetterdaten_komplett.merge(luftfeuchtigkeit, on=["Stations_ID", "Datum"], how="outer")

wetterdaten_komplett = wetterdaten_komplett.merge(niederschlag, on=["Stations_ID", "Datum"], how="outer")

wetterdaten_komplett = wetterdaten_komplett.merge(sonneneinstrahlung, on=["Stations_ID", "Datum"], how="outer")

wetterdaten_komplett = wetterdaten_komplett.merge(bewoelkung, on=["Stations_ID", "Datum"], how="outer")

# Ergebnis anzeigen
print(wetterdaten_komplett.head())

# Alle Spaltennamen anzeigen
print(wetterdaten_komplett.columns)

# Fehlerwerte bereinigen (-999 -> NA)
wetterdaten_komplett = wetterdaten_komplett.replace(-999, pd.NA)
wetterdaten_komplett = wetterdaten_komplett.replace(-999.0, pd.NA)

wetterdaten_komplett.to_csv("wetterdaten_komplett.csv", index=False)

# Analyse-Datensatz mit den wichtigsten Wettervariablen erstellen
wetterdaten_analyse = wetterdaten_komplett[[
    "Datum",
    "Temperatur",
    "Windgeschwindigkeit",
    "Relative_Luftfeuchtigkeit",
    "Niederschlagshoehe_mm",
    "Sonnenscheindauer_Minuten",
    "Gesamtbewoelkung"
]]

# Spalten prüfen
print(wetterdaten_analyse.columns)

# Erste Zeilen anzeigen
print(wetterdaten_analyse.head())

# Analyse-Datensatz als CSV speichern
wetterdaten_analyse.to_csv("wetterdaten_analyse.csv", index=False)