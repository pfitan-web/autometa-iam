import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide", page_icon="⚙️")

# --- 2. GESTION DU MODE ET DES QUOTAS ---
IS_PUBLIC = st.secrets.get("IS_PUBLIC_VERSION", "true").lower() == "true"
SYSTEM_KEY = st.secrets.get("RAPIDAPI_KEY", "")
PARTSLINK_LINK = st.secrets.get("PARTSLINK_URL", "")

# Limite de démo (2 appels)
DEMO_LIMIT = 2

# Initialisation du compteur de session
if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0

# --- 3. BARRE LATÉRALE (GESTION CLÉ API) ---
st.sidebar.title("⚙️ AutoMeta Expert")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

# Logique de sélection de la clé
st.sidebar.divider()

# Input pour la clé utilisateur
user_key = st.sidebar.text_input(
    "🔑 Votre Clé RapidAPI (Illimité)", 
    type="password", 
    help="Entrez votre propre clé pour débloquer l'accès illimité."
)

# Détermination de la clé active et du statut
if user_key:
    ACTIVE_KEY = user_key
    is_unlimited = True
    st.sidebar.success("✅ Mode Illimité Activé")
else:
    ACTIVE_KEY = SYSTEM_KEY
    is_unlimited = False
    remaining = DEMO_LIMIT - st.session_state.api_calls
    if remaining > 0:
        st.sidebar.info(f"⚡ Mode Démo : {remaining} appels restants")
    else:
        st.sidebar.error("⛔ Quota Démo Épuisé")

# Liens d'aide pour obtenir une clé
with st.sidebar.expander("Comment avoir une clé ?"):
    st.markdown("""
    1. Créez un compte sur **[RapidAPI](https://rapidapi.com/auth/sign-up)**.
    2. Abonnez-vous à l'API **[TecDoc Catalog](https://rapidapi.com/ronhartman/api/tecdoc-catalog)** (Plan Free).
    3. Copiez votre `X-RapidAPI-Key` et collez-la ci-dessus.
    """)

# Liens externes (VIN)
st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown(f'<a href="https://partsouq.com/en/search/all?q={vin_input}" target="_blank">🚀 PARTSOUQ VIN</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

# Mode Privé (Partslink)
if not IS_PUBLIC and PARTSLINK_LINK:
    st.sidebar.divider()
    st.sidebar.markdown(f'[🔐 ACCÈS PARTSLINK24]({PARTSLINK_LINK})')

# --- 4. FONCTIONS API (AVEC CONTRÔLE QUOTA) ---
HOST = "tecdoc-catalog.p.rapidapi.com"
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

@st.cache_data(ttl=600)
def get_clean_iam(oem_ref, api_key):
    """Recherche IAM avec passage de la clé en argument pour éviter les erreurs de cache"""
    clean_ref = oem_ref.replace(" ", "").upper()
    url = f"https://{HOST}/articles-oem/search-by-article-oem-no/lang-id/6/article-oem-no/{clean_ref}"
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": HOST}
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
        elif res.status_code == 403 or res.status_code == 401:
            return "AUTH_ERROR" # Mauvaise clé utilisateur
        return []
    except: return []

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
        # --- LOGIQUE DE BLOCAGE ---
        if not is_unlimited and st.session_state.api_calls >= DEMO_LIMIT:
            st.error(f"⛔ **Limite de démo atteinte ({DEMO_LIMIT}/{DEMO_LIMIT})**")
            st.warning("Pour continuer vos recherches, veuillez saisir votre propre Clé API (Gratuite) dans la barre latérale.")
            st.markdown("👉 **[Créer ma clé RapidAPI maintenant](https://rapidapi.com/ronhartman/api/tecdoc-catalog)**")
        else:
            # Exécution de la recherche
            data = get_clean_iam(oe_input, ACTIVE_KEY)
            
            # Gestion du retour
            if data == "AUTH_ERROR":
                st.error("❌ La clé API saisie est invalide. Veuillez vérifier sur RapidAPI.")
            elif data:
                # Incrémentation du compteur SI c'est une clé démo et que l'appel a réussi
                if not is_unlimited:
                    st.session_state.api_calls += 1
                    # Force le rechargement pour mettre à jour la sidebar
                    st.rerun()

                df = pd.DataFrame(data)
                premium = df[df['is_premium']]
                
                st.markdown(f"### 🏆 Résultats pour `{oe_input}`")
                st.dataframe(premium[["Photo", "Marque", "Référence", "Produit"]], 
                             column_config={"Photo": st.column_config.ImageColumn("Visuel")}, 
                             hide_index=True, width="stretch")
                
                st.divider()
                choice = st.selectbox("📋 Copier une référence :", [f"{x['Marque']} - {x['Ref_Pure']}" for x in data])
                st.code(choice.split(" - ")[-1], language="text")
            else:
                st.warning("Aucun résultat trouvé ou erreur de connexion.")

# --- 6. FOOTER ---
st.divider()
clean_oe = oe_input.replace(" ", "").lower()
cx1, cx2, cx3, cx4 = st.columns(4)
cx1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean_oe}")
cx2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean_oe}")
cx3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean_oe}")
cx4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean_oe}")
