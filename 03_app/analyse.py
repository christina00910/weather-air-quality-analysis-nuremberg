import pandas as pd
import seaborn as sns
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

def calcMeanYear(dfO, stoff):
    df = dfO.copy()
    
    # Jahresmittelwert berechnen
    df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
    df.set_index('datum', inplace=True)
    min_hours_per_year = int(8760 * 0.7)
    
    # 'YE' steht für Year End Resampling
    annual_trend = df[stoff].resample('YE').apply(
        lambda x: x.mean() if x.notna().sum() >= min_hours_per_year else None
    )
    chart_data = annual_trend.reset_index()
    chart_data = chart_data.dropna()
    
    # ========================================================
    # MATPLOTLIB-DARSTELLUNG (Kompakt, Dark Mode, Ohne Legende)
    # ========================================================
    # Halbe Grafikgröße wählen (6x4) und schwarzer Hintergrund
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
    ax.set_facecolor('black')
    
    # Liniendiagramm mit Markern zeichnen (analog zu px.line)
    ax.plot(
        chart_data['datum'].dt.year,  # Nutzt nur die Jahreszahl für eine saubere X-Achse
        chart_data[stoff],
        color='#4A90E2',              # Kräftiges Blau für die Linie
        marker='o',                   # Punkte als Marker
        markerfacecolor='white',      # Weiße Punkte
        markeredgecolor='#4A90E2',
        linewidth=2
    )
    
    # Titel und Beschriftungen auf Deutsch setzen
    ax.set_title(
        f"Jahresmittelwert Trend für {stoff.upper()}", 
        color='white', 
        fontsize=11, 
        fontweight="bold"
    )
    ax.set_xlabel("Jahr", color='white', fontsize=9)
    ax.set_ylabel(r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    
    # Achsenstriche und Jahreszahlen weiß färben
    ax.tick_params(colors='white', which='both', labelsize=8)
    
    # Rahmenlinien (Spines) weiß färben
    for spine in ax.spines.values():
        spine.set_color('white')
        
    # Dezente graue Gitterlinien im Hintergrund
    ax.grid(axis="both", linestyle="--", alpha=0.3, color='dimgray')
    
    # Sicherstellen, dass alle Jahreszahlen als Ganzzahlen dargestellt werden
    ax.xaxis.get_major_locator().set_params(integer=True)
    
    plt.tight_layout()
    return fig

def calcMeanSaisonYear(dfO, stoff):
    # Kopie anlegen, um das Original nicht zu verändern
    df = dfO.copy()
    
    # Datum konvertieren und als Index setzen
    df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
    df.set_index('datum', inplace=True)
    
    # Gruppieren nach Jahr und Monat, um den monatlichen Mittelwert zu berechnen
    # Das unstack() sorgt dafür, dass Jahre als Zeilen und Monate (1-12) als Spalten vorliegen
    monthly_means = df.groupby([df.index.year, df.index.month])[stoff].mean().unstack()
    
    # ========================================================
    # MATPLOTLIB-DARSTELLUNG (Kompakt, Dark Mode, Ohne Legende)
    # ========================================================
    # Halbe Grafikgröße wählen (6x4) und schwarzer Hintergrund
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
    ax.set_facecolor('black')

    # Jahre und gut sichtbare Kontrastfarben für den Dark Mode definieren
    jahre = [1990, 2000, 2010, 2020]
    farben = ["#FF6B6B", "#4DCD94", "#4A90E2", "#F5A623"] # Kräftige, helle Farben
    
    for jahr, farbe in zip(jahre, farben):
        if jahr in monthly_means.index:
            daten_jahr = monthly_means.loc[jahr]
            
            # Linie zeichnen
            ax.plot(
                daten_jahr,
                color=farbe,
                marker="o",
                markersize=4,
                linewidth=1.5
            )
            
            # WICHTIG (Ersatz für die Legende): Jahreszahl direkt an das Ende der Linie schreiben
            # Findet den letzten gültigen (Nicht-NaN) Wert des Jahres für die Y-Position
            letzter_monat = daten_jahr.dropna().index[-1]
            letzter_wert = daten_jahr[letzter_monat]
            ax.text(
                letzter_monat + 0.1, letzter_wert, str(jahr), 
                color=farbe, fontsize=8, va='center', fontweight='bold'
            )

    # Titel und Beschriftungen auf Deutsch setzen (Größen für kleine Grafik optimiert)
    ax.set_title(
        f"Saisonales {stoff.upper()}-Muster im Jahrzehntvergleich", 
        color='white', 
        fontsize=11, 
        fontweight="bold"
    )
    ax.set_xlabel("Monat", color='white', fontsize=9)
    ax.set_ylabel(r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    
    # Achsen-Ticks definieren (Monate 1 bis 12)
    ax.set_xticks(range(1, 13))
    
    # Achsenstriche und Beschriftungen weiß färben
    ax.tick_params(colors='white', which='both', labelsize=8)
    
    # Rahmenlinien (Spines) weiß färben
    for spine in ax.spines.values():
        spine.set_color('white')
        
    # Dezente graue Gitterlinien im Hintergrund aktivieren
    ax.grid(True, linestyle="--", alpha=0.3, color='dimgray')
    
    # X-Achse leicht erweitern, damit die Jahreszahlen am Rand Platz haben und nicht abgeschnitten werden
    ax.set_xlim(0.5, 13.5)
    
    plt.tight_layout()
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

def analyzeSeasonAndWeekend(dfO, stoff):
    """Analysiert und plottet die Schadstoff-Durchschnitte nach Jahreszeit
    und Werktag vs. Wochenende ab dem Jahr 2008. Gibt (fig_season, fig_weekend) zurück.
    """
    # Kopie anlegen, um das Original nicht zu verändern
    df = dfO.copy()
    
    # Sicherstellen, dass das Datum im richtigen Format vorliegt
    df["datum"] = pd.to_datetime(df["datum"])
    
    # Analysezeitraum ab 2008 filtern
    df = df[df["datum"].dt.year >= 2008]

    # Den übergebenen Schadstoffnamen in Kleinbuchstaben umwandeln
    stoff_lower = stoff.lower()

    # Absicherung: Prüfen, ob die Spalte existiert
    if stoff_lower not in df.columns:
        st.error(f"Schadstoff '{stoff}' fehlt im Datensatz.")
        return None, None

    # Zeitvariablen erstellen
    df["wochentag"] = df["datum"].dt.dayofweek
    df["monat"] = df["datum"].dt.month
    df["wochenende"] = df["wochentag"].isin([5, 6]).astype(int)

    # Deutsche Jahreszeiten-Logik
    def get_season(monat):
        if monat in [12, 1, 2]:
            return "Winter"
        elif monat in [3, 4, 5]:
            return "Frühling"
        elif monat in [6, 7, 8]:
            return "Sommer"
        else:
            return "Herbst"
    df["season"] = df["monat"].apply(get_season)

    # Standard-Stile zurücksetzen für konsistenten Dark Mode
    plt.rcParams.update(plt.rcParamsDefault)

    # ========================================================
    # DIAGRAMM 1: JAHRESZEIT (AUF DEUTSCH)
    # ========================================================
    season_order = ["Frühling", "Sommer", "Herbst", "Winter"]
    schadstoff_jahreszeit = df.groupby("season")[stoff_lower].mean().reindex(season_order)

    # Kompakte Größe (5x4) und schwarzer Hintergrund
    fig_season, ax_season = plt.subplots(figsize=(5, 4), facecolor='black')
    ax_season.set_facecolor('black')
    
    ax_season.bar(schadstoff_jahreszeit.index, schadstoff_jahreszeit.values, color="#4A90E2")
    
    ax_season.set_title(f"Mittlere {stoff.upper()}-Werte nach Jahreszeit", color='white', fontsize=10, fontweight="bold")
    ax_season.set_xlabel("Jahreszeit", color='white', fontsize=9)
    ax_season.set_ylabel(r"Durchschnittliche Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    
    ax_season.tick_params(colors='white', which='both', labelsize=8)
    for spine in ax_season.spines.values():
        spine.set_color('white')
    ax_season.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    fig_season.tight_layout()

    # ========================================================
    # DIAGRAMM 2: WERKTAG VS. WOCHENENDE (AUF DEUTSCH)
    # ========================================================
    schadstoff_wochenende = df.groupby("wochenende")[stoff_lower].mean()

    # Kompakte Größe (5x4) und schwarzer Hintergrund
    fig_weekend, ax_weekend = plt.subplots(figsize=(5, 4), facecolor='black')
    ax_weekend.set_facecolor('black')
    
    # Beschriftung direkt auf Deutsch gesetzt
    ax_weekend.bar(["Werktag", "Wochenende"], schadstoff_wochenende.values, color="#FF6B6B")
    
    ax_weekend.set_title(f"{stoff.upper()}: Werktag vs. Wochenende", color='white', fontsize=10, fontweight="bold")
    ax_weekend.set_ylabel(r"Durchschnittliche Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    
    ax_weekend.tick_params(colors='white', which='both', labelsize=8)
    for spine in ax_weekend.spines.values():
        spine.set_color('white')
    ax_weekend.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    fig_weekend.tight_layout()

    return fig_season, fig_weekend

def getExceedancesPerYear(dfO, stoff):
    # Kopie anlegen, um das Original nicht zu verändern
    df = dfO.copy()
    
    # Datum umwandeln
    df["datum"] = pd.to_datetime(df["datum"])

    # Den übergebenen Schadstoffnamen in Kleinbuchstaben umwandeln
    stoff_lower = stoff.lower()

    # LQI-Schwellenwert ab Klasse "Mäßig"
    lqi_grenzwerte_maessig = {
        "pm10": 28,
        "pm2x5": 16,
        "o3": 73,
        "no2": 31
    }

    # Absicherung: Falls der Schadstoff nicht in den Grenzwerten oder im DF existiert
    if stoff_lower not in lqi_grenzwerte_maessig or stoff_lower not in df.columns:
        st.error(f"Schadstoff '{stoff}' wird nicht unterstützt oder fehlt im Datensatz.")
        return None

    grenzwert = lqi_grenzwerte_maessig[stoff_lower]

    # Relevante Daten auswählen
    daten = df[["datum", stoff_lower]].dropna()

    # Jahr aus Datum erstellen
    daten["jahr"] = daten["datum"].dt.year.astype(int)

    # Prüfen, ob der Grenzwert überschritten bzw. erreicht wurde
    daten["ab_maessig"] = daten[stoff_lower] >= grenzwert

    # Überschreitungen pro Jahr zählen
    ueberschreitungen_jahr = daten.groupby("jahr")["ab_maessig"].sum()

    st.write(f"### 📊 Jährliche Auswertung: LQI-Überschreitungen ({stoff.upper()})")
    st.write(f"### 📈 Stunden mit mindestens mäßiger Luftqualität ({stoff.upper()})")

    # Standard-Stile zurücksetzen
    plt.rcParams.update(plt.rcParamsDefault)

    # Halbe Grafikgröße wählen (6x4) und schwarzer Hintergrund
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
    ax.set_facecolor('black')

    # Balkendiagramm zeichnen (Kräftiges Blau für guten Kontrast im Dark Mode)
    ax.bar(
        ueberschreitungen_jahr.index.astype(str),
        ueberschreitungen_jahr.values,
        color="#4A90E2"
    )

    # Titel und Beschriftungen auf Deutsch
    ax.set_title(
        f"Stunden mit mindestens mäßiger Luftqualität: {stoff.upper()}",
        color='white',
        fontsize=10,
        fontweight="bold"
    )
    ax.set_xlabel("Jahr", color='white', fontsize=9)
    ax.set_ylabel("Anzahl belasteter Stunden", color='white', fontsize=9)
    
    # Achsenstriche und -beschriftungen weiß färben
    ax.tick_params(colors='white', which='both', labelsize=8)
    jahre = ueberschreitungen_jahr.index.astype(str)
    # Setzt die Positionen der Ticks auf jeden 5. Eintrag
    ax.set_xticks(range(0, len(jahre), 5))
    # Setzt die Beschriftungen für jeden 5. Eintrag
    ax.set_xticklabels(jahre[::5], rotation=45, ha='right')
    
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')

    plt.tight_layout()
    return fig