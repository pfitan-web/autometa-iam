import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="AutoMeta-IAM Pro v13.3", layout="wide")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", None)
HOST = "tecdoc-catalog.p.rapidapi.com"

# Marques Premium
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

# --- 2. FONCTIONS API ---

def get_clean_iam(oem_ref):
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
                    # Ajout du badge visuel si Premium
                    is_p = any(p in brand for p in PREMIUM_BRANDS)
                    display_brand = f"⭐ {brand}" if is_p else brand
                    
                    unique_refs[ref_no] = {
                        "Aperçu": item.get('s3image'),
                        "Marque": display_brand,
                        "Référence": ref_no,
                        "Produit": item.get('articleProductName'),
                        "ID": item.get('articleId'),
                        "is_premium": is_p
                    }
            return list(unique_refs.values())
        return []
    except: return []

def get_technical_specs(article_id):
    # Utilisation de l'endpoint exact de votre curl
    url = f"https://{HOST}/api/v1/articles/selection-of-all-specifications-criterias-for-the-article/article-id/{article_id}/lang-id/6/country-filter-id/85"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except: return []

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")
st.sidebar.subheader("🔗 Liens de Recherche")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)
st.sidebar.markdown('[🔗 PARTSOUQ](https://partsouq.com/)')
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. ANALYSE TECDOC FRANCE"])

with tab1:
    if vin_input:
        st.subheader(f"🛠️ VIN : `{vin_input.upper()}`")
        c1, c2, c3 = st.columns(3)
        c1.link_button("🚀 Partsouq VIN", f"https://partsouq.com/en/search/all?q={vin_input}")
        c2.link_button("🇯🇵 Amayama", f"https://www.amayama.com/en/search?q={vin_input}")
        c3.link_button("🚘 SIV Auto", "https://www.siv-auto.fr/")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=800, scrolling=True)

with tab2:
    oe_input = st.text_input("📦 Référence OE Aftermarket", value="1109AY").upper()
    
    if oe_input:
        with st.spinner("Analyse du catalogue..."):
            items = get_clean_iam(oe_input)
            
            if items:
                premium = [i for i in items if i['is_premium']]
                others = [i for i in items if not i['is_premium']]

                st.markdown("### 🏆 Sélection Premium")
                st.dataframe(
                    pd.DataFrame(premium),
                    column_config={"Aperçu": st.column_config.ImageColumn("Photo", width="small"), "ID": None, "is_premium": None},
                    hide_index=True,
                    width="stretch"
                )
                
                st.divider()
                st.subheader("📏 Comparateur Technique")
                
                # Correction du bouton avec session_state
                col_sel, col_act = st.columns([3, 1])
                with col_sel:
                    options = {f"{x['Marque']} - {x['Référence']}": x['ID'] for x in premium + others[:10]}
                    selected_label = st.selectbox("Sélectionner une pièce :", options.keys())
                
                with col_act:
                    if st.button("🚀 Extraire Dimensions"):
                        st.session_state.current_specs = get_technical_specs(options[selected_label])
                        st.session_state.current_label = selected_label

                # Affichage des résultats si présents en session
                if "current_specs" in st.session_state and st.session_state.current_specs:
                    st.info(f"Fiche technique : {st.session_state.current_label}")
                    specs_df = pd.DataFrame(st.session_state.current_specs)
                    if not specs_df.empty:
                        st.table(specs_df[['criteriaDescription', 'criteriaValue']].rename(columns={'criteriaDescription': 'Critère', 'criteriaValue': 'Valeur'}))
                    else:
                        st.warning("Aucune spécification trouvée pour cet ID.")

                with st.expander("📦 Reste du catalogue (Dédoublonné)"):
                    st.dataframe(pd.DataFrame(others), column_config={"Aperçu": st.column_config.ImageColumn(), "ID": None, "is_premium": None}, hide_index=True, width="stretch")
            else:
                st.warning("Aucune donnée trouvée.")

        st.divider()
        cx1, cx2, cx3, cx4 = st.columns(4)
        clean = oe_input.lower().replace(" ", "")
        cx1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean}")
        cx2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean}")
        cx3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean}")
        cx4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean}")
