import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v12.1", layout="wide")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", None)
HOST = "tecdoc-catalog.p.rapidapi.com"

# --- 2. FONCTIONS API (Basées sur le repo Ron Hartman) ---

def fetch_tecdoc(endpoint, params):
    """Fonction générique pour interroger l'API"""
    url = f"https://{HOST}{endpoint}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": HOST
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            return response.json(), None
        return None, f"Erreur {response.status_code}: {response.text}"
    except Exception as e:
        return None, str(e)

# --- 3. LOGIQUE D'ANALYSE ---

def analyze_oem_reference(oem_no):
    """Workflow complet : Cherche les équivalents IAM"""
    # Étape 1 : Recherche des articles liés à l'OEM
    # Selon le repo, l'endpoint de recherche par numéro est souvent /articles/search
    search_params = {
        "searchQuery": oem_no,
        "searchType": "oe",
        "lang": "fr",
        "country": "FR"
    }
    
    # Correction de l'endpoint d'après les standards du repo
    data, error = fetch_tecdoc("/articles/search", search_params)
    return data, error

# --- 4. INTERFACE ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)
st.sidebar.markdown('[🔗 PARTSOUQ](https://partsouq.com/)')
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

st.sidebar.divider()
oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. ANALYSE TECDOC"])

with tab1:
    # On garde l'Iframe pour la recherche visuelle
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=800, scrolling=True)

with tab2:
    if oe_input:
        st.subheader(f"📊 Résultats TecDoc pour `{oe_input.upper()}`")
        
        if not RAPIDAPI_KEY:
            st.error("🔑 Clé API manquante dans les Secrets Streamlit.")
        else:
            with st.spinner("Interrogation de la base TecDoc..."):
                res, err = analyze_oem_reference(oe_input)
                
                if err:
                    st.error(f"Erreur d'appel API : {err}")
                    st.info("Note : Vérifiez si l'endpoint dans le code correspond à votre abonnement RapidAPI.")
                elif res:
                    # Le repo Ron Hartman renvoie souvent une liste sous 'articles' ou directement une liste
                    articles = res.get('articles', []) if isinstance(res, dict) else res
                    
                    if articles and len(articles) > 0:
                        df_data = []
                        for art in articles:
                            df_data.append({
                                "Marque": art.get('brandName', art.get('mfrName', 'N/A')),
                                "Référence": art.get('articleNumber', 'N/A'),
                                "Désignation": art.get('genericArticleName', 'N/A'),
                                "ID Article": art.get('articleId', 'N/A')
                            })
                        
                        st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
                        
                        # DEBUG JSON pour voir les specs disponibles sans refaire d'appel
                        with st.expander("🔍 Voir détails techniques bruts (JSON)"):
                            st.json(res)
                    else:
                        st.warning("Aucune correspondance trouvée dans TecDoc.")
        
        # Rappel des liens directs en bas pour la sécurité
        st.divider()
        st.caption("Sécurité : Accès directs aux catalogues web")
        c1, c2, c3 = st.columns(3)
        clean = oe_input.lower().replace(" ", "")
        c1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean}")
        c2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean}?ref=fulltext")
        c3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean}")
