import streamlit as st
import pandas as pd
from google import genai
from groq import Groq
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM v6.2", layout="wide")
load_dotenv()

# Récupération des clés
gemini_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

# 2. SELECTION DU MOTEUR FONCTIONNEL
st.sidebar.title("🤖 Moteurs d'Expertise")
# On ne garde que ce qui ne fait pas de 404 d'après vos tests
engine_type = st.sidebar.radio("Technologie :", ["Gemini 2.0 (Google)", "Llama 3.3 (Groq FREE)"])

if engine_type == "Gemini 2.0 (Google)":
    model_choice = "gemini-2.0-flash-exp" # Le seul qui passe sans 404
    st.sidebar.info("Modèle 2.0 actif. Attention aux limites de quota (429).")
else:
    model_choice = "llama-3.3-70b-versatile"
    st.sidebar.info("Modèle Llama 3 actif via Groq. Idéal si Gemini sature.")

oe_input = st.sidebar.text_input("Référence OE", value="1109AY")

# 3. LOGIQUE DE GÉNÉRATION SÉCURISÉE
def get_iam_data(model, oe):
    prompt = f"Génère un tableau de 40 correspondances IAM pour l'OE {oe}. Format: MARQUE | REF | DESC"
    
    if "gemini" in model:
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    else:
        # Moteur Groq totalement gratuit (nécessite une clé Groq)
        client = Groq(api_key=groq_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content

# 4. INTERFACE
tab1, tab2 = st.tabs(["🔍 VUES OEM", "📊 CATALOGUE IAM"])

with tab2:
    if st.button("🚀 Lancer l'Analyse Massive", use_container_width=True):
        with st.spinner(f"Interrogation de {model_choice}..."):
            try:
                raw_text = get_iam_data(model_choice, oe_input)
                if raw_text:
                    data = []
                    for line in raw_text.strip().split('\n'):
                        if '|' in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) >= 2:
                                data.append({
                                    "Marque": cols[0].upper(), 
                                    "Référence": cols[1], 
                                    "Note": cols[2] if len(cols)>2 else ""
                                })
                    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                    st.success(f"Analyse réussie avec {model_choice}")
            except Exception as e:
                if "429" in str(e):
                    st.error("🚨 Quota Gemini épuisé (429). Basculez sur 'Llama 3.3 (Groq)' à gauche !")
                elif "404" in str(e):
                    st.error("🚨 Erreur 404 : Ce modèle n'est plus supporté. Contactez le support.")
                else:
                    st.error(f"Erreur : {e}")
