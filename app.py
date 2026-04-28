import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Configurazione Pagina
st.set_page_config(page_title="SafetyManager 81/08", layout="wide")

# --- CSS PER CONTRASTO ELEVATO E PULIZIA ---
st.markdown("""
    <style>
    /* Sfondo bianco e testo nero per tutto */
    .stApp { background-color: #FFFFFF; color: #000000; }
    
    /* Forza il testo nero ovunque, inclusi widget e sidebar */
    h1, h2, h3, p, span, label, .stMarkdown { color: #111827 !important; }
    
    /* Sidebar: sfondo grigio chiarissimo con testo scuro */
    [data-testid="stSidebar"] { background-color: #F3F4F6 !important; border-right: 1px solid #E5E7EB; }
    [data-testid="stSidebar"] * { color: #111827 !important; }

    /* Pulsante primario azzurro */
    .stButton>button {
        background-color: #3B82F6; color: white !important;
        border-radius: 6px; border: none; font-weight: bold;
    }
    
    /* Box per documenti e dipendenti */
    .stContainer {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    /* Stile per dipendenti NON in forza */
    .cessato { color: #9CA3AF !important; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# Inizializzazione Database
if 'aziende' not in st.session_state:
    st.session_state.aziende = {}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ SafetyManager")
    st.write("---")
    menu = st.radio("Scegli sezione:", ["📊 Dashboard", "🏢 Aziende"])

# --- FUNZIONI DI SUPPORTO ---
def calcola_scadenza(data_emiss, anni):
    return data_emiss + relativedelta(years=int(anni))

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Dashboard Panoramica")
    
    scadenze_totali = []
    dip_attivi = 0
    for az_nome, az_dati in st.session_state.aziende.items():
        scadenze_totali.extend(az_dati['documenti'])
        dip_attivi += sum(1 for d in az_dati['dipendenti'] if d['In Forza'])
    
    oggi = datetime.now().date()
    soglia_30 = oggi + timedelta(days=30)
    
    scaduti = [s for s in scadenze_totali if s['Scadenza'] < oggi]
    in_scadenza = [s for s in scadenze_totali if oggi <= s['Scadenza'] <= soglia_30]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aziende", len(st.session_state.aziende))
    c2.metric("Dipendenti Attivi", dip_attivi)
    c3.metric("Scaduti", len(scaduti))
    c4.metric("In Scadenza (30gg)", len(in_scadenza))

    st.write("---")
    if scaduti:
        st.subheader("🚨 DOCUMENTI SCADUTI")
        for s in scaduti:
            st.error(f"**{s['Azienda']}**: {s['Tipo']} - {s['Dipendente']} (Scaduto il {s['Scadenza'].strftime('%d/%m/%Y')})")
    
    if in_scadenza:
        st.subheader("⚠️ IN SCADENZA (Prossimi 30 giorni)")
        for s in in_scadenza:
            st.warning(f"**{s['Azienda']}**: {s['Tipo']} - {s['Dipendente']} (Scadenza: {s['Scadenza'].strftime('%d/%m/%Y')})")

# --- AZIENDE ---
else:
    st.header("Gestione Aziende")
    
    # Aggiungi Azienda
    with st.expander("➕ Clicca qui per aggiungere una nuova azienda"):
        with st.form("new_az"):
            col1, col2 = st.columns(2)
            n_az = col1.text_input("Nome Azienda *")
            piva_az = col2.text_input("P.IVA")
            sl_az = col1.text_input("Sede Legale")
            so_az = col2.text_input("Sede Operativa")
            tel_az = col1.text_input("Telefono")
            if st.form_submit_button("SALVA AZIENDA"):
                if n_az:
                    st.session_state.aziende[n_az] = {
                        "info": {"piva": piva_az, "sl": sl_az, "so": so_az, "tel": tel_az},
                        "dipendenti": [], "documenti": []
                    }
                    st.rerun()

    # Selettore Azienda
    elenco = list(st.session_state.aziende.keys())
    if elenco:
        scelta = st.selectbox("Seleziona l'azienda su cui lavorare:", elenco)
        az = st.session_state.aziende[scelta]
        
        st.write(f"**Dati:** P.IVA {az['info']['piva']} | Tel: {az['info']['tel']} | Sede: {az['info']['so']}")
        
        tab_doc, tab_dip = st.tabs(["📄 DOCUMENTI E ATTESTATI", "👥 DIPENDENTI"])

        # --- TAB DIPENDENTI ---
        with tab_dip:
            with st.popover("➕ Aggiungi Nuovo Dipendente"):
                with st.form("form_dip"):
                    c1, c2 = st.columns(2)
                    nom = c1.text_input("Nome")
                    cog = c2.text_input("Cognome")
                    dn = st.date_input("Data di Nascita", value=datetime(1990,1,1), min_value=datetime(1940,1,1))
                    ln = st.text_input("Luogo di Nascita")
                    man = st.text_input("Mansione")
                    if st.form_submit_button("REGISTRA DIPENDENTE"):
                        az['dipendenti'].append({
                            "Nome": f"{nom} {cog}", "Mansione": man, "In Forza": True,
                            "Nascita": f"{dn.strftime('%d/%m/%Y')} ({ln})"
                        })
                        st.rerun()
            
            for i, d in enumerate(az['dipendenti']):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    # Effetto "chiaro" se non in forza
                    nome_display = d['Nome'] if d['In Forza'] else f"~~{d['Nome']} (Cessato)~~"
                    stile = "normal" if d['In Forza'] else "cessato"
                    
                    col1.markdown(f"<span class='{stile}'>**{nome_display}**<br><small>{d['Mansione']} | {d['Nascita']}</small></span>", unsafe_allow_html=True)
                    d['In Forza'] = col2.toggle("In forza", value=d['In Forza'], key=f"tog_{scelta}_{i}")
                    if col3.button("🗑️", key=f"del_d_{scelta}_{i}"):
                        az['dipendenti'].pop(i)
                        st.rerun()

        # --- TAB DOCUMENTI ---
        with tab_doc:
            with st.popover("➕ Aggiungi Documento / Scadenza"):
                with st.form("form_doc"):
                    t_doc = st.selectbox("Tipo Documento", [
                        "Nomina RSPP", "Attestato RSPP", "Nomina PREPOSTO", "Attestato PREPOSTO",
                        "Elezione RLS", "Attestato RLS", "Antincendio LIVELLO I", "Antincendio LIVELLO II",
                        "Antincendio LIVELLO III", "Primo Soccorso", "Specifica BASSO", "Specifica MEDIO",
                        "Specifica ALTO", "Medico Competente", "Idoneità Medica", "Altro"
                    ])
                    nomi_attivi = [d['Nome'] for d in az['dipendenti']]
                    dip_sel = st.selectbox("Seleziona Dipendente", ["Aziendale"] + nomi_attivi)
                    
                    c1, c2 = st.columns(2)
                    d_emiss = c1.date_input("Data Emissione", value=datetime.now())
                    v_anni = c2.number_input("Anni Validità", min_value=1, max_value=10, value=5)
                    
                    # Calcolo automatico della scadenza visibile nel form
                    d_scad_auto = calcola_scadenza(d_emiss, v_anni)
                    st.info(f"📅 La scadenza verrà registrata per il: **{d_scad_auto.strftime('%d/%m/%Y')}**")
                    
                    not_d = st.text_area("Note")
                    if st.form_submit_button("SALVA DOCUMENTO"):
                        az['documenti'].append({
                            "Azienda": scelta, "Tipo": t_doc, "Dipendente": dip_sel,
                            "Emissione": d_emiss, "Scadenza": d_scad_auto, "Note": not_d
                        })
                        st.rerun()

            for j, doc in enumerate(az['documenti']):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    giorni = (doc['Scadenza'] - datetime.now().date()).days
                    
                    col1.markdown(f"**{doc['Tipo']}**<br><small>{doc['Dipendente']}</small>", unsafe_allow_html=True)
                    col1.caption(f"Emissione: {doc['Emissione'].strftime('%d/%m/%Y')} | Scadenza: **{doc['Scadenza'].strftime('%d/%m/%Y')}**")
                    
                    if giorni < 0:
                        col2.error(f"Scaduto")
                    elif giorni <= 30:
                        col2.warning(f"{giorni} gg")
                    else:
                        col2.success(f"{giorni} gg")
                        
                    if col3.button("🗑️", key=f"del_doc_{scelta}_{j}"):
                        az['documenti'].pop(j)
                        st.rerun()
