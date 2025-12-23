import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro v4.2", layout="wide")
load_dotenv()

# 2. INITIALISATION IA
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # On utilise 'gemini-1.5-flash' car c'est le plus léger
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Clé API manquante dans les Secrets.")

# 3. INTERFACE (Placée en haut pour garantir l'affichage)
st.sidebar.title("🚀 AutoMeta-IAM Pro")
oe_input = st.sidebar.text_input("Référence OE", value="1109.AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
        
        if st.button("🔥 Générer le Catalogue Complet", use_container_width=True):
            with st.spinner("Extraction des données..."):
                prompt = f"Liste 30 correspondances IAM pour l'OE {oe_input}. Format: MARQUE | REF | DESC | CRITERES"
                
                try:
                    # Syntaxe ultra-simplifiée pour compatibilité maximale
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        lines = response.text.strip().split('\n')
                        results = []
                        for line in lines:
                            if '|' in line:
                                p = [x.strip() for x in line.split('|')]
                                results.append({"Marque": p[0], "Ref": p[1], "Desc": p[2] if len(p)>2 else "", "Critères": p[3] if len(p)>3 else ""})
                        
                        st.table(pd.DataFrame(results))
                    else:
                        st.warning("L'IA a renvoyé une réponse vide.")
                except Exception as e:
                    st.error(f"Détail de l'erreur : {e}")
