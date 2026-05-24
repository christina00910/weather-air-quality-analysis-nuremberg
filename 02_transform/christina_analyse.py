# Analysezeitraum ab 2008
df = df[df["datum"].dt.year >= 2008]

# Zielvariable festlegen
schadstoff = "pm10"

# Zeitvariablen erstellen
df["wochentag"] = df["datum"].dt.dayofweek
df["monat"] = df["datum"].dt.month
df["wochenende"] = df["wochentag"].isin([5, 6]).astype(int)
df["rush_hour"] = df["stunde"].isin([6,7,8,9,16,17,18,19]).astype(int)


# Jahreszeit erstellen
def jahreszeit(monat):
    if monat in [12, 1, 2]:
        return "Winter"
    elif monat in [3, 4, 5]:
        return "Frühling"
    elif monat in [6, 7, 8]:
        return "Sommer"
    else:
        return "Herbst"
df["jahreszeit"] = df["monat"].apply(jahreszeit)

# Durchschnitt nach Jahreszeit
reihenfolge = ["Frühling", "Sommer", "Herbst", "Winter"]
schadstoff_jahreszeit = df.groupby("jahreszeit")[schadstoff].mean()
schadstoff_jahreszeit = schadstoff_jahreszeit.reindex(reihenfolge)
plt.figure(figsize=(8,5))
plt.bar(schadstoff_jahreszeit.index, schadstoff_jahreszeit.values)
plt.title(f"Durchschnittliche {schadstoff.upper()}-Werte nach Jahreszeit")
plt.xlabel("Jahreszeit")
plt.ylabel(f"Durchschnittlicher {schadstoff.upper()}-Wert")
plt.show()


# Durchschnitt Werktag vs Wochenende
schadstoff_wochenende = df.groupby("wochenende")[schadstoff].mean()

plt.figure(figsize=(6,5))
plt.bar(["Werktag", "Wochenende"], schadstoff_wochenende.values)
plt.title(f"{schadstoff.upper()}: Werktag vs Wochenende")
plt.ylabel(f"Durchschnittlicher {schadstoff.upper()}-Wert")
plt.show()