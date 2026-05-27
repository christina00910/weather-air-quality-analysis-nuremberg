import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analyseSilvesterTime (df, stoff):
    # Silvesteranalyse
    # Ziel: Analyse der Luftschadstoffbelastung rund um Weihnachten und Silvester.

    # ------------------------------------------------------------
    # Zielvariable festlegen
    # ------------------------------------------------------------
    schadstoff = stoff

    # ------------------------------------------------------------
    # Monat und Tag erstellen
    # ------------------------------------------------------------
    df["monat"] = df["datum"].dt.month
    df["tag"] = df["datum"].dt.day

    # ------------------------------------------------------------
    # Zeitraum rund um Silvester filtern (21.12. bis 07.01.)
    # ------------------------------------------------------------
    silvester_df = df[
        ((df["monat"] == 12) & (df["tag"] >= 21)) |
        ((df["monat"] == 1) & (df["tag"] <= 7))
    ].copy()

    # ------------------------------------------------------------
    # Hilfsspalte für korrekte Sortierung erstellen
    # ------------------------------------------------------------
    silvester_df["tag_sort"] = silvester_df.apply(
        lambda row: row["tag"] if row["monat"] == 12 else row["tag"] + 31,
        axis=1
    )

    # ------------------------------------------------------------
    # Datum für die Anzeige formatieren
    # ------------------------------------------------------------
    silvester_df["datum_label"] = silvester_df["datum"].dt.strftime("%d.%m.")

    # ------------------------------------------------------------
    # Durchschnittswerte pro Tag berechnen
    # ------------------------------------------------------------
    silvester_tagesmittel = silvester_df.groupby(
        ["tag_sort", "datum_label"])[schadstoff].mean().reset_index()

    silvester_tagesmittel = silvester_tagesmittel.sort_values("tag_sort")

    # ------------------------------------------------------------
    # Grafik erstellen
    # ------------------------------------------------------------
    # 1. Figur erstellen (Kompakt und schwarzer Hintergrund)
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
    ax.set_facecolor('black')

    # 2. Plot zeichnen
    ax.plot(
        silvester_tagesmittel["datum_label"],
        silvester_tagesmittel[schadstoff],
        color='#4A90E2',
        marker="o",
        markerfacecolor='white',
        markeredgecolor='#4A90E2',
        markersize=4,
        linewidth=1
    )

    # 3. Titel und Achsenbeschriftungen verkleinern
    ax.set_title(f"Verlauf von {schadstoff.upper()} rund um Silvester", color='white', fontsize=9, fontweight="bold")
    ax.set_xlabel("Datum", color='white', fontsize=5.5)
    ax.set_ylabel(f"Schnitt {schadstoff.upper()}-Wert", color='white', fontsize=5.5)

    # 4. WICHTIG: Ticks setzen BEVOR set_xticklabels aufgerufen wird (behebt potenzielle Fehler)
    ax.set_xticks(np.arange(len(silvester_tagesmittel)))
    
    # Achsen-Zahlen & Datums-Labels verkleinern und rotieren
    ax.set_xticklabels(silvester_tagesmittel["datum_label"], fontsize=4.5, color='white', rotation=45)
    ax.tick_params(colors='white', which='both', labelsize=4.5)

    # 5. Rahmen und Gitternetz anpassen
    for spine in ax.spines.values():
        spine.set_color('white')
    ax.grid(True, color='dimgray', linestyle='--', linewidth=0.5, alpha=0.3)

    # 6. Layout optimieren und Figur zurückgeben
    fig.tight_layout()
    return fig