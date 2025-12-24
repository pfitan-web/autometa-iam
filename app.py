import streamlit as st
import pandas as pd
from ddgs import DDGS # Utilisation du nouveau nom du paquet
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v9.5", layout="wide")

# --- 2. FONCTION DE RECHERCHE (Nouveau format DDGS) ---
def get_clean_web_data(oe_ref):
    results = []
    try:
        with DDGS() as ddgs:
            # On cible les plateformes clés avec la nouvelle syntaxe
            query = f"site:distriauto.fr OR site:daparto.fr {oe_ref}"
            search_results = ddgs.text(query, max_results=10)
            
            for r in search_results:
                title = r.get('title', '').upper()
                body = r.get('body', '').upper()
                
                brands = ["PURFLUX", "MANN", "BOSCH", "MAHLE", "VALEO", "HENGST", "FEBI", "UFI"]
                for b in brands:
                    if b in title or b in body:
                        results.append({
                            "Marque": b,
                            "Source / Info": r.get('title', '')[:60] + "...",
                            "Lien": r.get('href', '#')
                        })
    except Exception as e:
        st.error(f"Erreur de recherche : {e}")
    return pd.DataFrame(results).drop_duplicates(subset=['Marque'])

# --- 3. BARRE LATÉRALE (Restauration avec liens intelligents) ---
st.sidebar.title("⚙️ Paramètres Expertise")

vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Entrez le VIN...")

st.sidebar.subheader("🔗 Liens Utiles")
# Liens dynamiques : ils incluent déjà votre référence OE pour vous faire gagner du temps
st.sidebar.markdown(f'[🔗 SIV AUTO](https://www.siv-auto.fr/)')
st.sidebar.markdown(f'[🔗 PARTSOUQ ({oe_input if "oe_input" in locals() else ""})](https://partsouq.com/en/search/all?q={oe_input if "oe_input" in locals() else ""})')
st.sidebar.markdown(f'[🔗 PARTSLINK24](https://www.partslink24.com/)')

st.sidebar.divider()

oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE IAM (VÉRIFIÉ)"])

with tab1:
    st.markdown(f"### 🛠️ Schémas Constructeurs : `{oe_input.upper()}`")
    if vin_input:
        st.info(f"Analyse pour VIN : **{vin_input.upper()}**")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)

with tab2:
    st.markdown(f"### 📋 Données réelles pour `{oe_input.upper()}`")
    
    if st.button("🔎 Lancer l'extraction Web", use_container_width=True):
        with st.spinner("Extraction en cours (Zéro IA / Zéro 429)..."):
            df_results = get_clean_web_data(oe_input)
            
            if not df_results.empty:
                st.success(f"✅ {len(df_results)} sources de confiance trouvées.")
                # Affichage des liens cliquables dans le tableau
                st.dataframe(
                    df_results, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Lien": st.column_config.LinkColumn("Lien vers Fiche")
                    }
                )
            else:
                st.warning("Aucune donnée directe trouvée.")
