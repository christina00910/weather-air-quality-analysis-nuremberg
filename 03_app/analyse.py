import pandas as pd
import seaborn as sns
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

def calcMeanYear (dfO, stoff) :
    df = dfO.copy ()
    # Jahresmittelwert nur berechnen, wenn das Jahr zu 50% vollständig ist
    df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
    df.set_index('datum', inplace=True)
    min_hours_per_year = int(8760 * 0.7)
    annual_trend = df[stoff].resample('YE').apply(lambda x: x.mean() if x.notna().sum() >= min_hours_per_year else None)
    chart_data = annual_trend.reset_index()
    chart_data = chart_data.dropna()
    # Das Plotly-Diagramm erstellen
    fig = px.line(
        chart_data, 
        x='datum', 
        y=stoff, 
        title=f"Jahresmittelwert Trend für {stoff}",
        markers=True
    )
    return fig


def calcMeanSaisonYear (dfO, stoff) :
    # Jahresmittelwert nur berechnen, wenn das Jahr zu 50% vollständig ist

    ## Methode: Saisonaler Mittelwert im Langzeitvergleich
    # Gruppieren nach Jahr und Monat, um den Mittelwert zu berechnen
    df = dfO.copy ()
    df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
    df.set_index('datum', inplace=True)
    monthly_means = df.groupby([df.index.year, df.index.month])[stoff].mean().unstack()
    
    # Plotten der Kurven für ausgewählte Jahrzehnte zum Vergleich
  # 3. Plot initialisieren
    fig, ax = plt.subplots(figsize=(10, 6))

    # 4. Kurven für die Jahrzehnte plotten (mit Absicherung, falls ein Jahr fehlt)
    jahre = [1990, 2000, 2010, 2020]
    farben = ["orange", "green", "blue", "red"]
    for jahr, farbe in zip(jahre, farben):
        if jahr in monthly_means.index:
            ax.plot(
                monthly_means.loc[jahr],
                label=str(jahr),
                color=farbe,
                marker="o",
            )
    # 5. Diagramm-Design anpassen
    ax.set_title(
        f"Veränderung des saisonalen {stoff}-Musters über die Jahrzehnte"
    )
    ax.set_xlabel("Monat")
    ax.set_ylabel(f"Mittlere {stoff} Konzentration (µg/m³)")
    ax.set_xticks(range(1, 13))
    ax.legend()
    ax.grid(True)
    return fig

def rushHourEffekt (dfo, stoff):
    # Datentypen korrigieren und Zeitstempel bauen
     # Datentypen korrigieren und Zeitstempel bauen
    df = dfo.copy()
    df['datum'] = pd.to_datetime(df['datum'])
    df['timestamp'] = df['datum'] + pd.to_timedelta(df['stunde'], unit='h')
    df.set_index('timestamp', inplace=True)
    df.drop(columns=['datum', 'stunde'], inplace=True)
    
    # Hilfsspalten anlegen
    df['hour'] = df.index.hour
    
    # 1. Standard-Stile zurücksetzen
    plt.rcParams.update(plt.rcParamsDefault)
    
    # 2. Plot mit schwarzem Hintergrund initialisieren
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='black')
    
    # 3. Achsen-Hintergrund auf Schwarz setzen
    ax.set_facecolor('black')
    
    # 4. Seaborn Plot mit weißer Linie und weißen Markern zeichnen
    sns.lineplot(
        data=df, x="hour", y=stoff, errorbar=None, 
        marker="o", ax=ax, color='white', 
        markerfacecolor='white', markeredgecolor='black'
    )
    
    # 5. Alle Textelemente explizit WEISS färben
    ax.set_title(f"Mittlerer {stoff.upper()}-Tagesverlauf (Rush-Hour-Effekt)", color='white', fontsize=12, pad=10)
    ax.set_xlabel("Uhrzeit", color='white')
    ax.set_ylabel(f"{stoff.upper()} [µg/m³]", color='white')
    
    # Achsenabschnitte (Ticks) und Beschriftungen weiß färben
    ax.tick_params(colors='white', which='both')
    
    # Die äußeren Rahmenlinien (Spines) weiß färben
    for spine in ax.spines.values():
        spine.set_color('white')
        
    # Gitterlinien dezent grau/weiß für gute Sichtbarkeit auf Schwarz
    ax.set_xticks(range(0, 24))
    ax.grid(True, color='dimgray', linestyle='--', linewidth=0.5)
    
    # Layout anpassen, damit nichts abgeschnitten wird
    fig.tight_layout()
    
    return fig

