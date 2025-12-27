import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide", page_icon="⚙️")

# --- 2. LOGIQUE DE DÉTECTION SÉCURISÉE (FORCE DÉMO SI INCONNU) ---
# On utilise une clé différente "APP_ENVIRONMENT" pour forcer la séparation
env_type = st.secrets.get("APP_ENVIRONMENT", "PUBLIC").upper().strip()

if env_type == "PRIVATE_EXPERT":
    IS_PRIVATE = True
    st.sidebar.success("🔐 MODE EXPERT : ILLIMITÉ")
else:
    IS_PRIVATE = False
    st.sidebar.info("🌐 MODE PUBLIC : DÉMO (2 APPELS)")

# Récupération des clés
SYSTEM_KEY = st.secrets.get("RAPIDAPI_KEY", "")
PARTSLINK_LINK = st.secrets.get("PARTSLINK_URL", "")

# Initialisation du quota
if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("⚙️ AutoMeta-IAM")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.divider()
# Champ pour que les visiteurs mettent leur propre clé
user_key = st.sidebar.text_input("🔑 Votre clé RapidAPI (Optionnel)", type="password", help="Pour débloquer l'illimité en mode public.")

# Détermination de la clé à utiliser
if user_key:
    ACTIVE_KEY = user_key
    is_unlimited = True
    st.sidebar.success("✅ Clé personnelle active")
elif IS_PRIVATE:
    ACTIVE_KEY = SYSTEM_KEY
    is_unlimited = True
else:
    ACTIVE_KEY = SYSTEM_KEY
    is_unlimited = False
    remaining = 2 - st.session_state.api_calls
    if remaining > 0:
        st.sidebar.write(f"⚡ Appels restants : {remaining}")
    else:
        st.sidebar.error("⛔ Quota démo épuisé")

# Liens Utiles
st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown(f"🚀 [PARTSOUQ VIN](https://partsouq.com/en/search/all?q={vin_input})")
st.sidebar.markdown("🚘 [SIV AUTO](https://www.siv-auto.fr/)")

# Partslink uniquement si EXPERT
if IS_PRIVATE and PARTSLINK_LINK:
    st.sidebar.divider()
    st.sidebar.markdown(f"**[🔐 ACCÈS PARTSLINK24]({PARTSLINK_LINK})**")

# --- 4. FONCTION API ---
@st.cache_data(ttl=600)
def fetch_tecdoc(oem_ref, api_key):
    url = f"https://tecdoc-catalog.p.rapidapi.com/articles-oem/search-by-article-oem-no/lang-id/6/article-oem-no/{oem_ref.strip()}"
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "tecdoc-catalog.p.rapidapi.com"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        return res.json() if res.status_code == 200 else []
    except:
        return []

# --- 5. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 VUES ÉCLATÉES OEM", "📊 ANALYSE TECDOC"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700, scrolling=True)

with tab2:
    oe_input = st.text_input("📦 Référence OE Aftermarket", value="1109AY").upper()
    
    if oe_input:
        # Vérification du quota pour le mode public
        if not is_unlimited and st.session_state.api_calls >= 2:
            st.error("⛔ Limite de démo atteinte (2/2).")
            st.warning("Insérez votre clé API dans la barre latérale pour continuer.")
        else:
            data = fetch_tecdoc(oe_input, ACTIVE_KEY)
            
            if data:
                # On compte l'appel si on est en démo
                if not is_unlimited:
                    st.session_state.api_calls += 1
                    st.rerun()

                # Traitement des données
                PREMIUM = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]
                processed = []
                seen = set()
                for item in data:
                    ref = item.get('articleNo')
                    if ref not in seen:
                        brand = item.get('supplierName', '').upper()
                        processed.append({
                            "Photo": item.get('s3image'),
                            "Marque": f"⭐ {brand}" if any(p in brand for p in PREMIUM) else brand,
                            "Référence": f"{ref} 📋",
                            "Ref_Pure": ref,
                            "Produit": item.get('articleProductName')
                        })
                        seen.add(ref)
                
                st.dataframe(pd.DataFrame(processed), 
                             column_config={"Photo": st.column_config.ImageColumn("Visuel")}, 
                             hide_index=True, width="stretch")
            else:
                st.info("Aucun résultat Aftermarket trouvé.")
