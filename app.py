import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM", layout="wide")

# 2. CHARGEMENT DES SECRETS
load_dotenv()
pl24_user = os.getenv("PL24_USER") or st.secrets.get("PL24_USER")

# 3. BARRE LATÉRALE
st.sidebar.title("🚀 AutoMeta-IAM")

# Section Identifiants
st.sidebar.subheader("1. Identification Véhicule")
vin_input = st.sidebar.text_input("VIN (Châssis)", placeholder="Coller le VIN ici...")

# Section Pièce
st.sidebar.subheader("2. Recherche Pièce")
oe_input = st.sidebar.text_input("Référence OE", placeholder="Ex: 03L253010G")

# Option de filtrage (Simule l'IA pour l'instant)
strict_mode = st.sidebar.checkbox("🎯 Mode Strict (VAG)", value=True, help="Si coché, recherche la correspondance exacte (lettre de fin incluse).")

st.sidebar.divider()

# Statut connexion
if pl24_user:
    st.sidebar.success(f"🟢 PartsLink24 : Connecté")
else:
    st.sidebar.caption("🔴 PartsLink24 : Non connecté")

# 4. STRUCTURE PRINCIPALE
col_oem, col_iam = st.columns([0.50, 0.50], gap="medium")

# --- COLONNE GAUCHE : VISUALISATION OEM ---
with col_oem:
    st.subheader("🖼️ Univers Constructeur")
    
    tab_visu, tab_outils = st.tabs(["👁️ Vue Éclatée (TradeSoft)", "🔗 Accès Rapides"])
    
    with tab_visu:
        st.info("💡 Sélectionnez le modèle manuellement ci-dessous.")
        ts_url = "https://ar-demo.tradesoft.pro/cats/#/catalogs"
        st.components.v1.iframe(ts_url, height=600, scrolling=True)

    with tab_outils:
        st.markdown("### 🚀 Lanceurs de Catalogues")
        
        # Grille de boutons
        b1, b2, b3 = st.columns(3)
        
        with b1:
            # PartSouq (Accueil, car sans marque on ne peut pas deep-link)
            st.link_button("Partsouq", "https://partsouq.com/", use_container_width=True)
            
        with b2:
            st.link_button("PartsLink24", "https://www.partslink24.com/", use_container_width=True)
            
        with b3:
            st.link_button("CatCar Info", "https://www.catcar.info/en/", use_container_width=True)
            
        if vin_input:
            st.success(f"📋 VIN `{vin_input}` copié (visuellement) pour usage rapide.")

# --- COLONNE DROITE : INTELLIGENCE IAM ---
with col_iam:
    st.subheader("🔧 Cross-Reference & Prix")
    
    if oe_input:
        # Nettoyage standardisé
        clean_oe = oe_input.replace(" ", "").upper() # On garde les points ou non selon ta pref, ici on garde brut sans espace
        url_ref = clean_oe.replace(".", "") # Version sans point pour les URL
        
        st.markdown(f"**Analyse de :** `{clean_oe}`")
        
        if strict_mode:
             st.caption("🎯 Filtre actif : Recherche de correspondance stricte (Suffixes importants)")

        st.divider()

        # B. MOTEUR DE RECHERCHE EXTERNE (Daparto / DistriAuto)
        st.markdown("### 🌍 Comparateurs (Moteur TecDoc)")
        
        # Mise à jour des URLs selon tes consignes exactes
        url_daparto = f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{url_ref}?ref=fulltext"
        url_distri = f"https://www.distriauto.fr/pieces-auto/oem/{url_ref}"
        
        c1, c2 = st.columns(2)
        with c1:
            st.link_button(f"🔎 Daparto ({clean_oe})", url_daparto, use_container_width=True)
        with c2:
            st.link_button(f"📦 DistriAuto ({clean_oe})", url_distri, use_container_width=True)

        # Placeholder pour future IA Gemini
        with st.expander("🧠 Analyseur IA (Bientôt disponible)"):
            st.write("Ici s'affichera l'analyse sémantique Gemini pour confirmer la compatibilité des versions (Ex: G vs H).")

    else:
        st.info("👈 Saisissez une référence OE pour générer les liens comparateurs.")

# FOOTER
st.divider()
st.caption("AutoMeta-IAM v2.0 | Clean Version")