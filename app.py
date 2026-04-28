import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurazione Pagina
st.set_page_config(page_title="SafetyManager", layout="wide")

# --- STILE CSS PER INTERFACCIA CHIARA E PULITA ---
st.markdown("""
    <style>
    .stApp { background-color: #F9FAFB; }
    .stButton>button { border-radius: 8px; }
    .main-card {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
    }
    </style>
    """, unsafe_allow_html=True)

# Inizializzazione Database (Session State)
if 'aziende' not in st.session_state:
    st.session_state.aziende = {}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ SafetyManager")
    menu = st.radio("Vai a:", ["📊 Dashboard", "🏢 Gestione Aziende"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("Dashboard")
    st.write("Panoramica scadenze e stato sicurezza")
    
    # Logica per contatori
    scadenze_totali = []
    dip_attivi = 0
    for az in st.session_state.aziende.values():
        scadenze_totali.extend(az['documenti'])
        dip_attivi += sum(1 for d in az['dipendenti'] if d['In Forza'])
    
    oggi = datetime.now().date()
    soglia_30 = oggi + timedelta(days=30)
    
    scaduti = [s for s in scadenze_totali if s['Scadenza'] < oggi]
    in_scadenza = [s for s in scadenze_totali if oggi <= s['Scadenza'] <= soglia_30]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aziende", len(st.session_state.aziende))
    c2.metric("Dipendenti Attivi", dip_attivi)
    c3.metric("In scadenza (30gg)", len(in_scadenza))
    c4.metric("Scaduti", len(scaduti))

# --- GESTIONE AZIENDE ---
else:
    st.title("Aziende")
    
    # Sezione Nuova Azienda
    with st.expander("➕ Aggiungi Nuova Azienda"):
        with st.form("form_azienda"):
            c1, c2 = st.columns(2)
            nome_az = c1.text_input("Nome Azienda *")
            piva = c2.text_input("P.IVA")
            sede_l = c1.text_input("Sede Legale")
            sede_o = c2.text_input("Sede Operativa")
            if st.form_submit_button("Crea Azienda"):
                if nome_az:
                    st.session_state.aziende[nome_az] = {
                        "info": {"piva": piva, "sede_l": sede_l, "sede_o": sede_o},
                        "dipendenti": [],
                        "documenti": []
                    }
                    st.success(f"Azienda {nome_az} creata!")
                    st.rerun()

    # Selezione Azienda
    lista_az = list(st.session_state.aziende.keys())
    if lista_az:
        scelta = st.selectbox("Seleziona Azienda per operare:", lista_az)
        az_corr = st.session_state.aziende[scelta]

        # Header Azienda selezionata (come da tua foto)
        st.markdown(f"### 🏢 {scelta}")
        st.info(f"**P.IVA:** {az_corr['info']['piva']} | **Sede Operativa:** {az_corr['info']['sede_o']}")

        # TAB DOCUMENTI E DIPENDENTI
        tab_doc, tab_dip = st.tabs(["📄 Documenti", "👥 Dipendenti"])

        # --- TAB DIPENDENTI ---
        with tab_dip:
            c_tit, c_add = st.columns([4, 1])
            with c_add:
                with st.popover("➕ Aggiungi Dipendente"):
                    with st.form("form_dip"):
                        n_d = st.text_input("Nome")
                        c_d = st.text_input("Cognome")
                        d_n = st.date_input("Data di Nascita", value=datetime(1990,1,1))
                        l_n = st.text_input("Luogo di Nascita")
                        man = st.text_input("Mansione")
                        if st.form_submit_button("Salva Dipendente"):
                            az_corr['dipendenti'].append({
                                "NomeCompleto": f"{n_d} {c_d}", "Info": f"{n_d} {c_d} - {man}",
                                "Mansione": man, "In Forza": True
                            })
                            st.rerun()
            
            # Lista Dipendenti con Switch
            for i, d in enumerate(az_corr['dipendenti']):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"**{d['NomeCompleto']}**\n{d['Mansione']}")
                    d['In Forza'] = col2.toggle("In forza", value=d['In Forza'], key=f"f_{i}")
                    if col3.button("🗑️", key=f"del_d_{i}"):
                        az_corr['dipendenti'].pop(i)
                        st.rerun()

        # --- TAB DOCUMENTI ---
        with tab_doc:
            c_tit2, c_add2 = st.columns([4, 1])
            with c_add2:
                with st.popover("➕ Aggiungi Documento"):
                    with st.form("form_doc"):
                        tipo = st.selectbox("Tipo Documento *", [
                            "Nomina RSPP", "Attestato RSPP", "Nomina PREPOSTO", "Attestato PREPOSTO",
                            "Elezione RLS", "Attestato RLS", "Antincendio LIVELLO I", "Antincendio LIVELLO II",
                            "Antincendio LIVELLO III", "Primo Soccorso", "Specifica BASSO", "Specifica MEDIO",
                            "Specifica ALTO", "Medico Competente", "Idoneità Medica", "Altro"
                        ])
                        dip_nomi = ["Aziendale (Nessuno)"] + [d['NomeCompleto'] for d in az_corr['dipendenti']]
                        dip_scelto = st.selectbox("Dipendente", dip_nomi)
                        emiss = st.date_input("Data Emissione")
                        validita = st.number_input("Anni Validità", min_value=1, value=5)
                        scad = emiss.replace(year=emiss.year + int(validita))
                        note = st.text_area("Note")
                        if st.form_submit_button("Salva"):
                            az_corr['documenti'].append({
                                "Tipo": tipo, "Dipendente": dip_scelto,
                                "Emissione": emiss, "Scadenza": scad, "Note": note
                            })
                            st.rerun()

            # Lista Documenti
            for j, doc in enumerate(az_corr['documenti']):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"**{doc['Tipo']}**")
                    col1.caption(f"{doc['Dipendente']} — Scade: {doc['Scadenza']}")
                    
                    # Calcolo giorni rimanenti
                    giorni = (doc['Scadenza'] - datetime.now().date()).days
                    col2.markdown(f"**{giorni} gg**")
                    
                    if col3.button("🗑️", key=f"del_doc_{j}"):
                        az_corr['documenti'].pop(j)
                        st.rerun()
    else:
        st.info("Inizia aggiungendo la tua prima azienda qui sopra!")
