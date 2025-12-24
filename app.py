import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v9.7", layout="wide")

# --- 2. FONCTION DE GÉNÉRATION DE LIENS DIRECTS ---
def get_direct_catalog_links(oe_ref):
    clean_ref = oe_ref.replace(".", "").replace(" ", "").upper()
    
    # On construit les URLs exactes que ces sites utilisent pour les recherches
    links = [
        {
            "Plateforme": "DISTRIAUTO",
            "Action": "Voir les équivalences",
            "URL": f"https://www.distriauto.fr/recherche?q={clean_ref}"
        },
        {
            "Plateforme": "DAPARTO",
            "Action": "Comparer les prix IAM",
            "URL": f"https://www.daparto.fr/recherche-de-pieces/tous-les-fabricants/{clean_ref}"
        },
        {
            "Plateforme": "OSCARO",
            "Action": "Vérifier compatibilité",
            "URL": f"https://www.oscaro.com/recherche/?q={clean_ref}"
        },
        {
            "Plateforme": "AUTODOC",
            "Action": "Fiches techniques détaillées",
            "URL": f"https://www.autodoc.fr/search?keyword={clean_ref}"
        }
    ]
    return pd.DataFrame(links)

# --- 3. BARRE LATÉRALE (Intégrité Conservée) ---
st.sidebar.title("⚙️ Paramètres Expertise")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Entrez le VIN...")

st.sidebar.subheader("🔗 Accès Rapides")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")

# Partsouq dynamique
st.sidebar.markdown(f'[🔗 PARTSOUQ ({oe_input})](https://partsouq.com/en/search/all?q={oe_input})')
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. EXPERTISE AFTERMARKET"])

with tab1:
    st.markdown(f"### 🛠️ Schémas Constructeurs : `{oe_input.upper()}`")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)

with tab2:
    st.markdown(f"### 📋 Accès directs aux catalogues pour `{oe_input.upper()}`")
    st.info("Cette méthode garantit l'accès aux données réelles sans erreurs d'IA ou blocages de robots.")
    
    df_links = get_direct_catalog_links(oe_input)
    
    # Affichage sous forme de cartes cliquables pour une meilleure ergonomie
    for index, row in df_links.iterrows():
        with st.expander(f"🚀 {row['Plateforme']} - {row['Action']}", expanded=True):
            st.write(f"Recherche directe pour la référence **{oe_input}**")
            st.link_button(f"Ouvrir {row['Plateforme']}", row['URL'], use_container_width=True)

    st.divider()
    st.warning("💡 Note : Les dimensions techniques (hauteur, filetage) se trouvent directement sur les fiches produits de ces liens.")
