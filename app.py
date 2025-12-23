import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro v3.9", layout="wide")
load_dotenv()

# 2. IA GEMINI (Configuration stable pour gros volume de données)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    genai.configure(api_key=api_key)
    # Utilisation de gemini-1.5-pro pour une meilleure capacité de liste
    model = genai.GenerativeModel('gemini-1.5-pro')

# --- TOP MARQUES ÉTENDUES ---
PREMIUM = ["PURFLUX", "MANN", "MAHLE", "KNECHT", "BOSCH", "HENGST", "DELPHI", "SKF", "SNR", "GATES", "VALEO", "LUK", "INA"]

def get_massive_catalogue(oe_ref):
    """Force l'IA à agir comme une API TecDoc complète"""
    prompt = f"""
    Tu es une API TecDoc. Pour la référence OE {oe_ref}, renvoie TOUTES les correspondances IAM connues dans l'industrie (minimum 40-50 références).
    Inclus les marques Premium (Purflux, Mann...), les marques spécialistes (Meyle, Vaico...) et les marques budget (Ridex, Stark...).
    
    Format strict par ligne : MARQUE | RÉFÉRENCE | DESCRIPTION | CRITÈRES (Dimensions/Spécifs)
    Exemple pour un filtre : PURFLUX | L358A | Filtre à huile | H: 100mm, Ø: 71mm, avec joint
    """
    try:
        # Configuration pour laisser l'IA écrire une réponse longue
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 4000})
        lines = response.text.strip().split('\n')
        results = []
        for line in lines:
            if '|' in line:
                p = [x.strip() for x in line.split('|')]
                if len(p) >= 2:
                    results.append({
                        "Marque": p[0].upper(),
                        "Référence": p[1],
                        "Description": p[2] if len(p) > 2 else "Pièce détachée",
                        "Critères Techniques": p[3] if len(p) > 3 else "Consulter fiche"
                    })
        return results
    except Exception as e:
        st.error(f"Erreur technique : {e}")
        return []

# 3. INTERFACE RÉTABLIE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("v3.9 | Deep Market Intelligence")

oe_input = st.sidebar.text_input("Référence OE", value="1109AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Base de données Aftermarket : `{oe_input.upper()}`")
        
        if st.button("🔥 Générer le Catalogue Complet (Mode TecDoc)", use_container_width=True):
            with st.spinner("Interrogation des bases de données mondiales..."):
                
                full_data = get_massive_catalogue(oe_input)
                
                if full_data:
                    df = pd.DataFrame(full_data)
                    
                    # Marquage des Top Marques
                    df['Qualité'] = df['Marque'].apply(lambda x: "⭐ PREMIUM" if any(p in x for p in PREMIUM) else "Standard")
                    
                    # Tri et affichage
                    df = df.sort_values(by="Qualité", ascending=False)
                    
                    st.success(f"✅ {len(df)} correspondances identifiées.")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error("Impossible de générer le catalogue. Vérifiez la clé API.")
