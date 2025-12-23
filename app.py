import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION & DESIGN
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide")
load_dotenv()

# Style pour optimiser l'espace et l'apparence TecDoc
st.markdown("""
    <style>
    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 60px; 
        background-color: #f8f9fa; 
        border-radius: 5px 5px 0 0;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1f4e79 !important; 
        color: white !important; 
    }
    /* Style du tableau */
    thead tr th { background-color: #1f4e79 !important; color: white !important; }
    .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. IA GEMINI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_expertise(oe_ref, brand, iam_ref):
    prompt = f"""Expert Aftermarket : Compare la référence OE {oe_ref} avec la référence {brand} {iam_ref}.
    S'il s'agit du groupe VAG (VW, Audi, etc.), vérifie si le suffixe final est compatible ou s'il y a un piège.
    Réponse courte (2 phrases max)."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except: return "Analyse indisponible."

# 3. BARRE LATÉRALE
st.sidebar.title("🚀 AutoMeta-IAM")
st.sidebar.caption("v2.5 - Gemini 1.5 Flash")

st.sidebar.subheader("📋 Identification")
vin_val = st.sidebar.text_input("VIN / Châssis", placeholder="WVWZZZ...")
oe_val = st.sidebar.text_input("Référence OE", placeholder="Ex: 03L253010G")

st.sidebar.divider()
st.sidebar.link_button("🌐 SIV-Auto (Plaque ⮕ VIN)", "https://siv-auto.fr/", use_container_width=True)

# 4. INTERFACE PRINCIPALE (ONGLETS)
tab1, tab2 = st.tabs(["🔍 IDENTIFICATION & VUES OEM", "📊 ANALYSE IAM & TECDOC"])

# --- ONGLET 1 : L'ATELIER OEM ---
with tab1:
    st.subheader("Identification et Documentation")
    
    # Dashboard de liens rapides
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("🚀 PartsLink24", "https://www.partslink24.com/", use_container_width=True)
    with c2: st.link_button("🌍 PartSouq", "https://partsouq.com/", use_container_width=True)
    with c3: st.link_button("📘 CatCar Info", "https://www.catcar.info/en/", use_container_width=True)
    
    st.divider()
    # Visualisation TradeSoft
    st.info("💡 Navigation visuelle : Utilisez le catalogue ci-dessous pour identifier la référence OE.")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=800, scrolling=True)

# --- ONGLET 2 : LE BUREAU D'ÉTUDES IAM ---
with tab2:
    st.subheader("Expertise Aftermarket & Moteur TecDoc")
    
    if oe_val:
        st.success(f"Référence détectée : **{oe_val.upper()}**")
        
        # Le bouton d'action principal
        if st.button("🤖 Lancer l'Analyse Automatique", use_container_width=True):
            with st.spinner("Le robot extrait les données et Gemini analyse les compatibilités..."):
                
                # Simulation de données (Logique Robot Scraper)
                # Note: Ici on pourra brancher la fonction fetch_distri_data
                data_iam = [
                    {"Marque": "AJUSA", "Référence": "JTC11620", "Désignation": "Kit de montage, turbocompresseur"},
                    {"Marque": "ELRING", "Référence": "714.050", "Désignation": "Pochette de joints haut moteur"},
                    {"Marque": "CORTECO", "Référence": "026265H", "Désignation": "Joint d'étanchéité"}
                ]
                
                final_rows = []
                for item in data_iam:
                    note = get_ai_expertise(oe_val, item['Marque'], item['Référence'])
                    final_rows.append({
                        "Marque": item['Marque'],
                        "Référence IAM": item['Référence'],
                        "Désignation": item['Désignation'],
                        "Analyse Gemini 2.5 Flash": note
                    })
                
                st.table(pd.DataFrame(final_rows))
        
        st.divider()
        st.write("🔗 **Liens de vérification manuelle :**")
        b1, b2 = st.columns(2)
        with b1: st.link_button("📦 DistriAuto", f"https://www.distriauto.fr/pieces-auto/oem/{oe_val}", use_container_width=True)
        with b2: st.link_button("🔎 Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{oe_val}?ref=fulltext", use_container_width=True)
        
    else:
        st.info("👈 Veuillez entrer une référence OE dans la barre latérale pour activer l'onglet d'analyse.")

# FOOTER
st.divider()
st.caption("AutoMeta-IAM Pro | Données TecDoc & IA")
