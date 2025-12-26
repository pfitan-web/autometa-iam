import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v14.4", layout="wide")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", None)
HOST = "tecdoc-catalog.p.rapidapi.com"

# Paramètres régionaux validés
LANG_ID = "6"
COUNTRY_ID = "85"
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

# --- 2. FONCTIONS API ---

@st.cache_data(ttl=600)
def get_clean_iam(oem_ref):
    """Recherche Aftermarket dédoublonnée avec indicateur de copie"""
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
                        "Référence": f"{ref_no} 📋", # Symbole visuel pour l'utilisateur
                        "Ref_Pure": ref_no,           # Garde la ref propre pour les API/Fiches
                        "Produit": item.get('articleProductName'),
                        "articleId": item.get('articleId'),
                        "is_premium": is_p
                    }
            return list(unique_refs.values())
        return []
    except: return []

def get_specs_official(article_id):
    """Extraction technique par ID Article"""
    url = f"https://{HOST}/api/v1/articles/selection-of-all-specifications-criterias-for-the-article/article-id/{article_id}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except: return []

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")
st.sidebar.subheader("🔗 Liens Directs")
# Lien Partsouq dynamique restauré
st.sidebar.markdown(f'<a href="https://partsouq.com/en/search/all?q={vin_input}" target="_blank">🚀 PARTSOUQ VIN</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

# --- 4. INTERFACE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. ANALYSE TECDOC"])

with tab1:
    if vin_input:
        c1, c2 = st.columns(2)
        c1.link_button("🚀 Partsouq", f"https://partsouq.com/en/search/all?q={vin_input}")
        c2.link_button("🚘 SIV", "https://www.siv-auto.fr/")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700, scrolling=True)

with tab2:
    oe_input = st.text_input("📦 Référence OE Aftermarket", value="1109AY").upper()
    
    if oe_input:
        data = get_clean_iam(oe_input)
        if data:
            df_main = pd.DataFrame(data)
            premium = df_main[df_main['is_premium']]
            others = df_main[~df_main['is_premium']]

            st.markdown("### 🏆 Sélection Premium")
            st.dataframe(
                premium[["Photo", "Marque", "Référence", "Produit"]], 
                column_config={
                    "Photo": st.column_config.ImageColumn("Visuel"),
                    "Référence": st.column_config.TextColumn(
                        "Référence", 
                        help="Double-cliquez sur la cellule pour copier la référence rapidement."
                    )
                }, 
                hide_index=True, width="stretch"
            )

            st.divider()
            st.subheader("📏 Fiche Technique & Copie Rapide")
            
            choice = st.selectbox("Choisir une référence pour les dimensions :", 
                                [f"{x['Marque']} - {x['Ref_Pure']}" for x in data],
                                key="spec_selector")
            
            selected_item = next(x for x in data if f"{x['Marque']} - {x['Ref_Pure']}" == choice)
            
            # Bloc de copie dédié (le plus efficace)
            st.info(f"📋 Copier la référence {choice} :")
            st.code(selected_item['Ref_Pure'], language="text") 
            
            with st.spinner("Analyse technique..."):
                specs = get_specs_official(selected_item['articleId'])
                if specs:
                    cols = st.columns(4)
                    for idx, s in enumerate(specs):
                        cols[idx % 4].metric(label=s.get('criteriaDescription'), value=s.get('criteriaValue'))
                else:
                    st.warning(f"⚠️ Aucune donnée technique pour l'ID {selected_item['articleId']}.")

            with st.expander("📦 Voir le reste du catalogue"):
                st.dataframe(others[["Photo", "Marque", "Référence", "Produit"]], 
                             column_config={"Photo": st.column_config.ImageColumn()}, 
                             hide_index=True, width="stretch")

# --- 5. FOOTER ---
st.divider()
clean = oe_input.lower().replace(" ", "")
cx1, cx2, cx3, cx4 = st.columns(4)
cx1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean}")
cx2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean}")
cx3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean}")
cx4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean}")
