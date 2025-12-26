import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="AutoMeta-IAM Pro v13.2", layout="wide")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", None)
HOST = "tecdoc-catalog.p.rapidapi.com"

# Marques Premium pour le filtrage Aftermarket
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

# --- 2. FONCTIONS API (Incrémentées) ---

def get_clean_iam(oem_ref):
    """Recherche IAM dédoublonnée par articleNo"""
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
                    unique_refs[ref_no] = {
                        "Aperçu": item.get('s3image'),
                        "Marque": item.get('supplierName', '').upper(),
                        "Référence": ref_no,
                        "Produit": item.get('articleProductName'),
                        "ID": item.get('articleId')
                    }
            return list(unique_refs.values())
        return []
    except: return []

def get_technical_specs(article_id):
    """Récupère les critères (Hauteur, Diamètre...)"""
    url = f"https://{HOST}/api/v1/articles/selection-of-all-specifications-criterias-for-the-article/article-id/{article_id}/lang-id/6/country-filter-id/85"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        return res.json() if res.status_code == 200 else []
    except: return []

# --- 3. BARRE LATÉRALE (Outils de navigation SIV/VIN) ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.subheader("🔗 Liens de Recherche")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)
st.sidebar.markdown('[🔗 PARTSOUQ](https://partsouq.com/)')
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. ANALYSE TECDOC FRANCE"])

# --- TAB 1 : VUES ECLATEES OEM ---
with tab1:
    if vin_input:
        st.subheader(f"🛠️ Identification en cours : `{vin_input.upper()}`")
        c1, c2, c3 = st.columns(3)
        c1.link_button("🚀 Partsouq VIN", f"https://partsouq.com/en/search/all?q={vin_input}")
        c2.link_button("🇯🇵 Amayama", f"https://www.amayama.com/en/search?q={vin_input}")
        c3.link_button("🚘 SIV Auto", "https://www.siv-auto.fr/")
    
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=800, scrolling=True)

# --- TAB 2 : ANALYSE AFTERMARKET ---
with tab2:
    oe_input = st.text_input("📦 Saisir la Référence OE pour analyse Aftermarket", value="1109AY").upper()
    
    if oe_input:
        st.subheader(f"📊 Résultats Aftermarket pour `{oe_input}`")
        
        with st.spinner("Nettoyage et filtrage du catalogue..."):
            items = get_clean_iam(oe_input)
            
            if items:
                premium = [i for i in items if any(p in i['Marque'] for p in PREMIUM_BRANDS)]
                others = [i for i in items if i not in premium]

                st.markdown("### ⭐ Sélection Premium (Unique)")
                if premium:
                    # Correction ici : width='stretch' au lieu de use_container_width=True
                    st.dataframe(
                        pd.DataFrame(premium),
                        column_config={
                            "Aperçu": st.column_config.ImageColumn("Photo", width="small"),
                            "ID": None
                        },
                        hide_index=True,
                        width="stretch" 
                    )
                
                st.divider()
                col_sel, col_act = st.columns([2, 1])
                with col_sel:
                    selected_label = st.selectbox("📏 Choisir une pièce pour voir les dimensions :", 
                                                [f"{x['Marque']} - {x['Référence']}" for x in premium + others[:5]])
                
                with col_act:
                    if st.button("Extraire Dimensions"):
                        all_match = premium + others
                        target = next(i for i in all_match if f"{i['Marque']} - {i['Référence']}" == selected_label)
                        specs = get_technical_specs(target['ID'])
                        if specs:
                            for s in specs:
                                st.write(f"🔹 **{s.get('criteriaDescription')}** : {s.get('criteriaValue')}")
                
                with st.expander("📦 Voir le reste du catalogue (Dédoublonné)"):
                    # Correction ici : width='stretch'
                    st.dataframe(
                        pd.DataFrame(others), 
                        column_config={"Aperçu": st.column_config.ImageColumn()}, 
                        hide_index=True,
                        width="stretch"
                    )
            else:
                st.warning("Aucun équivalent trouvé pour cette référence.")

        st.divider()
        st.caption("Accès directs rapides :")
        cx1, cx2, cx3, cx4 = st.columns(4)
        clean = oe_input.lower().replace(" ", "")
        cx1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean}")
        cx2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean}")
        cx3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean}")
        cx4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean}")