def getKorrelation  (dfO, stoff) :
    df = dfO.copy ()
    corr_matrix = df.corr(numeric_only=True) 
    
    # 2. Jetzt die Korrelation für den spezifischen Stoff herausholen
    korrelationen = corr_matrix[stoff].sort_values(ascending=False)
    st.dataframe(korrelationen.to_frame(name="Korrelationskoeffizient"))

    # 4. Visuelle Heatmap für den Überblick vorbereiten
    fig, ax = plt.subplots(figsize=(10, 8))

    # Hier funktioniert 'corr_matrix' jetzt fehlerfrei
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("Korrelationsmatrix der Messreihe")
    return fig

def getEinfluss (dfO, stoff) :
    """Erstellt die zwei Diagramme nebeneinander (Windklasse vs."""
    # Temperatur) und zeigt sie in Streamlit an.
    # 1. Daten kopieren, um Seiteneffekte beim Re-Run zu vermeiden
    df = dfO.copy()

    # Figure mit zwei Diagrammen nebeneinander erstellen
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # --- DIAGRAMM 1: Windgeschwindigkeit ---
    df["Windklasse"] = pd.cut(
        df["windgeschwindigkeit"],
        bins=[-1, 1, 2, 4, 6, 12],
        labels=[
            "Windstill (<1 m/s)",
            "Schwach (1-2 m/s)",
            "Mäßig (2-4 m/s)",
            "Frisch (4-6 m/s)",
            "Stark (>6 m/s)",
        ],
    )

    sns.boxplot(
        ax=ax1,
        data=df,
        x="Windklasse",
        y="no2",
        hue="Windklasse",
        palette="Blues_r",
        showfliers=False,
        legend=False,
    )

    ax1.set_title(
        r"1. Einfluss der Windgeschwindigkeit"
        + "\n"
        + r"(Je mehr Wind, desto sauberer die Luft)",
        fontsize=12,
        fontweight="bold",
    )
    ax1.set_xlabel("Windgeschwindigkeit Klasse")
    ax1.set_ylabel(r"$\mathrm{NO_2}$-Konzentration [$\mathrm{\mu g/m^3}$]")
    ax1.grid(axis="y", linestyle="--", alpha=0.7)

    # --- DIAGRAMM 2: Temperatur & Inversions-Effekt ---
    sns.regplot(
        ax=ax2,
        data=df,
        x="temperatur",
        y="no2",
        scatter_kws={"alpha": 0.3, "color": "tab:orange", "s": 10},
        line_kws={"color": "darkred", "linewidth": 2},
        lowess=True,
    )
    ax2.set_title(
        r"2. Einfluss der Temperatur"
        + "\n"
        + r"(Höhere Werte im kalten Winter / Heizperiode)",
        fontsize=12,
        fontweight="bold",
    )
    ax2.set_xlabel("Temperatur [°C]")
    ax2.set_ylabel(r"$\mathrm{NO_2}$-Konzentration [$\mathrm{\mu g/m^3}$]")
    ax2.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()

