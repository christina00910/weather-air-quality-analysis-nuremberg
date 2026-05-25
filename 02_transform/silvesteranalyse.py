# Silvesteranalyse
# Ziel: Analyse der Luftschadstoffbelastung rund um Weihnachten und Silvester.

# ------------------------------------------------------------
# Bibliotheken laden
# ------------------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Daten laden
# ------------------------------------------------------------
df = pd.read_csv("02_transform/data_2.csv")

# ------------------------------------------------------------
# Datum umwandeln
# ------------------------------------------------------------
df["datum"] = pd.to_datetime(df["datum"])

# ------------------------------------------------------------
# Zielvariable festlegen
# Möglich:
# "o3", "no2", "pm10", "pm2x5"
# ------------------------------------------------------------
schadstoff = "pm10"

# ------------------------------------------------------------
# Monat und Tag erstellen
# ------------------------------------------------------------
df["monat"] = df["datum"].dt.month
df["tag"] = df["datum"].dt.day

# ------------------------------------------------------------
# Zeitraum rund um Silvester filtern
# 21.12. bis 07.01.
# ------------------------------------------------------------
silvester_df = df[
    ((df["monat"] == 12) & (df["tag"] >= 21)) |
    ((df["monat"] == 1) & (df["tag"] <= 7))].copy()

# ------------------------------------------------------------
# Hilfsspalte für korrekte Sortierung erstellen
# Dezembertage vor Januartagen
# ------------------------------------------------------------
silvester_df["tag_sort"] = silvester_df.apply(
    lambda row: row["tag"] if row["monat"] == 12 else row["tag"] + 31,
    axis=1)

# ------------------------------------------------------------
# Datum für die Anzeige formatieren
# ------------------------------------------------------------
silvester_df["datum_label"] = silvester_df["datum"].dt.strftime("%d.%m.")

# ------------------------------------------------------------
# Durchschnittswerte pro Tag berechnen
# Über alle verfügbaren Jahre hinweg
# ------------------------------------------------------------
silvester_tagesmittel = silvester_df.groupby(
    ["tag_sort", "datum_label"])[schadstoff].mean().reset_index()

silvester_tagesmittel = silvester_tagesmittel.sort_values("tag_sort")

# ------------------------------------------------------------
# Grafik erstellen
# ------------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(
    silvester_tagesmittel["datum_label"],
    silvester_tagesmittel[schadstoff],
    marker="o")
plt.title(f"Durchschnittlicher Verlauf von {schadstoff.upper()} rund um Silvester")
plt.xlabel("Datum")
plt.ylabel(f"Durchschnittlicher {schadstoff.upper()}-Wert")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()