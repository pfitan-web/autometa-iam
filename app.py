import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v11.0", layout="wide")

# Récupération de la clé API (si configurée)
rapid_api_key = st.secrets.get("RAPIDAPI_KEY", None)

# --- 2. FONCTIONS ---

def get_tecdoc_data(oe_ref):
    """Interroge l'API TecDoc via RapidAPI"""
    if not rapid_api_key:
        return None, "Clé API manquante"
    
    url = "https://tecdoc-catalog.p.rapidapi.com/api/v1/articles/search"
    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "tecdoc-catalog.p.rapidapi.com"
    }
    # Paramètres standards pour une recherche OE
    params = {
        "searchQuery": oe_ref,
        "searchType": "oe", # ou "any"
        "country": "FR",
        "lang": "fr"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data, None
        elif response.status_code == 429:
            return None, "Quota RapidAPI dépassé (429)"
        else:
            return None, f"Erreur API: {response.status_code}"
            
    except Exception as e:
        return None, f"Erreur technique: {str(e)}"

def format_tecdoc_results(json_data):
    """Transforme le JSON complexe en tableau simple"""
    results = []
    # La structure dépend de l'API exacte, voici une structure standard TecDoc
    # Il faudra peut-être ajuster selon le retour exact de 'ronhartman'
    try:
        articles = json_data.get('articles', [])
        for art in articles:
            results.append({
                "Marque": art.get('mfrName', 'Inconnu'),
                "Référence": art.get('articleNumber', '-'),
                "Description": art.get('genericArticleName', 'Pièce'),
                "Statut": art.get('articleStatus', '')
            })
    except Exception:
        pass
    return pd.DataFrame(results)

def get_expert_links(oe_ref):
    """Génère les liens de secours"""
    clean_ref = oe_ref.replace(".", "").replace(" ", "").lower()
    return [
        {"Plateforme": "DISTRIAUTO", "URL": f"https://www.distriauto.fr/pieces-auto/oem/{clean_ref}"},
        {"Plateforme": "DAPARTO", "URL": f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean_ref}?ref=fulltext"},
        {"Plateforme": "OSCARO", "URL": f"https://www.oscaro.com/fr/search?q={clean_ref}"},
        {"Plateforme": "AUTODOC", "URL": f"https://www.auto-doc.fr/search?keyword={clean_ref}"}
    ]

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("⚙️ Expertise Pro")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Saisir VIN...")

st.sidebar.subheader("🔗 Liens de Recherche")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)
st.sidebar.markdown('[🔗 PARTSOUQ](https://partsouq.com/)')
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

st.sidebar.divider()
oe_input = st.sidebar.text_input("📦 Référence OE", value="")

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. EXPERTISE HYBRIDE"])

with tab1:
    if vin_input:
        st.subheader(f"🛠️ VIN : `{vin_input.upper()}`")
    elif oe_input:
        st.subheader(f"🛠️ OE : `{oe_input.upper()}`")
    else:
        st.subheader("🛠️ Catalogue OEM")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=800, scrolling=True)

with tab2:
    if oe_input:
        st.subheader(f"📊 Analyse : `{oe_input.upper()}`")
        
        # --- BLOC 1 : API TECDOC (Priorité) ---
        st.markdown("#### ⚡ Résultats API (TecDoc Data)")
        
        if not rapid_api_key:
            st.warning("⚠️ Clé API non configurée dans les Secrets. Affichage des liens uniquement.")
        else:
            with st.spinner("Interrogation TecDoc en cours..."):
                json_data, error_msg = get_tecdoc_data(oe_input)
                
                if error_msg:
                    st.error(f"⚠️ {error_msg}")
                elif json_data:
                    # Debugger : Afficher le JSON brut dans un expander pour ajuster le code si besoin
                    with st.expander("Voir données brutes (JSON)"):
                        st.json(json_data)
                    
                    df_tecdoc = format_tecdoc_results(json_data)
                    if not df_tecdoc.empty:
                        st.dataframe(df_tecdoc, use_container_width=True, hide_index=True)
                    else:
                        st.info("L'API a répondu mais aucune correspondance directe trouvée dans ce format.")
        
        st.divider()

        # --- BLOC 2 : LIENS DE SECOURS (Toujours là) ---
        st.markdown("#### 🌍 Vérification Web (Catalogues)")
        expert_links = get_expert_links(oe_input)
        col1, col2 = st.columns(2)
        
        for i, link in enumerate(expert_links):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                with st.container(border=True):
                    st.write(f"**{link['Plateforme']}**")
                    st.link_button(f"Ouvrir {oe_input.upper()}", link["URL"], use_container_width=True)
    else:
        st.info("Saisissez une référence OE pour lancer l'analyse Hybride.")
