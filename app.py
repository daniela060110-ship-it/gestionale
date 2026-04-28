import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurazione Pagina (Layout Moderno)
st.set_page_config(page_title="SafetyManager D.Lgs 81/08", layout="wide", initial_sidebar_state="expanded")

# --- CSS CUSTOM PER INTERFACCIA COME DA FOTO ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stSidebar { background-color: #1e293b; color: white; }
    .stCard {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .metric-card {
        background: white; padding: 15px; border-radius: 8px;
        border-left: 5px solid #3b82f6; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIONE DATABASE (Simulata con Session State) ---
# Nota: Per produzione qui collegheremo un database reale
if 'aziende' not in st.session_state:
    st.session_state.aziende = {}
if 'scadenze' not in st.session_state:
    st.session_state.scadenze = []

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.title("🛡️ SafetyManager")
    st.caption("D.LGS. 81/08")
    st.divider()
    menu = st.radio("Navigazione", ["📊 Dashboard", "🏢 Aziende"])

# --- LOGICA DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("Dashboard")
    st.write("Panoramica scadenze e stato sicurezza")
    
    # Calcolo metriche
    oggi = datetime.now().date()
    soglia_30 = oggi + timedelta(days=30)
    
    scadute = [s for s in st.session_state.scadenze if s['Data Scadenza'] < oggi]
    in_scadenza = [s for s in st.session_state.scadenze if oggi <= s['Data Scadenza'] <= soglia_30]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Aziende", len(st.session_state.aziende))
    with col2:
        st.metric("Dipendenti Attivi", sum(1 for a in st.session_state.aziende.values() for d in a.get('dipendenti', []) if d['In Forza']))
    with col3:
        st.metric("In scadenza (30gg)", len(in_scadenza), delta_color="inverse")
    with col4:
        st.metric("Scaduti", len(scadute), delta_color="inverse")

    st.subheader("⚠️ Scadenze imminenti e documenti scaduti")
    if not in_scadenza and not scadute:
        st.success("✅ Tutto in regola! Nessuna scadenza nei prossimi 30 giorni.")
    else:
        for s in scadute + in_scadenza:
            color = "red" if s['Data Scadenza'] < oggi else "orange"
            st.warning(f"**{s['Azienda']}**: {s['Documento']} di {s['Dipendente']} ({s['Data Scadenza']})")

# --- LOGICA AZIENDE ---
elif menu == "🏢 Aziende":
    st.title("Aziende")
    col_titolo, col_btn = st.columns([4, 1])
    
    with col_btn:
        if st.button("+ Nuova Azienda"):
            st.session_state.show_form = True

    if st.session_state.get('show_form', False):
        with st.form("Aggiungi Azienda"):
            n = st.text_input("Nome Azienda")
            piva = st.text_input("P.IVA")
            sl = st.text_input("Sede Legale")
            so = st.text_input("Sede Operativa")
            tel = st.text_input("N. Telefono")
            note = st.text_area("Note")
            if st.form_submit_button("Salva Azienda"):
                st.session_state.aziende[n] = {
                    "P.IVA": piva, "Sede Legale": sl, "Sede Operativa": so, 
                    "Tel": tel, "Note": note, "dipendenti": []
                }
                st.session_state.show_form = False
                st.rerun()

    # Ricerca Azienda
    search = st.text_input("🔍 Cerca azienda...")
    
    for nome_azienda, dati in st.session_state.aziende.items():
        if search.lower() in nome_azienda.lower():
            with st.expander(f"🏢 {nome_azienda} - {dati['Sede Operativa']}"):
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.write(f"**P.IVA:** {dati['P.IVA']} | **Tel:** {dati['Tel']}")
                with col_del:
                    if st.button(f"Elimina {nome_azienda}", key=f"del_{nome_azienda}"):
                        del st.session_state.aziende[nome_azienda]
                        st.rerun()
                
                st.divider()
                # GESTIONE DIPENDENTI
                st.subheader("👥 Gestione Dipendenti")
                
                # Form aggiunta dipendente
                with st.form(f"add_dep_{nome_azienda}"):
                    nome_dep = st.text_input("Nome Dipendente")
                    if st.form_submit_button("Aggiungi Dipendente"):
                        st.session_state.aziende[nome_azienda]['dipendenti'].append({
                            "Nome": nome_dep, "In Forza": True, "Attestati": []
                        })
                        st.rerun()
                
                # Lista Dipendenti
                for i, dep in enumerate(dati['dipendenti']):
                    c1, c2, c3 = st.columns([2, 1, 3])
                    c1.write(f"**{dep['Nome']}**")
                    stato = c2.toggle("In Forza", value=dep['In Forza'], key=f"tog_{nome_azienda}_{i}")
                    st.session_state.aziende[nome_azienda]['dipendenti'][i]['In Forza'] = stato
                    
                    # Gestione Attestati
                    with c3.popover("📜 Aggiungi Documento/Scadenza"):
                        doc_tipo = st.selectbox("Tipo Documento", [
                            "Nomina RSPP", "Attestato RSPP", "Nomina PREPOSTO", "Attestato PREPOSTO",
                            "Elezione RLS", "Attestato RLS", "Antincendio LIVELLO I", "Antincendio LIVELLO II", 
                            "Antincendio LIVELLO III", "Primo Soccorso", "Specifica BASSO", 
                            "Specifica MEDIO", "Specifica ALTO", "Medico Competente", "Idoneità Medica", "Altro"
                        ], key=f"sel_{nome_azienda}_{i}")
                        data_s = st.date_input("Scadenza", key=f"date_{nome_azienda}_{i}")
                        if st.button("Registra Scadenza", key=f"btn_{nome_azienda}_{i}"):
                            nuova_scadenza = {
                                "Azienda": nome_azienda, "Dipendente": dep['Nome'],
                                "Documento": doc_tipo, "Data Scadenza": data_s
                            }
                            st.session_state.scadenze.append(nuova_scadenza)
                            st.success("Registrato!")
