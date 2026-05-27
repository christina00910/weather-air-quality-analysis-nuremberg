# Zeitliche analyse Rush Hour / Wochenende / Jahreszeit

# Bibliotheken laden
import pandas as pd
import matplotlib.pyplot as plt

# Daten laden
df = pd.read_csv("02_transform/Schadstoff_Wetter.csv")

# Datum umwandeln
df["datum"] = pd.to_datetime(df["datum"])

# Zielvariable festlegen
schadstoff = "no2"

# Zeitvariablen erstellen
df["wochentag"] = df["datum"].dt.dayofweek
df["monat"] = df["datum"].dt.month
df["wochenende"] = df["wochentag"].isin([5, 6]).astype(int)
df["rush_hour"] = df["stunde"].isin([6,7,8,9,16,17,18,19]).astype(int)

# Jahr 1993 filtern
df_1993 = df[df["datum"].dt.year == 1993]

# Erste Zeilen anzeigen
print(df_1993.head())

# Allgemeine Infos
print(df_1993.info())

# Fehlende Werte prüfen
print(df_1993.isna().sum())

# Statistische Übersicht
print(df_1993.describe())

# Anzahl Zeilen prüfen
print("Anzahl Zeilen:", len(df_1993))

# Durchschnittlicher NO2-Wert pro Jahr
print(df.groupby(df["datum"].dt.year)["no2"].mean())

# Monatsmittelwerte für 1993
df_1993["monat"] = df_1993["datum"].dt.month
print(df_1993.groupby("monat")["no2"].mean())


# ------------------------------------------------------------
# Wettervergleich 1993 vs. 1994
# Ziel: Prüfen, ob das auffällige NO2-Tief im Jahr 1993
# möglicherweise mit besonderen Wetterbedingungen zusammenhängt.
# ------------------------------------------------------------

# Vergleichsjahre festlegen
vergleichsjahre = [1993, 1994]

# Wettervariablen auswählen
wetter_variablen = [
    "temperatur",
    "windgeschwindigkeit",
    "luftdruck",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung",
    "no2"]

# Daten für 1993 und 1994 filtern
vergleich_df = df[df["datum"].dt.year.isin(vergleichsjahre)].copy()

# Jahr erstellen
vergleich_df["jahr"] = vergleich_df["datum"].dt.year

# Jahresmittelwerte berechnen
wettervergleich = vergleich_df.groupby("jahr")[wetter_variablen].mean()

# Ergebnisse anzeigen
print("Wettervergleich 1993 vs. 1994")
print(wettervergleich)

# ------------------------------------------------------------
# Grafik erstellen
# ------------------------------------------------------------

for variable in wetter_variablen:
    plt.figure(figsize=(6, 5))
    plt.bar(
        wettervergleich.index.astype(str),
        wettervergleich[variable])

    plt.title(f"{variable}: Jahresmittel 1993 vs. 1994")
    plt.xlabel("Jahr")
    plt.ylabel(f"Durchschnitt {variable}")

    plt.tight_layout()
    plt.show()

    # Monatliche Mittelwerte vergleichen

vergleich_monate = (
    df[df["datum"].dt.year.isin([1993, 1994])]
    .groupby([df["datum"].dt.year, df["datum"].dt.month])["no2"]
    .mean()
    .unstack(0))

print(vergleich_monate)
vergleich_monate.plot(figsize=(12,6))
plt.title("NO2-Monatsmittelwerte: 1993 vs. 1994")
plt.xlabel("Monat")
plt.ylabel("NO2 [µg/m³]")
plt.grid()
plt.show()

print(df[df["datum"].dt.year == 1993]["no2"].head(50))
print(df[df["datum"].dt.year == 1993]["no2"].describe())
print(df[df["datum"].dt.year == 1994]["no2"].describe())
plt.figure(figsize=(12,6))
df[df["datum"].dt.year == 1993]["no2"].hist(
    bins=30,
    alpha=0.5,
    label="1993")
df[df["datum"].dt.year == 1994]["no2"].hist(
    bins=30,
    alpha=0.5,
    label="1994")
plt.xlabel("NO2 [µg/m³]")
plt.ylabel("Häufigkeit")
plt.title("Verteilung NO2: 1993 vs. 1994")
plt.legend()
plt.show()