def inversionswetter(dfO, stoff):
    # Kopie erstellen und den richtigen Variablennamen (dfO) nutzen
    df = dfO.copy()
    
    # Inversionswetter-Bedingung berechnen
    inversions_wetter = (df['windgeschwindigkeit'] < 1.5) & \
                        (df['gesamtbewoelkung'] <= 2) & \
                        (df['luftdruck'] > 1020)

    # Spalte für die Zuweisung erstellen
    df['Wettertyp'] = np.where(inversions_wetter, 'Inversionslage (wolkenlos & windstill)', 'Normales Wetter')
    
    # Standard-Stile zurücksetzen (löscht eventuelle Streamlit-Vorgaben)
    plt.rcParams.update(plt.rcParamsDefault)
    
    fig, ax = plt.subplots(figsize=(7, 6), facecolor='black')
    ax.set_facecolor('black')
    
    # Farben für den Dark Mode anpassen (kräftigere Farben für besseren Kontrast auf Schwarz)
    farben = {
        "Normales Wetter": "#4A90E2",      # Helles Blau
        "Inversionslage (wolkenlos & windstill)": "#FF6B6B", # Helles Lachsrot
    }

    # Den übergebenen Stoffnamen in Kleinbuchstaben umwandeln für den Spaltenabgleich
    stoff_lower = stoff.lower()

    # Absicherung: Prüfen, ob der Schadstoff als Spalte existiert
    if "%s" % stoff_lower in df.columns:
        sns.boxplot(
            ax=ax,
            data=df,
            x="Wettertyp",
            y=stoff_lower,
            hue="Wettertyp",
            palette=farben,
            showfliers=False,
            legend=False
        )
    else:
        # Falls die Spalte fehlt, Text im Plot anzeigen
        ax.text(0.5, 0.5, f"Schadstoff '{stoff}' nicht im Datensatz", 
                color='white', ha='center', va='center', transform=ax.transAxes)

    # Styling an Dark Mode anpassen (Schrift und Linien in Weiß)
    ax.set_xlabel("")
    ax.set_ylabel(r"Konzentration [$\mathrm{\mu g/m^3}$]", color='white')
    ax.tick_params(colors='white', which='both')
    
    for spine in ax.spines.values():
        spine.set_color('white')
        
    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')

    # Dynamische LaTeX-Titelvergabe je nach gewähltem Schadstoff
    if stoff_lower == "no2":
        ax.set_title(r"Stickstoffdioxid ($\mathrm{NO_2}$)" + "\n" + r"(Verkehrs- & Heizungsstau)", color='white', fontsize=12)
    elif stoff_lower == "pm10":
        ax.set_title(r"Feinstaub ($\mathrm{PM_{10}}$)" + "\n" + r"(Starke Akkumulation bei Inversion)", color='white', fontsize=12)
    elif stoff_lower == "o3":
        ax.set_title(r"Ozon ($\mathrm{O_3}$)" + "\n" + r"(Abbau am Boden bei Smog)", color='white', fontsize=12)
    else:
        ax.set_title(f"{stoff.upper()}-Profil im Vergleich", color='white', fontsize=12)

    # Gesamttitel für die Einzelfigur anpassen
    plt.suptitle(
        f"Einfluss der Wetterlage auf {stoff.upper()}",
        fontsize=13,
        fontweight="bold",
        color="white"
    )
    
    plt.tight_layout()
    return fig

