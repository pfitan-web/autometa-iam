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
    model = genai.GenerativeModel('gemini-1.5-flash')

# 3. INTERFACE (Placée AVANT les fonctions risquées)
st.sidebar.title("🚀 AutoMeta-IAM Pro")
oe_input = st.sidebar.text_input("Référence OE", value="1109.AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    # L'iframe reste visible même en cas d'erreur IA
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
        if st.button("🔥 Générer le Catalogue Complet", use_container_width=True):
            with st.spinner("Extraction des données en cours..."):
                prompt = f"Liste 30 correspondances Aftermarket pour l'OE {oe_input}. Format: MARQUE | REF | DESC | CRITERES"
                try:
                    response = model.generate_content(prompt)
                    if response.text:
                        lines = response.text.strip().split('\n')
                        results = []
                        for line in lines:
                            if '|' in line:
                                p = [x.strip() for x in line.split('|')]
                                results.append({"Marque": p[0], "Ref": p[1], "Desc": p[2] if len(p)>2 else "", "Critères": p[3] if len(p)>3 else ""})
                        st.table(pd.DataFrame(results))
                except Exception as e:
                    st.error(f"Erreur d'accès : {e}. Vérifiez que le requirements.txt est à jour.")
