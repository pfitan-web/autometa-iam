import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide")

# --- 2. DÉTECTION DU MODE VIA LE NOUVEAU SECRET ---
# On récupère le type de version. Si rien n'est mis, on reste en PUBLIC par sécurité.
v_type = st.secrets.get("VERSION_TYPE", "PUBLIC_DEMO")

IS_PRIVATE = (v_type == "PRIVATE_EXPERT")
SYSTEM_KEY = st.secrets.get("RAPIDAPI_KEY", "")
PARTSLINK_LINK = st.secrets.get("PARTSLINK_URL", "")

# Quotas
if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("⚙️ AutoMeta")

# Indicateur de version pour vous aider à vérifier
if IS_PRIVATE:
    st.sidebar.success("🔐 MODE EXPERT ILLIMITÉ")
else:
    st.sidebar.info("🌐 MODE PUBLIC DÉMO")

st.sidebar.divider()
user_key = st.sidebar.text_input("🔑 Clé RapidAPI (Visiteur)", type="password")

# LOGIQUE DE DÉVERROUILLAGE
ACTIVE_KEY = SYSTEM_KEY
is_unlimited = False

if user_key:
    ACTIVE_KEY = user_key
    is_unlimited = True
elif IS_PRIVATE:
    is_unlimited = True
else:
    is_unlimited = False
    remaining = 2 - st.session_state.api_calls

# --- 4. AFFICHAGE DES LIENS ---
st.sidebar.subheader("🔗 Liens")
st.sidebar.markdown("🚀 [PARTSOUQ VIN](https://partsouq.com/)")

# Partslink n'apparaît QUE si on est en mode PRIVATE_EXPERT
if IS_PRIVATE and PARTSLINK_LINK:
    st.sidebar.divider()
    st.sidebar.markdown(f"**[🔐 ACCÈS PARTSLINK24]({PARTSLINK_LINK})**")

# --- 5. RECHERCHE TECDOC ---
oe_input = st.text_input("📦 Référence OE", value="1109AY").upper()

if oe_input:
    if not is_unlimited and st.session_state.api_calls >= 2:
        st.error("⛔ Quota démo épuisé. Entrez votre clé en sidebar.")
    else:
        # Ici votre fonction de recherche habituelle
        # ... (appels API)
        if not is_unlimited:
            st.session_state.api_calls += 1
            st.rerun()
        st.success(f"Analyse en cours avec la clé : {'Système' if not user_key else 'Utilisateur'}")
