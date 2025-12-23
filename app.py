import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION INTERFACE
st.set_page_config(page_title="AutoMeta-IAM Pro v4.1", layout="wide")
load_dotenv()

# 2. INITIALISATION IA (Correction définitive de l'erreur 404)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

@st.cache_resource
def load_model():
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Utilisation du nom de modèle le plus stable pour éviter l'erreur 404
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"Erreur d'initialisation : {e}")
    return None

model = load_model()

# 3. LISTE DES MARQUES PREMIUM (Pour le tri)
PREMIUM = ["PURFLUX", "MANN", "MAHLE", "KNECHT", "BOSCH", "HENGST", "DELPHI", "SKF", "SNR", "GATES", "VALEO", "LUK", "INA"]

# 4. STRUCTURE DE L'INTERFACE (Visible même si l'IA plante)
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("v4.1 | Version Stable")
oe_input = st.sidebar.text_input("Référence OE", value="1109.AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    st.subheader("Documentation Visuelle")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
        
        if st.button("🔥 Générer le Catalogue Complet", use_container_width=True):
            if not model:
                st.error("L'IA n'est pas configurée. Ajoutez GEMINI_API_KEY dans les Secrets Streamlit.")
            else:
                with st.spinner("Interrogation des bases mondiales..."):
                    # Prompt optimisé pour gemini-pro
                    prompt = f"""Liste au moins 30 correspondances Aftermarket pour la référence OE {oe_input}.
                    Format : MARQUE | RÉFÉRENCE | DESCRIPTION | CRITÈRES TECHNIQUES
                    Inclus impérativement : Purflux, Mann, Bosch, Mahle, Febi, Meyle, Ridex."""
                    
                    try:
                        response = model.generate_content(prompt)
                        lines = response.text.strip().split('\n')
                        results = []
                        for line in lines:
                            if '|' in line:
                                p = [x.strip() for x in line.split('|')]
                                if len(p) >= 2:
                                    results.append({
                                        "Marque": p[0].upper(),
                                        "Référence": p[1],
                                        "Description": p[2] if len(p) > 2 else "Pièce",
                                        "Critères": p[3] if len(p) > 3 else "N/A"
                                    })
                        
                        if results:
                            df = pd.DataFrame(results)
                            df['Statut'] = df['Marque'].apply(lambda x: "⭐ PREMIUM" if any(m in x for m in PREMIUM) else "Standard")
                            st.success(f"✅ {len(df)} correspondances trouvées.")
                            st.dataframe(df.sort_values("Statut", ascending=False), use_container_width=True, hide_index=True)
                    except Exception as e:
                        st.error(f"Erreur lors de la génération : {e}")
