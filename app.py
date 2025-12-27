import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v16.1", layout="wide", page_icon="⚙️")

# --- 2. GESTION DU MODE ET DES SECRETS ---
# IS_PUBLIC est True par défaut si non spécifié dans les secrets
IS_PUBLIC = st.secrets.get("IS_PUBLIC_VERSION", "true").lower() == "true"
SYSTEM_KEY = st.secrets.get("RAPIDAPI_KEY", "")
PARTSLINK_LINK = st.secrets.get("PARTSLINK_URL", "")

# Initialisation du compteur de session pour le mode démo
DEMO_LIMIT = 2
if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0

# --- 3. BARRE LATÉRALE (LOGIQUE DE CLÉ) ---
st.sidebar.title("⚙️ AutoMeta Expert")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.divider()
user_key = st.sidebar.text_input("🔑 Votre Clé RapidAPI (Visiteurs)", type="password")

# --- LOGIQUE DE DÉVERROUILLAGE ---
ACTIVE_KEY = ""
is_unlimited = False

if user_key:
    # Cas 1 : Clé fournie manuellement (visiteur ou expert)
    ACTIVE_KEY = user_key
    is_unlimited = True
    st.sidebar.success("✅ Mode Illimité (Clé Manuelle)")
elif not IS_PUBLIC:
    # Cas 2 : VERSION PRIVÉE -> Illimité avec la SYSTEM_KEY
    ACTIVE_KEY = SYSTEM_KEY
    is_unlimited = True
    st.sidebar.success("🔐 Mode Expert (Illimité)")
else:
    # Cas 3 : VERSION PUBLIQUE -> Mode Démo
    ACTIVE_KEY = SYSTEM_KEY
    is_unlimited = False
    remaining = DEMO_LIMIT - st.session_state.api_calls
    if remaining > 0:
        st.sidebar.info(f"⚡ Mode Démo : {remaining} appels restants")
    else:
        st.sidebar.error("⛔ Quota Démo Épuisé")

# Aide pour obtenir une clé (uniquement en mode public bridé)
if IS_PUBLIC and not is_unlimited:
    with st.sidebar.expander("Comment avoir une clé ?"):
        st.markdown("1. Créez un compte sur [RapidAPI](https://rapidapi.com/).\n2. Abonnez-vous à l'API [TecDoc](https://rapidapi.com/ronhartman/api/tecdoc-catalog).\n3. Collez votre clé ci-dessus.")

st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown(f'<a href="https://partsouq.com/en/search/all?q={vin_input}" target="_blank">🚀 PARTSOUQ VIN</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

if not IS_PUBLIC and PARTSLINK_LINK:
    st.sidebar.divider()
    st.sidebar.markdown(f'[🔐 ACCÈS PARTSLINK24]({PARTSLINK_LINK})')

# --- 4. FONCTIONS API ---
HOST = "tecdoc-catalog.p.rapidapi.com"
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

@st.cache_data(ttl=600)
def get_clean_iam(oem_ref, api_key):
    clean_ref = oem_ref.replace(" ", "").upper()
    url = f"https://{HOST}/articles-oem/search-by-article-oem-no/lang-id/6/article-oem-no/{clean_ref}"
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        return res.json() if res.status_code == 200 else []
    except: return []

# --- 5. INTERFACE ---
tab1, tab2 = st.tabs(["🔍 VUES ÉCLATÉES OEM", "📊 ANALYSE TECDOC"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700, scrolling=True)

with tab2:
    oe_input = st.text_input("📦 Référence OE Aftermarket", value="1109AY").upper()
    
    if oe_input:
        if not is_unlimited and st.session_state.api_calls >= DEMO_LIMIT:
            st.error(f"⛔ Limite de démo atteinte ({DEMO_LIMIT}/{DEMO_LIMIT})")
            st.warning("Veuillez saisir votre propre clé dans la barre latérale pour continuer.")
        else:
            raw_data = get_clean_iam(oe_input, ACTIVE_KEY)
            if raw_data:
                # Incrémentation si mode démo uniquement
                if not is_unlimited:
                    st.session_state.api_calls += 1
                    st.rerun()

                # Traitement et affichage
                unique_refs = {}
                for item in raw_data:
                    ref = item.get('articleNo')
                    if ref not in unique_refs:
                        brand = item.get('supplierName', '').upper()
                        unique_refs[ref] = {
                            "Photo": item.get('s3image'),
                            "Marque": f"⭐ {brand}" if any(p in brand for p in PREMIUM_BRANDS) else brand,
                            "Référence": f"{ref} 📋",
                            "Produit": item.get('articleProductName')
                        }
                
                st.dataframe(pd.DataFrame(list(unique_refs.values())), 
                             column_config={"Photo": st.column_config.ImageColumn()}, 
                             hide_index=True, width="stretch")
