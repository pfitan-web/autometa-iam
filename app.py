import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide", page_icon="⚙️")

# --- 2. DÉTECTION DU MODE (INJECTION MALIGNE) ---
# Si le secret IS_PUBLIC_VERSION n'existe pas ou est à True, on masque le privé.
IS_PUBLIC = st.secrets.get("IS_PUBLIC_VERSION", "true").lower() == "true"
PARTSLINK_LINK = st.secrets.get("PARTSLINK_URL", "") # Ne sera rempli que sur votre app privée

# Accès API
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", "")
HOST = "tecdoc-catalog.p.rapidapi.com"
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

# --- 3. FONCTIONS API ---
@st.cache_data(ttl=600)
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
                    is_p = any(p in brand for p in PREMIUM_BRANDS)
                    unique_refs[ref_no] = {
                        "Photo": item.get('s3image'),
                        "Marque": f"⭐ {brand}" if is_p else brand,
                        "Référence": f"{ref_no} 📋",
                        "Ref_Pure": ref_no,
                        "Produit": item.get('articleProductName'),
                        "is_premium": is_p
                    }
            return list(unique_refs.values())
        return []
    except: return []

# --- 4. BARRE LATÉRALE (DYNAMIQUE) ---
st.sidebar.title("⚙️ AutoMeta Expert")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown(f'<a href="https://partsouq.com/en/search/all?q={vin_input}" target="_blank">🚀 PARTSOUQ VIN</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

# L'INJECTION MALIGNE : Partslink n'apparaît que si le secret est présent et IS_PUBLIC est False
if not IS_PUBLIC and PARTSLINK_LINK:
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Espace Expert")
    st.sidebar.markdown(f'[🔗 ACCÈS PARTSLINK24]({PARTSLINK_LINK})')
    st.sidebar.info("✅ Mode Privé Déverrouillé")

# --- 5. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. ANALYSE TECDOC"])

with tab1:
    if vin_input:
        c1, c2 = st.columns(2)
        c1.link_button("🚀 Partsouq", f"https://partsouq.com/en/search/all?q={vin_input}")
        c2.link_button("🚘 SIV Auto", "https://www.siv-auto.fr/")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700, scrolling=True)

with tab2:
    oe_input = st.text_input("📦 Référence OE Aftermarket", value="1109AY").upper()
    if oe_input:
        data = get_clean_iam(oe_input)
        if data:
            df = pd.DataFrame(data)
            premium = df[df['is_premium']]
            st.markdown("### 🏆 Top Marques Sélectionnées")
            st.dataframe(premium[["Photo", "Marque", "Référence", "Produit"]], 
                         column_config={"Photo": st.column_config.ImageColumn("Visuel")}, 
                         hide_index=True, width="stretch")
            
            st.divider()
            choice = st.selectbox("📋 Copier une référence :", [f"{x['Marque']} - {x['Ref_Pure']}" for x in data])
            st.code(choice.split(" - ")[-1], language="text")

# --- 6. FOOTER ---
st.divider()
clean_oe = oe_input.replace(" ", "").lower()
cx1, cx2, cx3, cx4 = st.columns(4)
cx1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean_oe}")
cx2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean_oe}")
cx3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean_oe}")
cx4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean_oe}")
