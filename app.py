import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide", page_icon="⚙️")

# --- 2. LOGIQUE D'ENVIRONNEMENT ---
env_type = st.secrets.get("APP_ENVIRONMENT", "PUBLIC").upper().strip()
IS_PRIVATE = (env_type == "PRIVATE_EXPERT")

# Clés
SYSTEM_KEY = st.secrets.get("RAPIDAPI_KEY", "")
PARTSLINK_LINK = st.secrets.get("PARTSLINK_URL", "")

if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("⚙️ AutoMeta-IAM")
if IS_PRIVATE:
    st.sidebar.success("🔐 MODE EXPERT : ILLIMITÉ")
else:
    st.sidebar.info("🌐 MODE PUBLIC : DÉMO")

vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")
user_key = st.sidebar.text_input("🔑 Votre clé RapidAPI (Optionnel)", type="password")

# Détermination de la clé active
ACTIVE_KEY = user_key if user_key else SYSTEM_KEY
is_unlimited = True if (user_key or IS_PRIVATE) else False

if not is_unlimited:
    remaining = 2 - st.session_state.api_calls
    st.sidebar.write(f"⚡ Appels restants : {max(0, remaining)}")

st.sidebar.divider()
st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown(f"🚀 [PARTSOUQ VIN](https://partsouq.com/en/search/all?q={vin_input})")
st.sidebar.markdown("🚘 [SIV AUTO](https://www.siv-auto.fr/)")

if IS_PRIVATE and PARTSLINK_LINK:
    st.sidebar.divider()
    st.sidebar.markdown(f"**[🔐 ACCÈS PARTSLINK24]({PARTSLINK_LINK})**")

# --- 4. FONCTION API AMÉLIORÉE ---
@st.cache_data(ttl=600)
def fetch_tecdoc(oem_ref, api_key):
    # On nettoie la ref : majuscules et pas d'espaces
    clean_ref = "".join(oem_ref.split()).upper()
    url = f"https://tecdoc-catalog.p.rapidapi.com/articles-oem/search-by-article-oem-no/lang-id/6/article-oem-no/{clean_ref}"
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "tecdoc-catalog.p.rapidapi.com"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []

# --- 5. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 VUES OEM", "📊 ANALYSE TECDOC"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700, scrolling=True)

with tab2:
    oe_input = st.text_input("📦 Référence OE Aftermarket", value="1109AY").upper()
    
    if oe_input:
        if not is_unlimited and st.session_state.api_calls >= 2:
            st.error("⛔ Quota démo épuisé.")
        else:
            with st.spinner('Recherche en cours...'):
                raw_data = fetch_tecdoc(oe_input, ACTIVE_KEY)
            
            if raw_data and isinstance(raw_data, list):
                if not is_unlimited:
                    st.session_state.api_calls += 1
                    st.rerun()

                PREMIUM = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]
                processed = []
                seen = set()

                for item in raw_data:
                    ref = item.get('articleNo')
                    if ref and ref not in seen:
                        brand = str(item.get('supplierName', '')).upper()
                        processed.append({
                            "Visuel": item.get('s3image'),
                            "Marque": f"⭐ {brand}" if any(p in brand for p in PREMIUM) else brand,
                            "Référence": ref,
                            "Désignation": item.get('articleProductName', 'N/A')
                        })
                        seen.add(ref)
                
                if processed:
                    df = pd.DataFrame(processed)
                    st.dataframe(
                        df, 
                        column_config={"Visuel": st.column_config.ImageColumn()},
                        hide_index=True, 
                        width="stretch"
                    )
                    
                    st.divider()
                    ref_list = [f"{row['Marque']} : {row['Référence']}" for _, row in df.iterrows()]
                    choix = st.selectbox("📋 Copier une référence :", ref_list)
                    st.code(choix.split(" : ")[-1], language="text")
                else:
                    st.info("Aucune correspondance trouvée dans la base TecDoc.")
            else:
                st.warning("L'API n'a retourné aucun résultat pour cette référence.")
