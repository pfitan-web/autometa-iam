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
    
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=800, scrolling=True)

with tab2:
    if not oe_input:
        st.warning("⚠️ Veuillez saisir une référence OE dans la barre latérale pour lancer l'expertise.")
    else:
        st.subheader(f"📊 Analyse Multi-Sources : `{oe_input.upper()}`")
        
        expert_links = get_expert_links(oe_input)
        col1, col2 = st.columns(2)
        
        for i, link in enumerate(expert_links):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                with st.container(border=True):
                    st.write(f"**{link['Plateforme']}**")
                    st.link_button(f"Ouvrir {oe_input.upper()}", link["URL"], use_container_width=True)
