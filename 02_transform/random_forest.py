#Random Forest Regressor
#Tatsächliche Wichtigkeit der Wetterfaktoren für die Vorhersage

# Bibliotheken laden
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# Daten Laden
df = pd.read_csv("02_transform/Schadstoff_Wetter.csv")

# Datum in datetime umwandeln
df["datum"] = pd.to_datetime(df["datum"])
print(df.info())

# Analysezeitraum ab 2008 Um eine einheitliche und vergleichbare Datenbasis zu gewährleisten
df = df[df["datum"].dt.year >= 2008]

# Zielvariable festlegen
schadstoff = "o3"

# Einflussvariablen (Wetterdaten)
x = df[[
    "temperatur",
    "windgeschwindigkeit",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung"]]

# Zielvariable
y = df[schadstoff]

# Fehlende Werte entfernen
rf_df = pd.concat([x, y], axis=1).dropna()

x = rf_df[[
    "temperatur",
    "windgeschwindigkeit",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung"]]

y = rf_df[schadstoff]

# Daten in Trainings- und Testset aufteilen
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# Random Forest Modell erstellen
modell = RandomForestRegressor(n_estimators=20, random_state=42, n_jobs=-1)
modell.fit(x_train, y_train)

# Vorhersagen treffen
vorhersage = modell.predict(x_test)

# Modellbewertung
r2 = r2_score(y_test, vorhersage)
mae = mean_absolute_error(y_test, vorhersage)
print("R²:", r2)
print("MAE:", mae)

# Feature Importance anzeigen
importance_df = pd.DataFrame({
    "Variable": x.columns,
    "Wichtigkeit": modell.feature_importances_})

importance_df = importance_df.sort_values(
    by="Wichtigkeit",
    ascending=False)

print(importance_df)

# Visualisierung
plt.figure(figsize=(10,6))

plt.bar(
    importance_df["Variable"],
    importance_df["Wichtigkeit"])

plt.title(f"Einfluss der Wettervariablen auf {schadstoff}")
plt.ylabel("Wichtigkeit")
plt.xticks(rotation=45)
plt.show()