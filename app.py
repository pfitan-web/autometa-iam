import streamlit as st
import os
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv()

st.title("AutoMeta-IAM 🏎️")

# Récupération sécurisée
user = os.getenv("PL24_USER")

if user:
    st.success(f"✅ Connexion sécurisée établie pour : {user}")
else:
    st.error("❌ Fichier .env non détecté ou vide.")

st.info("Ce message confirme que le code lit tes secrets localement sans les afficher publiquement.")