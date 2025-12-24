import streamlit as st
import pandas as pd
from duckduckgo_search import DDGS
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v9.4", layout="wide")

# --- 2. FONCTION DE SCRAPING PUR (SANS IA) ---
def get_clean_web_data(oe_ref):
    results = []
    try:
        with DDGS() as ddgs:
            # On cherche sur les plateformes clés
            query = f"site:distriauto.fr OR site:daparto.fr {oe_ref}"
            search_results = ddgs.text(query, max_results=10)
            
            for r in search_results:
                title = r['title'].upper()
                body = r['body'].upper()
                
                # Extraction basique par mots-clés pour éviter l'IA
                brands = ["PURFLUX", "MANN", "BOSCH", "MAHLE", "VALEO", "HENGST", "FEBI", "UFI"]
                for b in brands:
                    if b in title or b in body:
                        # On tente de trouver une référence proche du nom de la marque
                        results.append({
                            "Marque": b,
                            "Source / Info": r['title'][:60] + "...",
                            "Lien": r['href']
                        })
    except Exception as e:
        st.error(f"Erreur de recherche : {e}")
    return pd.DataFrame(results).drop_duplicates(subset=['Marque'])

# --- 3. BARRE LATÉRALE (Restauration Totale + Liens) ---
st.sidebar.title("⚙️ Paramètres Expertise")

# Identification VIN
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Entrez le VIN...")

# SECTION LIENS EXTERNES
st.sidebar.subheader("🔗 Liens Utiles")
cols = st.sidebar.columns(2)
with cols[0]:
    st.markdown('[SIV AUTO](https://www.siv-auto.fr/)')
    st.markdown('[PARTSOUQ](https://partsouq.com/)')
with cols[1]:
    st.markdown('[PARTSLINK24](https://www.partslink24.com/)')

st.sidebar.divider()

# Input OE
oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE IAM (SCRAPING)"])

with tab1:
    st.markdown(f"### 🛠️ Schémas Constructeurs : `{oe_input.upper()}`")
    if vin_input:
        st.info(f"Analyse pour VIN : **{vin_input.upper()}**")
    # Iframe Tradesoft
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)

with tab2:
    st.markdown(f"### 📋 Données réelles extraites pour `{oe_input.upper()}`")
    st.caption("Cette version n'utilise plus l'IA pour éviter les blocages de quota (429).")
    
    if st.button("🔎 Lancer l'extraction Web", use_container_width=True):
        with st.spinner("Extraction des sources Distriauto / Daparto..."):
            df_results = get_clean_web_data(oe_input)
            
            if not df_results.empty:
                st.success(f"✅ {len(df_results)} sources de confiance trouvées.")
                st.dataframe(df_results, use_container_width=True, hide_index=True)
                
                # Petit bloc d'aide pour l'utilisateur
                st.info("💡 Cliquez sur les liens ci-dessus pour vérifier les dimensions exactes sur les fiches produits.")
            else:
                st.warning("Aucune donnée directe trouvée. Essayez une référence OE plus générique.")
