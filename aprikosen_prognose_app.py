
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# Titel
st.title("🌳 Aprikosenbäume Entwicklungsprognose")
st.markdown("""
Dieses Tool prognostiziert den Bestand an Aprikosenbäumen basierend auf fixen monatlichen Neupflanzungen 
und einem prozentualen jährlichen Wachstum.
""")

# Seitenleiste für Parameter
st.sidebar.header("🔧 Parameter konfigurieren")

startbestand = st.sidebar.number_input("Startbestand (Bäume)", value=60000, step=1000)
monatliche_zugaenge = st.sidebar.number_input("Monatliche Zugänge", value=1800, step=100)
jaehrliches_wachstum = st.sidebar.slider("Jährliches Wachstum (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.1)
prognosejahre = st.sidebar.slider("Prognosezeitraum (Jahre)", min_value=1, max_value=10, value=5)

# Berechnungen
startdatum = datetime(2025, 5, 1)
monate_gesamt = prognosejahre * 12
monatlicher_wachstumsfaktor = (1 + jaehrliches_wachstum/100) ** (1/12)

daten = []
aktueller_bestand = startbestand

for monat in range(1, monate_gesamt + 1):
    aktuelles_datum = startdatum + timedelta(days=30.44 * (monat - 1))
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
plt.figure(figsize=(10, 5))
plt.plot(df['Datum'], df['Baumbestand'], marker='o', linewidth=2)
plt.xlabel("Datum")
plt.ylabel("Anzahl Bäume")
plt.grid(True)
st.pyplot()

# Statistiken
st.subheader("📊 Statistische Kennzahlen")
end_bestand = df['Baumbestand'].iloc[-1]
gesamtwachstum = end_bestand - startbestand
gesamtwachstum_prozent = ((end_bestand / startbestand) - 1) * 100

st.markdown(f"- **Startbestand:** {startbestand:,} Bäume")
st.markdown(f"- **Endbestand:** {end_bestand:,.0f} Bäume")
st.markdown(f"- **Gesamtwachstum:** {gesamtwachstum:,.0f} Bäume ({gesamtwachstum_prozent:.2f}%)")
st.markdown(f"- **Durchschnittlicher monatlicher Zuwachs:** {df['Monatlicher_Zuwachs'].mean():,.0f} Bäume")
