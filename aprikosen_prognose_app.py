
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date


# Titel
st.title("🌳 Aprikosenbäume Entwicklungsprognose")
st.markdown("""
Dieses Tool prognostiziert den Bestand an Aprikosenbäumen basierend auf fixen monatlichen Neupflanzungen
und einem prozentualen jährlichen Wachstum.
""")


MAX_PROGNOSEJAHRE = 50


def _parse_int(value: str, field_label: str, minimum: int = 0, maximum: int | None = None):
    if not value.strip():
        raise ValueError(f"{field_label} ist ein Pflichtfeld.")
    try:
        parsed = int(value)
    except ValueError:
        raise ValueError(f"{field_label} muss eine ganze Zahl sein.")
    if parsed < minimum:
        raise ValueError(f"{field_label} muss mindestens {minimum} betragen.")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{field_label} darf höchstens {maximum} betragen.")
    return parsed


def _parse_float(value: str, field_label: str, minimum: float = 0.0):
    if not value.strip():
        raise ValueError(f"{field_label} ist ein Pflichtfeld.")
    try:
        parsed = float(value.replace(",", "."))
    except ValueError:
        raise ValueError(f"{field_label} muss eine Zahl sein.")
    if parsed < minimum:
        raise ValueError(f"{field_label} muss mindestens {minimum} betragen.")
    return parsed


# Seitenleiste für Parameter
st.sidebar.header("🔧 Parameter konfigurieren")
with st.sidebar.form("parameter_form", clear_on_submit=False):
    startbestand_input = st.text_input(
        "Startbestand (Bäume)",
        value="1000",
        help="Pflichtfeld. Gesamtzahl vorhandener Bäume zu Beginn (ganze Zahl)."
    )
    monatliche_zugaenge_input = st.text_input(
        "Monatliche Zugänge",
        value="1800",
        help="Pflichtfeld. Geplante Neupflanzungen pro Monat (ganze Zahl)."
    )
    jaehrliches_wachstum_input = st.text_input(
        "Jährliches Wachstum (%)",
        value="7.0",
        help="Pflichtfeld. Prozentuales Wachstum pro Jahr (0 oder größer)."
    )
    prognosejahre_input = st.text_input(
        "Prognosezeitraum (Jahre)",
        value="5",
        help=(
            f"Pflichtfeld. Anzahl der Jahre für die Prognose (mindestens 1, maximal {MAX_PROGNOSEJAHRE})."
        ),
    )
    startdatum_input = st.date_input(
        "Startdatum",
        value=datetime.today().date(),
        min_value=date(2000, 1, 1),
        max_value=date(2050, 12, 31),
        help="Pflichtfeld. Datum, ab dem die Prognose beginnen soll."
    )
    submitted = st.form_submit_button("Prognose berechnen")

if not submitted:
    st.info("Bitte füllen Sie die Pflichtfelder links aus und starten Sie die Prognose.")
    st.stop()

validation_errors = []
try:
    startbestand = _parse_int(startbestand_input, "Startbestand (Bäume)")
except ValueError as exc:
    validation_errors.append(str(exc))

try:
    monatliche_zugaenge = _parse_int(monatliche_zugaenge_input, "Monatliche Zugänge")
except ValueError as exc:
    validation_errors.append(str(exc))

try:
    jaehrliches_wachstum = _parse_float(jaehrliches_wachstum_input, "Jährliches Wachstum (%)")
except ValueError as exc:
    validation_errors.append(str(exc))

try:
    prognosejahre = _parse_int(
        prognosejahre_input,
        "Prognosezeitraum (Jahre)",
        minimum=1,
        maximum=MAX_PROGNOSEJAHRE,
    )
except ValueError as exc:
    validation_errors.append(str(exc))

if validation_errors:
    for error in validation_errors:
        st.sidebar.error(error)
    st.error("Bitte korrigieren Sie die markierten Eingaben, um fortzufahren.")
    st.stop()

# Berechnungen
startdatum = pd.Timestamp(startdatum_input)
monate_gesamt = prognosejahre * 12
monatlicher_wachstumsfaktor = (1 + jaehrliches_wachstum/100) ** (1/12)

daten = []
aktueller_bestand = startbestand

for monat in range(1, monate_gesamt + 1):
    aktuelles_datum = startdatum + pd.DateOffset(months=monat - 1)
    daten.append({
        'Monat': monat,
        'Datum': aktuelles_datum,
        'Baumbestand': round(aktueller_bestand),
        'Monatlicher_Zuwachs': round(aktueller_bestand * (monatlicher_wachstumsfaktor - 1) + monatliche_zugaenge)
    })
    aktueller_bestand = aktueller_bestand * monatlicher_wachstumsfaktor + monatliche_zugaenge

df = pd.DataFrame(daten)
df['Gesamtzuwachs'] = df['Baumbestand'] - startbestand
df['Gesamtwachstum_%'] = ((df['Baumbestand'] / startbestand) - 1) * 100

# Plots
st.subheader("📈 Entwicklung des Baumbestands")

fig, ax = plt.subplots(figsize=(10, 5))

lineare_entwicklung = startbestand + (df['Monat'] - 1) * monatliche_zugaenge
lineares_endbestandsziel = lineare_entwicklung.iloc[-1]

ax.plot(
    df['Datum'],
    df['Baumbestand'],
    color='seagreen',
    marker='$\u2618$',
    markersize=10,
    markerfacecolor='forestgreen',
    markeredgecolor='forestgreen',
    linewidth=2,
    label='Prognose mit Wachstum'
)

ax.plot(
    df['Datum'],
    lineare_entwicklung,
    color='black',
    linewidth=2,
    linestyle='--',
    label='Lineare Entwicklung (ohne Zinseszins)'
)

ax.set_xlabel("Datum")
ax.set_ylabel("Anzahl Bäume")
ax.set_title("Monatliche Baumbestandsentwicklung")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# Statistiken
st.subheader("📊 Statistische Kennzahlen")
end_bestand = df['Baumbestand'].iloc[-1]
zinseszinseffekt = end_bestand - lineares_endbestandsziel
gesamtwachstum = end_bestand - startbestand
gesamtwachstum_prozent = ((end_bestand / startbestand) - 1) * 100
zinseszinseffekt_anteil_prozent = (zinseszinseffekt / end_bestand) * 100 if end_bestand else 0

st.markdown(f"- **Startbestand:** {startbestand:,} Bäume")
st.markdown(f"- **Endbestand:** {end_bestand:,.0f} Bäume")
st.markdown(f"- **Gesamtwachstum:** {gesamtwachstum:,.0f} Bäume ({gesamtwachstum_prozent:.2f}%)")
st.markdown(
    f"- **Zusätzlicher Ertrag durch Zinseszins:** {zinseszinseffekt:,.0f} Bäume "
    f"({zinseszinseffekt_anteil_prozent:.2f}% des Endbestands)"
)
st.markdown(f"- **Durchschnittlicher monatlicher Zuwachs:** {df['Monatlicher_Zuwachs'].mean():,.0f} Bäume")

# Verteilung des Endbestands
st.subheader("🥧 Anteil des Zinseszinseffekts am Endbestand")
rest_bestand = end_bestand - zinseszinseffekt
fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
ax_pie.pie(
    [rest_bestand, zinseszinseffekt],
    labels=["Lineare Entwicklung", "Zinseszinseffekt"],
    autopct="%1.1f%%",
    startangle=90,
    colors=["#a3c9a8", "#2e7d32"],
    explode=(0, 0.05),
)
ax_pie.axis('equal')
st.pyplot(fig_pie)
