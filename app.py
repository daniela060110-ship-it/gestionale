import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurazione Pagina
st.set_page_config(page_title="SafetyManager 81/08", layout="wide")

# --- CSS PER TESTO NERO E INTERFACCIA CHIARA ---
st.markdown("""
    <style>
    /* Forza il colore del testo globale */
    html, body, [data-testid="stWidgetLabel"], .stText, p, h1, h2, h3, span {
        color: #1F2937 !important; 
    }
    .stApp { background-color: #FFFFFF; }
    
    /* Card per i dipendenti e documenti */
    .element-container div.stMarkdown div p { color: #1F2937 !important; }
    
    /* Sidebar scura con testo chiaro per contrasto */
    [data-testid="stSidebar"] { background-color: #111827; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Stile per i box dei documenti */
    .stCard {
        background-color: #F9FAFB;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Inizializzazione Database
if 'aziende' not in st.session_state:
    st.session_state.aziende = {}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ SafetyManager")
    st.caption("Gestione D.Lgs. 81/08")
    st.divider()
    menu = st.radio("Navigazione", ["📊 Dashboard", "🏢 Aziende"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Dashboard")
    st.write("Panoramica scadenze e stato sicurezza")
    
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

    st.subheader("⚠️ Avvisi Recenti")
    if not in_scadenza and not scadute:
        st.success("Tutto in regola!")
    else:
        for s in scaduti:
            st.error(f"SCADUTO: {s['Tipo']} - {s['Dipendente']} ({s['Azienda']})")
        for s in in_scadenza:
            st.warning(f"IN SCADENZA: {s['Tipo']} - {s['Dipendente']} ({s['Azienda']})")

# --- GESTIONE AZIENDE ---
else:
    st.header("Aziende")
    
    with st.expander("➕ Aggiungi Nuova Azienda"):
        with st.form("nuova_az"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome Azienda *")
            piva = c2.text_input("P.IVA")
            sl = c1.text_input("Sede Legale")
            so = c2.text_input("Sede Operativa")
            if st.form_submit_button("Salva"):
                if nome:
                    st.session_state.aziende[nome] = {
                        "info": {"piva": piva, "sede_l": sl, "sede_o": so},
                        "dipendenti": [], "documenti": []
                    }
                    st.rerun()

    lista_az = list(st.session_state.aziende.keys())
    if lista_az:
        scelta = st.selectbox("Seleziona Azienda:", lista_az)
        az = st.session_state.aziende[scelta]

        st.subheader(f"🏢 {scelta}")
        st.write(f"**P.IVA:** {az['info']['piva']} | **Sede Operativa:** {az['info']['sede_o']}")

        tab_doc, tab_dip = st.tabs(["📄 Documenti", "👥 Dipendenti"])

        # --- TAB DIPENDENTI ---
        with tab_dip:
            with st.popover("➕ Aggiungi Dipendente"):
                with st.form("f_dip"):
                    n = st.text_input("Nome")
                    c = st.text_input("Cognome")
                    dn = st.date_input("Data Nascita", value=datetime(1980,1,1))
                    ln = st.text_input("Luogo Nascita")
                    man = st.text_input("Mansione")
                    if st.form_submit_button("Registra"):
                        az['dipendenti'].append({
                            "Nome": f"{n} {c}", "Dati": f"{dn} - {ln}",
                            "Mansione": man, "In Forza": True
                        })
                        st.rerun()
            
            for i, d in enumerate(az['dipendenti']):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"**{d['Nome']}** \n*{d['Mansione']}*")
                    d['In Forza'] = col2.toggle("In forza", value=d['In Forza'], key=f"d_{scelta}_{i}")
                    if col3.button("🗑️", key=f"del_d_{scelta}_{i}"):
                        az['dipendenti'].pop(i)
                        st.rerun()

        # --- TAB DOCUMENTI ---
        with tab_doc:
            with st.popover("➕ Aggiungi Documento"):
                with st.form("f_doc"):
                    tipo = st.selectbox("Tipo Documento", [
                        "Nomina RSPP", "Attestato RSPP", "Nomina PREPOSTO", "Attestato PREPOSTO",
                        "Elezione RLS", "Attestato RLS", "Antincendio LIVELLO I", "Antincendio LIVELLO II",
                        "Antincendio LIVELLO III", "Primo Soccorso", "Specifica BASSO", "Specifica MEDIO",
                        "Specifica ALTO", "Medico Competente", "Idoneità Medica", "Altro"
                    ])
                    nomi_d = [d['Nome'] for d in az['dipendenti']]
                    dip_s = st.selectbox("Assegna a Dipendente", ["Aziendale"] + nomi_d)
                    emiss = st.date_input("Data Emissione")
                    anni = st.number_input("Anni Validità", value=5)
                    scad = emiss.replace(year=emiss.year + anni)
                    note = st.text_area("Note")
                    if st.form_submit_button("Salva Documento"):
                        az['documenti'].append({
                            "Tipo": tipo, "Dipendente": dip_s, "Azienda": scelta,
                            "Emissione": emiss, "Scadenza": scad, "Note": note
                        })
                        st.rerun()

            for j, doc in enumerate(az['documenti']):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    giorni = (doc['Scadenza'] - datetime.now().date()).days
                    col1.write(f"**{doc['Tipo']}** ({doc['Dipendente']})")
                    col1.caption(f"Scadenza: {doc['Scadenza']} | Note: {doc['Note']}")
                    
                    if giorni < 0:
                        col2.error(f"Scaduto ({giorni} gg)")
                    elif giorni <= 30:
                        col2.warning(f"{giorni} gg")
                    else:
                        col2.success(f"{giorni} gg")
                    
                    if col3.button("🗑️", key=f"del_doc_{scelta}_{j}"):
                        az['documenti'].pop(j)
                        st.rerun()
