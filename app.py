import streamlit as st

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v9.9", layout="wide")

# --- 2. GÉNÉRATION DES URLS EXACTES ---
def get_expert_links(oe_ref):
    clean_ref = oe_ref.replace(".", "").replace(" ", "").lower()
    return [
        {"Plateforme": "DISTRIAUTO", "URL": f"https://www.distriauto.fr/pieces-auto/oem/{clean_ref}", "Note": "Base OEM"},
        {"Plateforme": "DAPARTO", "URL": f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean_ref}?ref=fulltext", "Note": "Comparateur"},
        {"Plateforme": "OSCARO", "URL": f"https://www.oscaro.com/fr/search?q={clean_ref}", "Note": "Catalogue FR"},
        {"Plateforme": "AUTODOC", "URL": f"https://www.auto-doc.fr/search?keyword={clean_ref}", "Note": "Fiche Technique"}
    ]

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

oe_input = st.sidebar.text_input("📦 Référence OE", value="")

if oe_input:
    st.sidebar.markdown(f'[🔗 PARTSOUQ ({oe_input.upper()})](https://partsouq.com/en/search/all?q={oe_input})')
    st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. EXPERTISE AFTERMARKET"])

with tab1:
    # On n'affiche le titre et l'iframe que si nécessaire ou par défaut
    if vin_input:
        st.subheader(f"🛠️ Analyse VIN : `{vin_input.upper()}`")
    elif oe_input:
        st.subheader(f"🛠️ Analyse par Référence : `{oe_input.upper()}`")
    else:
        st.subheader("🛠️ Accès Catalogue OEM")
    
    st.components.v1.iframe("
