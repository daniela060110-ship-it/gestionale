import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurazione Pagina
st.set_page_config(page_title="Gestione Sicurezza 81/08", layout="wide")

st.title("🛡️ Gestore Scadenze Sicurezza Lavoro")

# Inizializzazione Database in memoria (nella realtà si userebbe un file CSV o DB)
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=[
        "Azienda", "Dipendente", "Stato", "Documento", "Livello/Rischio", "Data Scadenza"
    ])

# --- SEZIONE INSERIMENTO ---
with st.sidebar:
    st.header("➕ Inserisci Nuovo Dato")
    azienda = st.text_input("Nome Azienda")
    dipendente = st.text_input("Nome Dipendente")
    in_forza = st.checkbox("Dipendente in forza", value=True)
    
    tipo_doc = st.selectbox("Documento/Nomina", [
        "Nomina RSPP", "Attestato RSPP", "Nomina PREPOSTO", "Attestato PREPOSTO",
        "Elezione RLS", "Attestato RLS", "Formazione ANTINCENDIO", 
        "Formazione PRIMO SOCCORSO", "Formazione Specifica", 
        "Nomina Medico Competente", "Idoneità Medica", "Altro"
    ])
    
    dettaglio = ""
    if "ANTINCENDIO" in tipo_doc:
        dettaglio = st.selectbox("Livello", ["LIVELLO I", "LIVELLO II", "LIVELLO III"])
    elif "Specifica" in tipo_doc:
        dettaglio = st.selectbox("Rischio", ["BASSO", "MEDIO", "ALTO"])
    
    data_scadenza = st.date_input("Data di Scadenza")
    
    if st.button("Salva nel Database"):
        nuovo_dato = {
            "Azienda": azienda,
            "Dipendente": dipendente,
            "Stato": "Attivo" if in_forza else "Cessato",
            "Documento": tipo_doc,
            "Livello/Rischio": dettaglio,
            "Data Scadenza": data_scadenza
        }
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([nuovo_dato])], ignore_index=True)
        st.success("Dato salvato!")

# --- VISUALIZZAZIONE E ALERT ---
st.header("📅 Scadenziario Attivo")

if not st.session_state.db.empty:
    df = st.session_state.db.copy()
    df['Data Scadenza'] = pd.to_datetime(df['Data Scadenza']).dt.date
    oggi = datetime.now().date()
    soglia_30gg = oggi + timedelta(days=30)

    # Funzione per evidenziare le scadenze
    def color_scadenze(val):
        if val <= oggi:
            return 'background-color: #ff4b4b; color: white' # Rosso (Scaduto)
        elif val <= soglia_30gg:
            return 'background-color: #ffa500; color: black' # Arancione (30gg)
        return ''

    # Filtri
    st.subheader("Filtra per Azienda")
    scelta_azienda = st.selectbox("Seleziona Azienda", ["Tutte"] + list(df['Azienda'].unique()))
    if scelta_azienda != "Tutte":
        df = df[df['Azienda'] == scelta_azienda]

    # Tabella formattata
    st.dataframe(df.style.applymap(color_scadenze, subset=['Data Scadenza']), use_container_width=True)
    
    # Conteggio Alert
    scadenze_vicine = df[(df['Data Scadenza'] <= soglia_30gg) & (df['Stato'] == "Attivo")]
    if not scadenze_vicine.empty:
        st.warning(f"Hai {len(scadenze_vicine)} scadenze prioritarie nei prossimi 30 giorni!")
else:
    st.info("Il database è vuoto. Inserisci i dati nella barra laterale.")
