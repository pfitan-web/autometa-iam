import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v14.0", layout="wide")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", None)
HOST = "tecdoc-catalog.p.rapidapi.com"

PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

# --- 2. FONCTIONS API ---

@st.cache_data(ttl=3600) # Cache pour éviter de consommer du quota inutilement
def get_full_data(oem_ref):
    """Simule un agent : Récupère TOUT d'un coup (IAM + Photos)"""
    clean_ref = oem_ref.replace(" ", "").upper()
    url = f"https://{HOST}/articles-oem/search-by-article-oem-no/lang-id/6/article-oem-no/{clean_ref}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            unique_refs = {}
            for item in res.json():
                ref_no = item.get('articleNo')
                if ref_no not in unique_refs:
                    brand = item.get('supplierName', '').upper()
                    is_p = any(p in brand for p in PREMIUM_BRANDS)
                    unique_refs[ref_no] = {
                        "Photo": item.get('s3image'),
                        "Marque": f"⭐ {brand}" if is_p else brand,
                        "Référence": ref_no,
                        "Désignation": item.get('articleProductName'),
                        "ID": item.get('articleId'),
                        "is_premium": is_p
                    }
            return list(unique_refs.values())
        return []
    except: return []

def get_specs_direct(article_id):
    """Récupère les dimensions sans passer par le session_state instable"""
    url = f"https://{HOST}/api/v1/articles/selection-of-all-specifications-criterias-for-the-article/article-id/{article_id}/lang-id/6/country-filter-id/85"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except: return []

# --- 3. INTERFACE (Restauration stricte OEM) ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. ANALYSE TECDOC"])

with tab1:
    if vin_input:
        st.subheader(f"🛠️ VIN : `{vin_input.upper()}`")
        st.link_button("🚀 Partsouq VIN", f"https://partsouq.com/en/search/all?q={vin_input}")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700, scrolling=True)

with tab2:
    oe_input = st.text_input("📦 Référence OE Aftermarket", value="1109AY").upper()
    
    if oe_input:
        data = get_full_data(oe_input)
        
        if data:
            premium = [i for i in data if i['is_premium']]
            others = [i for i in data if not i['is_premium']]

            # --- TABLEAU PRINCIPAL ---
            st.markdown("### 🏆 Sélection Premium")
            st.dataframe(
                pd.DataFrame(premium),
                column_config={"Photo": st.column_config.ImageColumn("Visuel"), "ID": None, "is_premium": None},
                hide_index=True, width="stretch"
            )

            # --- ANALYSE TECHNIQUE (Logique sans bouton pour éviter les bugs) ---
            st.divider()
            st.subheader("📏 Fiche Technique Détaillée")
            
            # Utilisation d'un sélecteur simple qui déclenche l'affichage auto
            all_list = premium + others[:5]
            choice = st.selectbox("Choisir une référence pour voir les cotes :", 
                                [f"{x['Marque']} - {x['Référence']}" for x in all_list])
            
            # On trouve l'ID immédiatement
            selected_id = next(x['ID'] for x in all_list if f"{x['Marque']} - {x['Référence']}" == choice)
            
            with st.spinner("Chargement des dimensions..."):
                specs = get_specs_direct(selected_id)
                if specs:
                    # Affichage en colonnes pour plus de clarté (comme en magasin)
                    cols = st.columns(4)
                    for idx, s in enumerate(specs):
                        cols[idx % 4].metric(label=s.get('criteriaDescription'), value=s.get('criteriaValue'))
                else:
                    st.warning("Aucune donnée technique pour cette référence précise.")

            with st.expander("📦 Reste du catalogue"):
                st.dataframe(pd.DataFrame(others), column_config={"Photo": st.column_config.ImageColumn()}, hide_index=True, width="stretch")
        else:
            st.error("Aucune donnée reçue. Vérifiez votre clé API ou la référence.")

st.divider()
# Liens de secours maintenus
cx1, cx2, cx3, cx4 = st.columns(4)
clean = oe_input.lower().replace(" ", "")
cx1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean}")
cx2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean}")
cx3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean}")
cx4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean}")
