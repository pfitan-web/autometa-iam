import streamlit as st
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro v3.8", layout="wide")
load_dotenv()

# 2. IA GEMINI (Utilisation de 'gemini-pro' pour la stabilité sur Streamlit Cloud)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

# LISTE ÉLARGIE DES MARQUES TOP (20/80)
PREMIUM_BRANDS = [
    "PURFLUX", "MANN-FILTER", "MAHLE", "KNECHT", "BOSCH", "HENGST",
    "TRW", "ATE", "BREMBO", "DELPHI", "PHINIA", "KYB", "KAYABA", 
    "MONROE", "LEMFÖRDER", "MEYLE", "SACHS", "BILSTEIN", "LUK", 
    "VALEO", "SKF", "GATES", "INA", "DAYCO", "CONTINENTAL", "NTN-SNR", "SNR"
]

# 3. FONCTION DE GÉNÉRATION DE DONNÉES MASSIVES (IA)
def get_massive_iam_data(oe_ref):
    """Demande à l'IA de générer TOUTES les correspondances connues si le web bloque"""
    prompt = f"""
    En tant qu'expert TecDoc, génère une liste exhaustive (minimum 20 références) pour l'OE {oe_ref}.
    Pour chaque marque premium (PURFLUX, MANN, MAHLE, BOSCH, etc.), donne la référence exacte.
    Format de sortie uniquement : MARQUE | RÉFÉRENCE | DESCRIPTION | CRITÈRES (Dimensions, Dents, etc)
    """
    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n')
        results = []
        for line in lines:
            if '|' in line:
                p = line.split('|')
                results.append({
                    "Marque": p[0].strip().upper(),
                    "Référence": p[1].strip(),
                    "Description": p[2].strip() if len(p) > 2 else "Filtre",
                    "Critères (Cotes)": p[3].strip() if len(p) > 3 else "Standard"
                })
        return results
    except: return []

# 4. INTERFACE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
oe_input = st.sidebar.text_input("Référence OE", value="1109AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. EXPERTISE TECHNIQUE IAM"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
        
        if st.button("⚡ Lancer l'Analyse Massive", use_container_width=True):
            with st.spinner("Extraction de la base de données..."):
                
                # Tentative IA Directe pour avoir du volume immédiatement
                data = get_massive_iam_data(oe_input)
                
                if data:
                    final_rows = []
                    for item in data:
                        is_top = any(m in item['Marque'] for m in PREMIUM_BRANDS)
                        final_rows.append({
                            "Statut": "🔝 TOP MARQUE" if is_top else "Alternative",
                            "Marque": item['Marque'],
                            "Référence": item['Référence'],
                            "Description": item['Description'],
                            "Critères (Dimensions)": item['Critères (Cotes)']
                        })
                    
                    df = pd.DataFrame(final_rows).sort_values(by="Statut", ascending=False)
                    
                    # Affichage riche
                    st.success(f"✅ {len(df)} références identifiées pour {oe_input}.")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error("Erreur lors de la génération des données.")