def smogVSNormal(dfO, stoff):
    """Analysiert historische Smogtage ab 1990 und stellt die Ergebnisse
    als Tabelle und Balkendiagramm in Streamlit dar.
    """
    # Kopie anlegen, um das Original nicht zu verändern
    df = dfO.copy()

    df.index = pd.to_datetime(df["datum"], errors="coerce") + pd.to_timedelta(
        df["stunde"], unit="h"
    )
    df = df[df.index >= "1990-01-01 00:00:00"]
    
    # WICHTIG: Nutzt jetzt den Parameter 'stoff' dynamisch für dropna
    df_clean = df.dropna(
        subset=["windgeschwindigkeit", "luftdruck", stoff]
    ).copy()

    df_clean["Jahr"] = df_clean.index.year
    df_clean["Dekade"] = (df_clean["Jahr"] // 10) * 10
    df_clean["Dekade_Str"] = df_clean["Dekade"].astype(str) + "er"

    # ========================================================
    # 3. SMOG-TAGE IDENTIFIZIEREN & ZUORDNEN
    # ========================================================
    stunden_mit_smog = (df_clean["windgeschwindigkeit"] <= 1.5) & (
        df_clean["luftdruck"] >= 992
    )

    smog_stunden_pro_tag = stunden_mit_smog.resample("D").sum()
    smog_tage_datumsliste = smog_stunden_pro_tag[
        smog_stunden_pro_tag >= 4
    ].index.date

    ist_smog_tag = (
        pd.Series(df_clean.index.date).isin(smog_tage_datumsliste).values
    )
    df_clean["Tagestyp"] = np.where(ist_smog_tag, "Smogtag", "Normaltag")

    st.write(f"### 📊 Numerische Auswertung nach Jahrzehnten ({stoff.upper()})")

    # WICHTIG: Nutzt jetzt den übergebenen 'stoff' für die Tabellen-Aggregatbildung
    vergleich_tabelle = (
        df_clean.groupby(["Dekade_Str", "Tagestyp"], observed=False)[stoff]
        .mean()
        .unstack()
    )

    # Prozentualen Schadstoff-Aufschlag berechnen
    vergleich_tabelle["Smog-Aufschlag (%)"] = (
        (vergleich_tabelle["Smogtag"] - vergleich_tabelle["Normaltag"])
        / vergleich_tabelle["Normaltag"]
    ) * 100

    # Tabelle formatiert in Streamlit anzeigen (auf 2 Nachkommastellen gerundet)
    st.dataframe(vergleich_tabelle.style.format("{:.2f}"))

    # ========================================================
    # 5. GRAFISCHE DARSTELLUNG (Kompakt & Dark Mode)
    # ========================================================
    st.write(f"### 📈 Grafischer historischer Wandel ({stoff.upper()})")

    # Standard-Stile zurücksetzen
    plt.rcParams.update(plt.rcParamsDefault)

    # Halbe Grafikgröße wählen (6x4) und schwarzer Hintergrund
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
    ax.set_facecolor('black')

    # Kräftige Farben für den Dark Mode
    farben = {"Normaltag": "#4A90E2", "Smogtag": "#FF6B6B"}

    # WICHTIG: 'y=stoff' für dynamische Achsenzuweisung
    sns.barplot(
        ax=ax,
        data=df_clean,
        x="Dekade_Str",
        y=stoff,
        hue="Tagestyp",
        palette=farben,
        errorbar=None,
        legend=False
    )

    # Grenzwert dezent in Weiß einzeichnen (nur sinnvoll/standardmäßig bei NO2)
    if stoff.lower() == "no2":
        ax.axhline(
            y=40,
            color="white",
            linestyle="--",
            linewidth=1,
            label=r"Jahresgrenzwert ($40\ \mathrm{\mu g/m^3}$)",
        )

    # Textelemente und Titel an den Dark Mode anpassen (Schriftgrößen für kleine Grafik reduziert)
    ax.set_title(
        f"{stoff.upper()}-Belastung: Smog- vs. Normaltage",
        color='white',
        fontsize=11,
        fontweight="bold",
    )
    ax.set_xlabel("Jahrzehnt (Dekade)", color='white', fontsize=9)
    ax.set_ylabel(
        r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9
    )
    
    # Achsenstriche und -beschriftungen weiß färben
    ax.tick_params(colors='white', which='both', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    
    # Legende an Dark Mode anpassen
    ax.legend(title="Typ des Tages", loc="upper right", 
              facecolor='black', edgecolor='white', labelcolor='white', fontsize=8, title_fontsize=8)

    plt.tight_layout()
    return fig

def seasonalInfluence(dfO, stoff):
    # Create copy to preserve original data
    df = dfO.copy()

    df.index = pd.to_datetime(df["datum"], errors="coerce") + pd.to_timedelta(
        df["stunde"], unit="h"
    )
    df = df[df.index >= "1990-01-01 00:00:00"]
    
    df_clean = df.dropna(
        subset=["windgeschwindigkeit", "luftdruck", stoff]
    ).copy()

    # Assign meteorological seasons based on month
    # 12,1,2 = Winter | 3,4,5 = Spring | 6,7,8 = Summer | 9,10,11 = Autumn
    df_clean["Month"] = df_clean.index.month
    df_clean["Season"] = pd.cut(
        df_clean["Month"],
        bins=[0, 2, 5, 8, 11, 12],
        labels=["Winter", "Frühling", "Sommer", "Herbst", "Winter"],
        ordered=False
    )

    # ========================================================
    # 3. IDENTIFY & ASSIGN SMOG DAYS
    # ========================================================
    hours_with_smog = (df_clean["windgeschwindigkeit"] <= 1.5) & (
        df_clean["luftdruck"] >= 992
    )

    smog_hours_per_day = hours_with_smog.resample("D").sum()
    smog_days_dates = smog_hours_per_day[
        smog_hours_per_day >= 4
    ].index.date

    is_smog_day = (
        pd.Series(df_clean.index.date).isin(smog_days_dates).values
    )
    df_clean["Day Type"] = np.where(is_smog_day, "Smog Tag", "Normaler Tag")

    st.write(f"### 📊 Numerical Evaluation by Season ({stoff.upper()})")

    # Group by Season and Day Type
    comparison_table = (
        df_clean.groupby(["Season", "Day Type"], observed=False)[stoff]
        .mean()
        .unstack()
    )
    
    # Sort seasons chronologically
    comparison_table = comparison_table.reindex(["Winter", "Frühling", "Sommer", "Herbst"])

    # Calculate percentage increase during smog events
    comparison_table["Smog in Prozent (%)"] = (
        (comparison_table["Smog Tag"] - comparison_table["Normaler Tag"])
        / comparison_table["Normaler Tag"]
    ) * 100

    # Display formatted table in Streamlit
    st.dataframe(comparison_table.style.format("{:.2f}"))

    # ========================================================
    # 5. GRAPHICAL REPRESENTATION (Compact, Dark Mode, No Legend)
    # ========================================================
    st.write(f"### 📈 Seasonal Variations ({stoff.upper()})")

    # Reset styles
    plt.rcParams.update(plt.rcParamsDefault)

    # Compact size (6x4) with black background
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
    ax.set_facecolor('black')

    # Dark Mode color palette
    colors = {"Normal Day": "#4A90E2", "Smog Day": "#FF6B6B"}

    # Draw barplot grouped by Season without legend
    sns.barplot(
        ax=ax,
        data=df_clean,
        x="Season",
        y=stoff,
        hue="Day Type",
        hue_order=["Normal Day", "Smog Day"],
        order=["Winter", "Frühling", "Sommer", "Herbst"],
        palette=colors,
        errorbar=None,
        legend=False  
    )

    # Standard annual limit line for NO2
    if stoff.lower() == "no2":
        ax.axhline(
            y=40,
            color="white",
            linestyle="--",
            linewidth=1
        )

    # Title and axis styling in English
    ax.set_title(
        f"Seasonal {stoff.upper()} Levels: Smog vs. Normal Days",
        color='white',
        fontsize=11,
        fontweight="bold",
    )
    ax.set_xlabel("Season", color='white', fontsize=9)
    ax.set_ylabel(
        r"Mean Concentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9
    )
    
    # White axis ticks and boundaries
    ax.tick_params(colors='white', which='both', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    
    # Double check to ensure legend is completely removed
    if ax.get_legend() is not None:
        ax.get_legend().remove()

    plt.tight_layout()
    return fig

def weekdayVSWeekend(dfO, pollutant):
    """Analyzes pollutant concentrations comparing weekdays vs. weekends

    during smog and normal days from 1990 onwards.
    """
    # Create copy to preserve original data
    df = dfO.copy()

    df.index = pd.to_datetime(df["datum"], errors="coerce") + pd.to_timedelta(
        df["stunde"], unit="h"
    )
    df = df[df.index >= "1990-01-01 00:00:00"]
    
    # Filter dataset dynamically by selected pollutant
    df_clean = df.dropna(
        subset=["windgeschwindigkeit", "luftdruck", pollutant]
    ).copy()

    # WICHTIG: Einteilung in Werktag (0-4 = Mo-Fr) und Wochenende (5-6 = Sa-So)
    df_clean["DayOfWeek"] = df_clean.index.weekday
    df_clean["Weekly Type"] = np.where(df_clean["DayOfWeek"] < 5, "Weekday", "Weekend")

    # ========================================================
    # 3. IDENTIFY & ASSIGN SMOG DAYS
    # ========================================================
    hours_with_smog = (df_clean["windgeschwindigkeit"] <= 1.5) & (
        df_clean["luftdruck"] >= 992
    )

    smog_hours_per_day = hours_with_smog.resample("D").sum()
    smog_days_dates = smog_hours_per_day[
        smog_hours_per_day >= 4
    ].index.date

    is_smog_day = (
        pd.Series(df_clean.index.date).isin(smog_days_dates).values
    )
    df_clean["Day Type"] = np.where(is_smog_day, "Smog Day", "Normal Day")

    st.write(f"### 📊 Numerical Evaluation: Weekday vs. Weekend ({pollutant.upper()})")

    # Group by Weekly Type and Day Type
    comparison_table = (
        df_clean.groupby(["Weekly Type", "Day Type"], observed=False)[pollutant]
        .mean()
        .unstack()
    )
    
    # Sort for logical presentation
    comparison_table = comparison_table.reindex(["Weekday", "Weekend"])

    # Calculate percentage increase during smog events
    comparison_table["Smog Increase (%)"] = (
        (comparison_table["Smog Day"] - comparison_table["Normal Day"])
        / comparison_table["Normal Day"]
    ) * 100

    # Display formatted table in Streamlit
    st.dataframe(comparison_table.style.format("{:.2f}"))

    # ========================================================
    # 5. GRAPHICAL REPRESENTATION (Compact, Dark Mode, No Legend)
    # ========================================================
    st.write(f"### 📈 Weekday vs. Weekend Variations ({pollutant.upper()})")

    # Reset styles
    plt.rcParams.update(plt.rcParamsDefault)

    # Compact size (6x4) with black background
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
    ax.set_facecolor('black')

    # Dark Mode color palette
    colors = {"Normal Day": "#4A90E2", "Smog Day": "#FF6B6B"}

    # Draw barplot grouped by Weekday/Weekend without legend
    sns.barplot(
        ax=ax,
        data=df_clean,
        x="Weekly Type",
        y=pollutant,
        hue="Day Type",
        hue_order=["Normal Day", "Smog Day"],
        order=["Weekday", "Weekend"],
        palette=colors,
        errorbar=None,
        legend=False  
    )

    # Standard annual limit line for NO2
    if pollutant.lower() == "no2":
        ax.axhline(
            y=40,
            color="white",
            linestyle="--",
            linewidth=1
        )

    # Title and axis styling in English
    ax.set_title(
        f"{pollutant.upper()} Levels: Weekdays vs. Weekends",
        color='white',
        fontsize=11,
        fontweight="bold",
    )
    ax.set_xlabel("Type of Week", color='white', fontsize=9)
    ax.set_ylabel(
        r"Mean Concentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9
    )
    
    # White axis ticks and boundaries
    ax.tick_params(colors='white', which='both', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    
    # Ensure legend is completely removed
    if ax.get_legend() is not None:
        ax.get_legend().remove()

    plt.tight_layout()
    return fig
