import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION & STYLE
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide")
load_dotenv()

# Injection CSS pour forcer l'affichage du menu et des tableaux
st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    thead tr th { background-color: #1f4e79 !important; color: white !important; }
    .stTable { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. IA GEMINI
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

def get_tech_data(oe_ref, brand, iam_ref):
    """Simule l'interrogation technique pour remplir le tableau"""
    prompt = f"Donne les caractéristiques techniques (ex: dents, diamètre, tension) pour la pièce {brand} {iam_ref} (OE: {oe_ref}). Format court."
    try:
        response = model.generate_content(prompt)
        return response.text
    except: return "Données indisponibles"

# 3. BARRE LATÉRALE (Rétablie)
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.divider()

st.sidebar.subheader("🚗 Identification")
vin = st.sidebar.text_input("VIN / Châssis", placeholder="WVWZZZ...")
st.sidebar.link_button("🌐 SIV-Auto", "https://siv-auto.fr/", use_container_width=True)

st.sidebar.subheader("📦 Pièce")
oe_input = st.sidebar.text_input("Référence OE", placeholder="Ex: 03L121011J")

st.sidebar.divider()
# Indicateur de statut (comme sur votre image image_bc71c9.png)
if st.secrets.get("PL24_USER"):
    st.sidebar.success("🟢 PartsLink24 : Connecté")
else:
    st.sidebar.warning("🟡 Mode Visiteur")

# 4. CORPS PRINCIPAL
tab1, tab2 = st.tabs(["🔍 IDENTIFICATION", "📊 TABLEAU TECHNIQUE IAM"])

with tab1:
    st.subheader("Identification Constructeur")
    st.info("Utilisez l'éclaté ci-dessous pour confirmer votre référence.")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.subheader(f"Comparatif Technique : {oe_input}")
        
        if st.button("🤖 Lancer l'Analyse Comparative", use_container_width=True):
            with st.spinner("Recherche des correspondances..."):
                # Simulation de données type Daparto/TecDoc
                # À terme, le robot remplira cette liste dynamiquement
                mock_results = [
                    {"Marque": "SKF", "Référence": "VKPC 81269"},
                    {"Marque": "FEBI", "Référence": "36048"},
                    {"Marque": "GATES", "Référence": "WP0118"}
                ]
                
                final_rows = []
                for item in mock_results:
                    tech = get_tech_data(oe_input, item['Marque'], item['Référence'])
                    final_rows.append({
                        "Marque": item['Marque'],
                        "Référence": item['Référence'],
                        "Critères Techniques": tech,
                        "Analyse IA": "Compatible"
                    })
                
                st.table(pd.DataFrame(final_rows))
        
        st.divider()
        st.write("🔗 Accès directs :")
        c1, c2 = st.columns(2)
        with c1: st.link_button("📦 DistriAuto", f"https://www.distriauto.fr/pieces-auto/oem/{oe_input}", use_container_width=True)
        with c2: st.link_button("🔎 Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{oe_input}", use_container_width=True)
    else:
        st.warning("Veuillez saisir une référence OE dans la barre latérale pour activer le tableau.")
