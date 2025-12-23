import streamlit as st
import pandas as pd
from genai import Client # Nouvelle bibliothèque
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro v5.0", layout="wide")
load_dotenv()

# 2. INITIALISATION NOUVELLE API
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
client = Client(api_key=api_key) if api_key else None

# 3. INTERFACE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("v5.0 | New SDK Engine")
oe_input = st.sidebar.text_input("Référence OE", value="1109.AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
        
        if st.button("🔥 Générer le Catalogue Complet", use_container_width=True):
            if not client:
                st.error("Clé API manquante.")
            else:
                with st.spinner("Interrogation de la nouvelle API Google..."):
                    prompt = f"Génère une liste de 40 correspondances Aftermarket pour l'OE {oe_input}. Format: MARQUE | REF | DESC | CRITERES"
                    
                    try:
                        # Nouvelle syntaxe de l'API google-genai
                        response = client.models.generate_content(
                            model="gemini-1.5-flash",
                            contents=prompt
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
                            
                            st.success(f"✅ {len(data)} références trouvées via SDK v5.0")
                            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                        
                    except Exception as e:
                        st.error(f"Erreur avec le nouveau SDK : {e}")
