import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro v5.2", layout="wide")
load_dotenv()

# 2. INITIALISATION DU CLIENT (Version Stable)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

@st.cache_resource
def get_client():
    if api_key:
        # On initialise le client normalement
        return genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
    return None

client = get_client()

# 3. INTERFACE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("v5.2 | Forced API v1")
oe_input = st.sidebar.text_input("Référence OE", value="1109.AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
        if st.button("🔥 Générer le Catalogue Complet", use_container_width=True):
            if not client:
                st.error("Clé API manquante dans les Secrets.")
            else:
                with st.spinner("Interrogation via API v1 Stable..."):
                    try:
                        # Appel avec forçage du modèle sur la branche stable
                        response = client.models.generate_content(
                            model="gemini-1.5-flash",
                            contents=f"Liste 40 correspondances IAM pour l'OE {oe_input}. Format: MARQUE | REF | DESC | CRITERES"
                        )
                        
                        if response.text:
                            data = []
                            for line in response.text.strip().split('\n'):
                                if '|' in line:
                                    cols = [c.strip() for c in line.split('|')]
                                    if len(cols) >= 2:
                                        data.append({
                                            "Marque": cols[0].upper(),
                                            "Référence": cols[1],
                                            "Description": cols[2] if len(cols) > 2 else "",
                                            "Critères": cols[3] if len(cols) > 3 else ""
                                        })
                            st.success(f"✅ {len(data)} références trouvées.")
                            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                        else:
                            st.warning("Réponse vide de l'IA.")
                    except Exception as e:
                        st.error(f"Détail de l'erreur : {e}")
