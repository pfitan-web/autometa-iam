import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide", page_icon="⚙️")

# --- 2. GESTION DU MODE PUBLIC / PRIVÉ (STRATÉGIQUE) ---
# Si "PUBLIC_MODE" est mis à "true" dans les Secrets Streamlit, le lien Partslink est masqué.
IS_PUBLIC = st.secrets.get("PUBLIC_MODE", "false").lower() == "true"

# --- 3. CONFIGURATION API & CONSTANTES ---
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", "")
HOST = "tecdoc-catalog.p.rapidapi.com"
LANG_ID = "6"
COUNTRY_ID = "85"

PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

# --- 4. FONCTIONS API ---

@st.cache_data(ttl=600)
def get_clean_iam(oem_ref):
    """Recherche Aftermarket dédoublonnée"""
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
                        "Référence": f"{ref_no} 📋",
                        "Ref_Pure": ref_no,
                        "Produit": item.get('articleProductName'),
                        "articleId": item.get('articleId'),
                        "is_premium": is_p
                    }
            return list(unique_refs.values())
        return []
    except: return []

# --- 5. BARRE LATÉRALE ---
st.sidebar.title("⚙️ Expertise Auto")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.subheader("🔗 Liens Directs")
# Lien Partsouq dynamique
st.sidebar.markdown(f'<a href="https://partsouq.com/en/search/all?q={vin_input}" target="_blank">🚀 PARTSOUQ VIN</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

# --- LOGIQUE DE MASQUAGE STRATÉGIQUE ---
if not IS_PUBLIC:
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Accès Expert")
    st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')
    st.sidebar.caption("Mode Privé Activé")

# --- 6. INTERFACE PRINCIPALE ---
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

            st.markdown("### 🏆 Sélection Marques Premium")
            st.dataframe(
                premium[["Photo", "Marque", "Référence", "Produit"]], 
                column_config={"Photo": st.column_config.ImageColumn("Visuel")}, 
                hide_index=True, width="stretch"
            )

            st.divider()
            st.subheader("📋 Copie Rapide")
            
            choice = st.selectbox("Référence pour copie :", 
                                [f"{x['Marque']} - {x['Ref_Pure']}" for x in data],
                                key="copy_selector")
            
            ref_to_copy = choice.split(" - ")[-1]
            st.code(ref_to_copy, language="text") 

            with st.expander("📦 Voir le reste du catalogue (Autres marques)"):
                st.dataframe(others[["Photo", "Marque", "Référence", "Produit"]], 
                             column_config={"Photo": st.column_config.ImageColumn()}, 
                             hide_index=True, width="stretch")

# --- 7. FOOTER ---
st.divider()
clean = oe_input.lower().replace(" ", "")
cx1, cx2, cx3, cx4 = st.columns(4)
cx1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean}")
cx2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean}")
cx3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean}")
cx4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean}")
