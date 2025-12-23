import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION INTERFACE
st.set_page_config(page_title="AutoMeta-IAM Pro v4.0", layout="wide")
load_dotenv()

# Style pour une densité d'information maximale (Style TecDoc)
st.markdown("""
    <style>
    .stDataFrame { font-size: 12px; }
    thead tr th { background-color: #1f4e79 !important; color: white !important; font-weight: bold; }
    .main .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION IA (Correction de l'erreur 404)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Changement pour le modèle flash qui est le plus compatible actuellement
        model = genai.GenerativeModel('gemini-1.5-flash') 
    except Exception as e:
        st.error(f"Erreur API : {e}")

# 3. LISTE DES MARQUES PREMIUM (20/80)
PREMIUM = ["PURFLUX", "MANN", "MAHLE", "KNECHT", "BOSCH", "HENGST", "DELPHI", "SKF", "SNR", "GATES", "VALEO", "LUK", "INA", "DAYCO", "DENSO"]

# 4. STRUCTURE DE LA PAGE (On définit les onglets AVANT les erreurs potentielles)
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("v4.0 | Database Edition")
oe_input = st.sidebar.text_input("Référence OE", value="1109.AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    st.subheader("Documentation Visuelle")
    # Iframe de secours si l'autre est bloquée
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700, scrolling=True)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
        
        if st.button("🔥 Générer le Catalogue Complet (Mode TecDoc)", use_container_width=True):
            if not model:
                st.error("L'IA n'est pas connectée. Vérifiez votre clé API dans les Secrets.")
            else:
                with st.spinner("Interrogation des bases de données mondiales..."):
                    # Prompt ultra-direct pour forcer le volume de données
                    prompt = f"""
                    Agis comme une base de données TecDoc. Pour la référence OE {oe_input}, liste TOUTES les correspondances Aftermarket.
                    Je veux un maximum de résultats (cible 50+).
                    Structure : MARQUE | RÉFÉRENCE | DESCRIPTION | CRITÈRES TECHNIQUES (Dimensions, cotes)
                    Inclus : Purflux, Mann, Bosch, Mahle, Febi, Meyle, Ridex, Stark, Mapco, etc.
                    """
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
                                        "Critères (Cotes)": p[3] if len(p) > 3 else "N/A"
                                    })
                        
                        if results:
                            df = pd.DataFrame(results)
                            # Marquage Premium
                            df['Statut'] = df['Marque'].apply(lambda x: "⭐ PREMIUM" if any(m in x for m in PREMIUM) else "Standard")
                            df = df.sort_values(by="Statut", ascending=False)
                            
                            st.success(f"✅ {len(df)} correspondances identifiées.")
                            st.dataframe(df, use_container_width=True, hide_index=True)
                        else:
                            st.warning("Aucune donnée générée. Essayez de reformuler la référence.")
                    except Exception as e:
                        st.error(f"Erreur de génération : {e}")
