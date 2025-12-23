import streamlit as st
import pandas as pd
from google import genai
from groq import Groq
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM v6.4", layout="wide")
load_dotenv()

# Récupération des clés sécurisées
gemini_key = st.secrets.get("GEMINI_API_KEY")
groq_key = st.secrets.get("GROQ_API_KEY")

# 2. BARRE LATÉRALE : SÉLECTEUR DE MOTEUR
st.sidebar.title("🚀 Intelligence Engine")
engine_type = st.sidebar.radio("Fournisseur :", ["Gemini 2.0 (Google)", "Groq (Multi-LLMs FREE)"])

if engine_type == "Gemini 2.0 (Google)":
    model_choice = "gemini-2.0-flash-exp"
    st.sidebar.info("Modèle 2.0 actif (0% erreur 404).")
else:
    model_choice = st.sidebar.selectbox(
        "Modèle Groq Gratuit :", 
        [
            "llama-3.3-70b-versatile", 
            "llama-3.1-8b-instant", 
            "mixtral-8x7b-32768",
            "deepseek-r1-distill-llama-70b"
        ]
    )
    st.sidebar.success("Moteur Groq 100% Gratuit actif.")

oe_input = st.sidebar.text_input("Référence OE", value="1109AY")

# 3. LE SUPER PROMPT EXPERT
def get_expert_prompt(oe):
    return f"""
    Tu es un expert mondial en bases de données Aftermarket automobile (type TecDoc).
    Ta mission est d'extraire les correspondances exactes pour la référence OE : {oe}.
    
    CONSIGNES STRICTES :
    1. Liste 50 correspondances (marques premium et secondaires).
    2. Pour chaque ligne, inclus : Marque | Référence | Spécifications techniques.
    3. Spécifications attendues : Dimensions (Hauteur, Diamètre), Type de joint, ou Pression si disponible.
    4. Marques prioritaires : Purflux, Mann-Filter, Bosch, Mahle, Valeo, Hengst, Febi, UFI.
    
    FORMAT DE RÉPONSE :
    MARQUE | RÉFÉRENCE | SPÉCIFICATIONS
    """

# 4. LOGIQUE DE GÉNÉRATION
def get_iam_data(model, oe):
    prompt = get_expert_prompt(oe)
    
    if "gemini" in model:
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    else:
        client = Groq(api_key=groq_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "Tu es un expert technique automobile."},
                      {"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content

# 5. AFFICHAGE DES RÉSULTATS
tab1, tab2 = st.tabs(["🔍 VUES OEM", "📊 CATALOGUE IAM EXPERT"])

with tab2:
    if st.button("🔥 Générer l'Analyse Massive", use_container_width=True):
        if not (gemini_key or groq_key):
            st.error("Aucune clé API détectée dans le fichier secrets.toml.")
        else:
            with st.spinner(f"Extraction technique via {model_choice}..."):
                try:
                    raw_text = get_iam_data(model_choice, oe_input)
                    if raw_text:
                        data = []
                        for line in raw_text.strip().split('\n'):
                            if '|' in line and "MARQUE" not in line:
                                cols = [c.strip() for c in line.split('|')]
                                if len(cols) >= 2:
                                    data.append({
                                        "Marque": cols[0].upper(),
                                        "Référence": cols[1],
                                        "Spécifications Techniques": cols[2] if len(cols) > 2 else "N/A"
                                    })
                        
                        df = pd.DataFrame(data)
                        st.success(f"✅ {len(df)} références identifiées.")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Bouton de téléchargement
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Télécharger le catalogue (CSV)", csv, "catalogue.csv", "text/csv")
                
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 Quota Gemini épuisé. Basculez sur Groq (Llama 3.3) à gauche !")
                    else:
                        st.error(f"Détail de l'erreur : {e}")
