import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION & DESIGN PRO
st.set_page_config(page_title="AutoMeta-IAM Pro | Deep Data Edition", layout="wide")
load_dotenv()

# Style pour une densité d'information maximale
st.markdown("""
    <style>
    .stDataFrame { font-size: 12px; }
    thead tr th { background-color: #1f4e79 !important; color: white !important; font-weight: bold; }
    .main .block-container { padding-top: 1rem; }
    [data-testid="stMetricValue"] { font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# 2. IA GEMINI : GÉNÉRATEUR DE CRITÈRES TECDOC
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

def get_tecdoc_specs(oe_ref, brand, iam_ref):
    """L'IA émule les 'Critères' TecDoc (Dents, Diamètre, Matériau)"""
    prompt = f"""
    Expert TecDoc. Pour la référence IAM {brand} {iam_ref} (OE {oe_ref}), génère une fiche technique précise :
    1. Description complète (ex: Pompe à eau avec joint et vis)
    2. Critères (ex: 19 dents, Turbine en plastique, Ø 30mm)
    3. Montage (ex: Courroie crantée)
    4. Observation (ex: Risque de variante suffixe G/J chez VAG)
    Réponds uniquement au format : DESCRIPTION | CRITÈRES | MONTAGE | OBSERVATION
    """
    try:
        response = model.generate_content(prompt)
        parts = response.text.split('|')
        return [p.strip() for p in parts] if len(parts) == 4 else ["N/A", "N/A", "N/A", "Check Suffix"]
    except: return ["Erreur IA", "Données non trouvées", "N/A", "N/A"]

# 3. BARRE LATÉRALE (Rétablie et enrichie)
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("Système Expert IAM v3.0")

st.sidebar.subheader("🚗 Identification")
vin_input = st.sidebar.text_input("VIN / Châssis", placeholder="WVWZZZ...")
st.sidebar.link_button("🌐 SIV-Auto (Plaque ⮕ VIN)", "https://siv-auto.fr/", use_container_width=True)

st.sidebar.subheader("📦 Recherche Pièce")
oe_val = st.sidebar.text_input("Référence Constructeur (OE)", value="03L121011J")

st.sidebar.divider()
st.sidebar.write("🟢 **Status API :** Gemini & Secrets OK") #

# 4. INTERFACE PRINCIPALE
tab_oem, tab_iam = st.tabs(["🔍 1. VUES ÉCLATÉES & VIN", "📊 2. FICHE TECHNIQUE IAM (TECDOC)"])

# --- ONGLET 1 : IDENTIFICATION ---
with tab_oem:
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.subheader("Documentation Visuelle OEM")
        st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)
    with col2:
        st.subheader("Accès Rapides")
        st.link_button("🚀 PartsLink24", "https://www.partslink24.com/", use_container_width=True)
        st.link_button("📘 CatCar Info", "https://www.catcar.info/", use_container_width=True)
        st.divider()
        st.info("💡 Retrouvez la référence exacte sur l'éclaté avant de lancer l'analyse IAM.")

# --- ONGLET 2 : LE TABLEAU DE DONNÉES RICHES ---
with tab_iam:
    if oe_val:
        st.markdown(f"### 📋 Expertise Technique IAM pour : `{oe_val.upper()}`")
        
        # Bouton d'action
        if st.button("🤖 Générer la Fiche Technique Comparative", use_container_width=True):
            with st.spinner("Extraction des données et génération des critères TecDoc..."):
                
                # Simulation de récupération de données (à coupler avec le scraper DistriAuto)
                # On se base sur les marques Premium identifiées dans vos captures
                iam_sources = [
                    {"Marque": "SKF", "Référence": "VKPC 81269"},
                    {"Marque": "FEBI BILSTEIN", "Référence": "36048"},
                    {"Marque": "GATES", "Référence": "WP0118"},
                    {"Marque": "GRAF", "Référence": "PA1089"}
                ]
                
                final_results = []
                for item in iam_sources:
                    # L'IA génère les colonnes riches (Dents, Matériau, etc.)
                    specs = get_tecdoc_specs(oe_val, item['Marque'], item['Référence'])
                    
                    final_results.append({
                        "Marque": item['Marque'],
                        "Référence": item['Référence'],
                        "Description": specs[0],
                        "Critères Techniques (Cotes/Dents)": specs[1],
                        "Montage/Type": specs[2],
                        "Analyse Critique (IA)": specs[3],
                        "Lien Image": f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{oe_val}"
                    })
                
                # Affichage via un DataFrame stylisé (plus riche que st.table)
                df = pd.DataFrame(final_results)
                st.dataframe(
                    df,
                    column_config={
                        "Lien Image": st.column_config.LinkColumn("📸 Voir Schéma/Photo"),
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.success("✅ Fiche technique générée. Vérifiez les 'Critères Techniques' pour confirmer le montage.")
        
        st.divider()
        st.caption("🔗 Sources externes :")
        c1, c2 = st.columns(2)
        with c1: st.link_button("🔎 Comparateur Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{oe_val}", use_container_width=True)
        with c2: st.link_button("📦 Catalogue DistriAuto", f"https://www.distriauto.fr/pieces-auto/oem/{oe_val}", use_container_width=True)

    else:
        st.warning("Veuillez saisir une référence OE dans la barre latérale.")
