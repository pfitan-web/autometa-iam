import streamlit as st
import pandas as pd
from google import genai
import os
import time
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro v5.4", layout="wide")
load_dotenv()

# 2. SELECTION DU MOTEUR (Pour contourner le 429)
st.sidebar.title("🚀 Configuration IA")
model_choice = st.sidebar.selectbox(
    "Moteur de recherche :",
    ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro"]
)

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# 3. INTERFACE
st.sidebar.divider()
oe_input = st.sidebar.text_input("Référence OE", value="1109AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
        if st.button("🔥 Lancer l'Analyse Massive", use_container_width=True):
            if not client:
                st.error("Clé API manquante.")
            else:
                with st.spinner(f"Interrogation de {model_choice}..."):
                    try:
                        # Appel avec le modèle sélectionné
                        response = client.models.generate_content(
                            model=model_choice,
                            contents=f"Génère un tableau de 50 correspondances IAM pour {oe_input}. Format: MARQUE | REF | DESC | CRITERES"
                        )
                        
                        if response.text:
                            data = []
                            for line in response.text.strip().split('\n'):
                                if '|' in line:
                                    cols = [c.strip() for c in line.split('|')]
                                    if len(cols) >= 2:
                                        data.append({"Marque": cols[0].upper(), "Réf": cols[1], "Desc": cols[2] if len(cols)>2 else "", "Critères": cols[3] if len(cols)>3 else ""})
                            st.success(f"✅ {len(data)} résultats trouvés.")
                            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                    
                    except Exception as e:
                        if "429" in str(e):
                            st.error("🚨 Quota épuisé pour ce moteur. Veuillez attendre 60 secondes ou changer de moteur dans la barre latérale.")
                        else:
                            st.error(f"Détail de l'erreur : {e}")
