# -*- coding: utf-8 -*-
"""
styling.py
==========
Zentrale Styling-Konfiguration für das Dashboard.

Verwendung in app.py (einmalig nach den Imports):

    import styling
    styling.apply_global_style()

Damit werden matplotlib + seaborn global auf einheitliches Look-and-Feel
gesetzt (Schriftart IBM Plex Sans, kleinere Schriftgrößen, Farbpalette,
Grid-Style). Existierende Plot-Funktionen müssen nicht angepasst werden,
sofern sie keine Hardcoded-Styles enthalten.

Zusätzlich stellt das Modul Konstanten bereit:
- PALETTE       : Hauptfarben für allgemeine Plots
- POLLUTANT_COLORS: Feste Farbzuordnung pro Schadstoff (Konsistenz!)
- COLORS        : Einzelne benannte Farben (primary, success, danger, ...)
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns


# ============================================================
# FARBPALETTE (IBM Carbon-inspiriert, finanztauglich)
# ============================================================

COLORS = {
    "primary":   "#0F62FE",   # IBM Blue – Hauptfarbe, neutral und professionell
    "secondary": "#393939",   # Dunkelgrau – für sekundäre Elemente
    "success":   "#198038",   # Grün – Unterhalb Grenzwert / positive Werte
    "warning":   "#F1C21B",   # Gelb – Achtung / Schwelle
    "danger":    "#DA1E28",   # Rot – Grenzwertüberschreitung
    "muted":     "#8D8D8D",   # Mittelgrau – Hintergrundlinien, Annotationen
    "accent":    "#8A3FFC",   # Lila – Akzentuierung, Highlights
    "neutral":   "#F4F4F4",   # Sehr helles Grau – Hintergrund-Layer
}

# Sequenzielle Hauptpalette (z. B. für Kategorienvergleiche)
PALETTE = [
    "#0F62FE",  # Blau
    "#198038",  # Grün
    "#DA1E28",  # Rot
    "#F1C21B",  # Gelb
    "#8A3FFC",  # Lila
    "#FA4D56",  # Hellrot
    "#007D79",  # Teal
    "#6929C4",  # Dunkellila
]

# Feste Farben pro Schadstoff -> über alle Tabs konsistent
POLLUTANT_COLORS = {
    "no2":   "#DA1E28",   # NO₂ -> Rot (Verkehr, "gefährlich")
    "o3":    "#F1C21B",   # O₃  -> Gelb (Sommer, Sonne)
    "pm10":  "#393939",   # PM10 -> Dunkelgrau (Staub)
    "pm2x5": "#8D8D8D",   # PM2.5 -> Mittelgrau (feinerer Staub)
}

# Sequenzielle Colormaps (für Heatmaps z. B. in Korrelationsanalyse)
HEATMAP_CMAP = "RdBu_r"          # Korrelationen (-1 bis +1)
SEQUENTIAL_CMAP = "viridis"      # Sequenzielle Werte


# ============================================================
# SCHRIFTART
# ============================================================

# Bevorzugt IBM Plex Sans, mit sauberen Fallbacks falls nicht installiert.
# Reihenfolge: System-IBM-Plex -> Helvetica -> Arial -> matplotlib-Default
FONT_FAMILY = ["IBM Plex Sans", "Helvetica", "Arial", "DejaVu Sans"]

# Schriftgrößen – etwas kleiner als matplotlib-Default für Dashboard-Look
FONT_SIZES = {
    "base":   9,
    "axes":   9,
    "ticks":  8,
    "legend": 8,
    "title":  11,
    "suptitle": 12,
}


# ============================================================
# GLOBALE STYLE-FUNKTION
# ============================================================

def apply_global_style():
    """
    Setzt matplotlib- und seaborn-Defaults global.
    Einmal in app.py nach den Imports aufrufen.
    """
    # Seaborn-Basis (whitegrid passt zu Dashboards – dezentes Grid)
    sns.set_theme(style="whitegrid", palette=PALETTE)

    # matplotlib rcParams überschreiben
    mpl.rcParams.update({
        # Schrift
        "font.family":      FONT_FAMILY,
        "font.size":        FONT_SIZES["base"],
        "axes.titlesize":   FONT_SIZES["title"],
        "axes.labelsize":   FONT_SIZES["axes"],
        "xtick.labelsize":  FONT_SIZES["ticks"],
        "ytick.labelsize":  FONT_SIZES["ticks"],
        "legend.fontsize":  FONT_SIZES["legend"],
        "figure.titlesize": FONT_SIZES["suptitle"],

        # Farben (Default-Cycler für Plots ohne explizite Farbe)
        "axes.prop_cycle":  plt.cycler(color=PALETTE),

        # Achsen & Grid
        "axes.edgecolor":   COLORS["muted"],
        "axes.labelcolor":  COLORS["secondary"],
        "axes.titlecolor":  COLORS["secondary"],
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.grid":         True,
        "grid.color":        COLORS["neutral"],
        "grid.linewidth":    0.6,
        "grid.alpha":        0.8,

        # Ticks
        "xtick.color":      COLORS["secondary"],
        "ytick.color":      COLORS["secondary"],
        "xtick.direction":  "out",
        "ytick.direction":  "out",

        # Figur
        "figure.facecolor": "white",
        "axes.facecolor":   "white",
        "figure.dpi":       100,
        "savefig.dpi":      150,
        "figure.autolayout": True,   # tight_layout automatisch

        # Legende
        "legend.frameon":    False,
        "legend.loc":        "best",

        # Linien
        "lines.linewidth":   1.6,
        "lines.markersize":  5,
    })


def get_pollutant_color(stoff: str) -> str:
    """
    Liefert die einheitliche Farbe für einen Schadstoff.
    Fallback: primary, falls Stoff unbekannt.

    Beispiel:
        ax.plot(df['datum'], df['no2'], color=styling.get_pollutant_color('no2'))
    """
    return POLLUTANT_COLORS.get(stoff, COLORS["primary"])
