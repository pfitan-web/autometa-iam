import streamlit as st
import pandas as pd
from google import genai
from groq import Groq
import os

# 1. CONFIGURATION INTERFACE (Restauration des onglets d'origine)
st.set_page_config(page_title="AutoMeta-IAM v6.6", layout="wide")

# Récupération des secrets
gemini_key = st.secrets.get("GEMINI_API_KEY")
groq_key = st.secrets.get("GROQ_API_KEY")

# 2. BARRE LATÉRALE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
engine_type = st.sidebar.radio("Moteur IA :", ["Gemini 2.0 (Google)", "Groq (Secours Gratuit)"])

if engine_type == "Gemini 2.0 (Google)":
    model_choice = "gemini-2.0-flash-exp"
    st.sidebar.info("Modèle 2.0 : Stable, sans erreur 404.")
else:
    model_choice = st.sidebar.selectbox("Modèle Groq :", ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b"])

oe_input = st.sidebar.text_input("Référence OE", value="1109AY")

# 3. STRUCTURE DES ONGLETS (Restauration de la partie OEM)
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE COMPLET IAM"])

with tab1:
    st.markdown("### 🛠️ Schémas Constructeurs (Tradesoft)")
    # Restauration de l'Iframe qui avait disparu
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=800, scrolling=True)

with tab2:
    st.markdown(f"### 📋 Expertise Aftermarket : `{oe_input.upper()}`")
    
    if st.button("🔥 Lancer l'Analyse Massive", use_container_width=True):
        with st.spinner(f"Extraction technique via {model_choice}..."):
            try:
                # SUPER PROMPT DE VÉRIFICATION DES FAITS
                # On demande à l'IA d'être honnête : si elle ne sait pas, elle ne doit pas inventer.
                expert_prompt = f"""
                Tu es un expert en pièces détachées automobiles. Pour la référence OE {oe_input} :
                1. Fournis uniquement des correspondances Aftermarket RÉELLES (ex: Purflux, Mann, Bosch).
                2. Si tu ne connais pas les dimensions exactes, écris 'À vérifier' au lieu d'inventer des chiffres.
                3. Ne répète pas la référence OE dans la colonne 'Référence' pour toutes les marques.
                
                Format : MARQUE | RÉFÉRENCE | CARACTÉRISTIQUES
                """
                
                if "gemini" in model_choice:
                    client = genai.Client(api_key=gemini_key)
                    response = client.models.generate_content(model=model_choice, contents=expert_prompt)
                    raw_text = response.text
                else:
                    client = Groq(api_key=groq_key)
                    completion = client.chat.completions.create(
                        model=model_choice,
                        messages=[{"role": "user", "content": expert_prompt}]
                    )
                    raw_text = completion.choices[0].message.content

                if raw_text:
                    data = []
                    for line in raw_text.strip().split('\n'):
                        if '|' in line and "MARQUE" not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) >= 2:
                                data.append({"Marque": cols[0], "Référence": cols[1], "Détails": cols[2] if len(cols)>2 else ""})
                    
                    df = pd.DataFrame(data)
                    st.success(f"✅ {len(df)} références identifiées.")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
            except Exception as e:
                if "429" in str(e):
                    st.error("🚨 Quota Google épuisé. Utilisez Groq à gauche.")
                else:
                    st.error(f"Erreur : {e}")
