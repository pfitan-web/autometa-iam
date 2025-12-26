import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v14.1", layout="wide")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", None)
HOST = "tecdoc-catalog.p.rapidapi.com"

# Configuration IDs validés par vos captures
LANG_ID = "6"      # Français
COUNTRY_ID = "85"  # France
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

# --- 2. FONCTIONS API ---

@st.cache_data(ttl=600)
def get_clean_iam(oem_ref):
    """Recherche Aftermarket avec dédoublonnage"""
    clean_ref = oem_ref.replace(" ", "").upper()
    url = f"https://{HOST}/articles-oem/search-by-article-oem-no/lang-id/{LANG_ID}/article-oem-no/{clean_ref}"
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
                        "Produit": item.get('articleProductName'),
                        "articleId": item.get('articleId'),
                        "is_premium": is_p
                    }
            return list(unique_refs.values())
        return []
    except: return []

def get_specs_force(article_id):
    """Extraction des critères techniques"""
    url = f"https://{HOST}/api/v1/articles/selection-of-all-specifications-criterias-for-the-article/article-id/{article_id}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except: return []

# --- 3. BARRE LATÉRALE (Restauration Liens) ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")
st.sidebar.subheader("🔗 Liens Directs")
st.sidebar.markdown(f'<a href="https://partsouq.com/en/search/all?q={vin_input}" target="_blank">🚀 PARTSOUQ VIN</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

# --- 4. INTERFACE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. ANALYSE TECDOC"])

with tab1:
    if vin_input:
        st.subheader(f"🛠️ Recherche VIN : `{vin_input.upper()}`")
        c1, c2 = st.columns(2)
        c1.link_button("🚀 Partsouq", f"https://partsouq.com/en/search/all?q={vin_input}")
        c2.link_button("🚘 SIV", "https://www.siv-auto.fr/")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700, scrolling=True)

with tab2:
    oe_input = st.text_input("📦 Référence OE pour analyse Aftermarket", value="1109AY").upper()
    
    if oe_input:
        data = get_clean_iam(oe_input)
        if data:
            premium = [i for i in data if i['is_premium']]
            others = [i for i in data if not i['is_premium']]

            st.markdown("### 🏆 Sélection Premium (Unique)")
            st.dataframe(pd.DataFrame(premium), column_config={"Photo": st.column_config.ImageColumn("Visuel"), "articleId": None, "is_premium": None}, hide_index=True, width="stretch")

            st.divider()
            st.subheader("📏 Fiche Technique (Auto-Refresh)")
            
            # Utilisation d'une clé unique pour forcer le rafraîchissement
            all_list = premium + others
            choice = st.selectbox("Choisir une référence pour extraire les cotes :", 
                                [f"{x['Marque']} - {x['Référence']}" for x in all_list],
                                key="selector_specs")
            
            selected_item = next(x for x in all_list if f"{x['Marque']} - {x['Référence']}" == choice)
            
            with st.spinner(f"Interrogation API pour {choice}..."):
                specs = get_specs_force(selected_item['articleId'])
                if specs:
                    # Affichage clair en metrics
                    cols = st.columns(4)
                    for idx, s in enumerate(specs):
                        cols[idx % 4].metric(label=s.get('criteriaDescription'), value=s.get('criteriaValue'))
                else:
                    st.warning(f"⚠️ Aucune donnée technique retournée par TecDoc pour l'ID {selected_item['articleId']}.")

            with st.expander("📦 Reste du catalogue"):
                st.dataframe(pd.DataFrame(others), column_config={"Photo": st.column_config.ImageColumn()}, hide_index=True, width="stretch")

st.divider()
cx1, cx2, cx3, cx4 = st.columns(4)
clean = oe_input.lower().replace(" ", "")
cx1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean}")
cx2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean}")
cx3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean}")
cx4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean}")
