import streamlit as st
import pandas as pd
from duckduckgo_search import DDGS
from google import genai
import io

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="AutoMeta-IAM Pro v9.3", layout="wide")
api_key = st.secrets.get("GEMINI_API_KEY")

# --- 2. FONCTIONS DE RECHERCHE ---
def get_verified_data(oe_ref):
    search_context = ""
    try:
        with DDGS() as ddgs:
            # Ciblage de l'URL spécifique identifiée : https://www.distriauto.fr/pieces-auto/oem/
            query = f"site:distriauto.fr/pieces-auto/oem/ {oe_ref}"
            results = ddgs.text(query, max_results=10)
            for r in results:
                search_context += f"\nSource: {r['title']} | Contenu: {r['body']}"
    except Exception:
        pass
    return search_context

# --- 3. BARRE LATÉRALE (Restauration Complète) ---
st.sidebar.title("⚙️ Paramètres Expertise")

# Identification VIN
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Entrez le VIN...")

# LIEN SIV AUTO (Correction du paramètre TypeError)
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 Accès SIV AUTO</a>', unsafe_allow_html=True)
st.sidebar.divider()

# Input OE et Filtres
oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")
brand_filter = st.sidebar.multiselect(
    "🛡️ Marques Premium :",
    ["PURFLUX", "MANN-FILTER", "BOSCH", "MAHLE", "VALEO", "HENGST", "FEBI", "UFI"],
    default=["PURFLUX", "MANN-FILTER", "BOSCH"]
)

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE IAM VÉRIFIÉ"])

with tab1:
    st.markdown(f"### 🛠️ Schémas Constructeurs : `{oe_input.upper()}`")
    if vin_input:
        st.info(f"Analyse pour VIN : **{vin_input.upper()}**")
    # Iframe Tradesoft (Maintenue)
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)

with tab2:
    st.markdown(f"### 📋 Correspondances Aftermarket (Source: Distriauto/Daparto)")
    
    if st.button("🔥 Lancer l'Expertise Massive", use_container_width=True):
        if not api_key:
            st.error("Clé API Gemini manquante. Veuillez configurer les Secrets.")
        else:
            with st.spinner("Recherche en direct sur Distriauto..."):
                # Extraction web réelle (Anti-hallucination)
                context = get_verified_data(oe_input)
                
                # Structuration via Gemini 2.0 (Le seul stable)
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Tu es un expert en pièces détachées. Voici les données sources trouvées :
                {context}
                
                TÂCHE :
                1. Liste les correspondances réelles pour l'OE {oe_input}.
                2. Garde uniquement les marques parmi : {', '.join(brand_filter)}.
                3. Extrais les caractéristiques techniques (Hauteur, Diamètre, etc.) SEULEMENT si présentes dans le texte.
                
                Format de sortie : Tableau Markdown (Marque | Référence | Caractéristiques)
                """
                
                try:
                    # Utilisation du modèle fonctionnel sans 404
                    response = client.models.generate_content(model="gemini-2.0-flash-exp", contents=prompt)
                    
                    if response.text:
                        st.markdown(response.text)
                        
                        # Export CSV
                        st.divider()
                        st.download_button(
                            label="📥 Télécharger les résultats",
                            data=response.text.encode('utf-8'),
                            file_name=f"Expertise_{oe_input}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"Erreur d'analyse : {e}")
