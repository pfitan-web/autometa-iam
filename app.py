import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v9.8", layout="wide")

# --- 2. GÉNÉRATION DES URLS EXACTES ---
def get_expert_links(oe_ref):
    # Nettoyage de la référence pour les URLs
    clean_ref = oe_ref.replace(".", "").replace(" ", "").lower()
    
    links = [
        {
            "Plateforme": "DISTRIAUTO",
            "URL": f"https://www.distriauto.fr/pieces-auto/oem/{clean_ref}",
            "Note": "Accès direct base OEM"
        },
        {
            "Plateforme": "DAPARTO",
            "URL": f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean_ref}?ref=fulltext",
            "Note": "Comparateur Aftermarket"
        },
        {
            "Plateforme": "OSCARO",
            "URL": f"https://www.oscaro.com/fr/search?q={clean_ref}",
            "Note": "Vérification compatibilité"
        },
        {
            "Plateforme": "AUTODOC",
            "URL": f"https://www.auto-doc.fr/search?keyword={clean_ref}",
            "Note": "Fiches techniques détaillées"
        }
    ]
    return links

# --- 3. BARRE LATÉRALE (Intégrité Totale Restaurée) ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

# Référence OE pour dynamisme
oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")

st.sidebar.markdown(f'[🔗 PARTSOUQ ({oe_input})](https://partsouq.com/en/search/all?q={oe_input})')
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

st.sidebar.divider()

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. EXPERTISE MULTI-CATALOGUES"])

with tab1:
    st.markdown(f"### 🛠️ Schémas Constructeurs : `{oe_input.upper()}`")
    if vin_input:
        st.info(f"VIN détecté : **{vin_input.upper()}**")
    # Iframe Tradesoft (Maintenue)
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)

with tab2:
    st.markdown(f"### 📋 Analyse Multi-Sources pour `{oe_input.upper()}`")
    st.write("Cliquez sur les boutons ci-dessous pour ouvrir les fiches techniques exactes :")
    
    expert_links = get_expert_links(oe_input)
    
    # Affichage en colonnes pour un aspect "Dashboard TecDoc"
    col1, col2 = st.columns(2)
    
    for i, link in enumerate(expert_links):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            with st.container(border=True):
                st.subheader(link["Plateforme"])
                st.caption(link["Note"])
                st.link_button(f"Ouvrir la fiche {oe_input}", link["URL"], use_container_width=True)

    st.divider()
    st.info("💡 **Astuce :** Ces liens pointent vers les pages de résultats 'fulltext' ou 'oem' pour garantir que vous tombez directement sur les caractéristiques de la pièce.")
