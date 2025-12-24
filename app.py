import streamlit as st
import pandas as pd
from duckduckgo_search import DDGS
from google import genai
import io

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="AutoMeta-IAM Pro v9.2", layout="wide")
api_key = st.secrets.get("GEMINI_API_KEY")

# --- 2. FONCTIONS DE RECHERCHE & ANALYSE ---
def get_verified_data(oe_ref):
    search_context = ""
    with DDGS() as ddgs:
        # Ciblage spécifique de l'URL OEM Distriauto
        query = f"site:distriauto.fr/pieces-auto/oem/ {oe_ref}"
        results = ddgs.text(query, max_results=10)
        for r in results:
            search_context += f"\nSource: {r['title']} | Contenu: {r['body']}"
    return search_context

# --- 3. BARRE LATÉRALE (Inputs & Paramètres) ---
st.sidebar.title("⚙️ Paramètres Expertise")

# Restauration des inputs VIN et SIV
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Entrez le VIN...")
st.sidebar.markdown("[🔗 Accès SIV AUTO](https://www.siv-auto.fr/)", unsafe_allow_stdio=True)
st.sidebar.divider()

# Input OE et Filtres
oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")
brand_filter = st.sidebar.multiselect(
    "🛡️ Marques Premium :",
    ["PURFLUX", "MANN-FILTER", "BOSCH", "MAHLE", "VALEO", "HENGST", "FEBI", "UFI"],
    default=["PURFLUX", "MANN-FILTER", "BOSCH"]
)

# --- 4. INTERFACE PRINCIPALE (Onglets) ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE IAM VÉRIFIÉ"])

with tab1:
    st.markdown(f"### 🛠️ Schémas Constructeurs : `{oe_input}`")
    if vin_input:
        st.caption(f"Analyse pour VIN : {vin_input}")
    # Restauration de l'iframe Tradesoft
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)

with tab2:
    st.markdown(f"### 📋 Correspondances Aftermarket (Source: Distriauto/Daparto)")
    
    if st.button("🔥 Lancer l'Expertise Massive", use_container_width=True):
        if not api_key:
            st.error("Clé API Gemini manquante dans les Secrets.")
        else:
            with st.spinner("Recherche des données réelles et filtrage premium..."):
                # Extraction web réelle (Anti-hallucination)
                context = get_verified_data(oe_input)
                
                if len(context) < 30:
                    st.warning("⚠️ Données web insuffisantes pour garantir l'exactitude.")
                
                # Structuration via Gemini 2.0 (Le seul stable sur votre projet)
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Tu es un extracteur de données Aftermarket. 
                Données sources : {context}
                
                MISSION :
                1. Liste les correspondances réelles pour l'OE {oe_input}.
                2. Filtre strictement pour garder ces marques : {', '.join(brand_filter)}.
                3. Extrais les caractéristiques techniques (Hauteur, Diamètre, Filetage) SI ELLES SONT DANS LE TEXTE.
                4. SI UNE INFO N'EST PAS DANS LE TEXTE, NE L'INVENTE PAS.
                
                Format de sortie : TABLEAU MARKDOWN (Marque | Référence | Caractéristiques)
                """
                
                try:
                    response = client.models.generate_content(model="gemini-2.0-flash-exp", contents=prompt)
                    
                    if response.text:
                        st.markdown(response.text)
                        
                        # Génération du fichier Excel pour téléchargement
                        # On simule la création d'un dataframe pour l'export
                        st.divider()
                        buffer = io.BytesIO()
                        # Note: Pour un export parfait, on pourrait parser la réponse MD en DataFrame ici
                        st.download_button(
                            label="📥 Télécharger le catalogue (Excel/CSV)",
                            data=response.text.encode('utf-8'),
                            file_name=f"Expertise_{oe_input}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"Erreur : {e}")
