import streamlit as st

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v10.0", layout="wide")

# --- 2. GÉNÉRATION DES URLS D'EXPERTISE ---
def get_expert_links(oe_ref):
    clean_ref = oe_ref.replace(".", "").replace(" ", "").lower()
    return [
        {"Plateforme": "DISTRIAUTO", "URL": f"https://www.distriauto.fr/pieces-auto/oem/{clean_ref}"},
        {"Plateforme": "DAPARTO", "URL": f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean_ref}?ref=fulltext"},
        {"Plateforme": "OSCARO", "URL": f"https://www.oscaro.com/fr/search?q={clean_ref}"},
        {"Plateforme": "AUTODOC", "URL": f"https://www.auto-doc.fr/search?keyword={clean_ref}"}
    ]

# --- 3. BARRE LATÉRALE (Accès Permanents) ---
st.sidebar.title("⚙️ Expertise Pro")

vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.subheader("🔗 Liens de Recherche")
# Les liens sont maintenant fixes pour permettre votre workflow
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)
st.sidebar.markdown('[🔗 PARTSOUQ](https://partsouq.com/)')
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

st.sidebar.divider()

oe_input = st.sidebar.text_input("📦 Référence OE", value="")

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. EXPERTISE AFTERMARKET"])

with tab1:
    # Affichage épuré : Priorité au VIN, puis OE, sinon titre neutre
    if vin_input:
        st.subheader(f"🛠️ VIN : `{vin_input.upper()}`")
    elif oe_input:
        st.subheader(f"🛠️ OE : `{oe_input.upper()}`")
    else:
        st.subheader("🛠️ Catalogue OEM")
    
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=800, scrolling=True)

with tab2:
    if oe_input:
        st.subheader(f"📊 Analyse : `{oe_input.upper()}`")
        
        expert_links = get_expert_links(oe_input)
        col1, col2 = st.columns(2)
        
        for i, link in enumerate(expert_links):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                with st.container(border=True):
                    st.write(f"**{link['Plateforme']}**")
                    st.link_button(f"Ouvrir {oe_input.upper()}", link["URL"], use_container_width=True)
    else:
        st.info("Saisissez une référence OE pour générer les accès aux catalogues IAM.")
