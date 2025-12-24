import streamlit as st
import pandas as pd
from ddgs import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v9.6", layout="wide")

# --- 2. FONCTION DE RECHERCHE AMÉLIORÉE (Zéro IA) ---
def get_clean_web_data(oe_ref):
    results = []
    # Nettoyage de la référence (ex: 1109.AY -> 1109AY)
    clean_ref = oe_ref.replace(".", "").replace(" ", "").upper()
    
    try:
        # Variantes de recherche pour maximiser les chances de résultats
        queries = [
            f"site:distriauto.fr {clean_ref}",
            f"site:daparto.fr {clean_ref}",
            f"{clean_ref} correspondance filtre"
        ]
        
        with DDGS(timeout=20) as ddgs:
            for q in queries:
                search_results = ddgs.text(q, max_results=5)
                if search_results:
                    for r in search_results:
                        title = r.get('title', '').upper()
                        body = r.get('body', '').upper()
                        
                        # Liste des marques Premium
                        brands = ["PURFLUX", "MANN", "BOSCH", "MAHLE", "VALEO", "HENGST", "FEBI", "UFI", "MECAFILTER"]
                        for b in brands:
                            if b in title or b in body:
                                results.append({
                                    "Marque": b,
                                    "Source / Info": r.get('title', '')[:70],
                                    "Lien": r.get('href', '#')
                                })
                time.sleep(0.5) 
                
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        
    return pd.DataFrame(results).drop_duplicates(subset=['Marque'])

# --- 3. BARRE LATÉRALE (Intégrité Totale) ---
st.sidebar.title("⚙️ Paramètres Expertise")
vin_input = st.sidebar.text_input("🔍 Identification VIN", placeholder="Entrez le VIN...")

st.sidebar.subheader("🔗 Liens Utiles")
st.sidebar.markdown('<a href="https://www.siv-auto.fr/" target="_blank">🔗 SIV AUTO</a>', unsafe_allow_html=True)

# Input OE pour que Partsouq soit dynamique
oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")

st.sidebar.markdown(f'[🔗 PARTSOUQ ({oe_input})](https://partsouq.com/en/search/all?q={oe_input})')
st.sidebar.markdown('[🔗 PARTSLINK24](https://www.partslink24.com/)')

st.sidebar.divider()

# --- 4. INTERFACE PRINCIPALE ---
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. CATALOGUE IAM (RÉSULTATS)"])

with tab1:
    st.markdown(f"### 🛠️ Schémas Constructeurs : `{oe_input.upper()}`")
    if vin_input:
        st.info(f"Analyse pour VIN : **{vin_input.upper()}**")
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)

with tab2:
    st.markdown(f"### 📋 Analyse Aftermarket pour `{oe_input.upper()}`")
    
    if st.button("🔎 Lancer l'extraction des données", use_container_width=True):
        with st.spinner("Interrogation des catalogues..."):
            df_results = get_clean_web_data(oe_input)
            
            if not df_results.empty:
                st.success(f"✅ {len(df_results)} correspondances trouvées.")
                st.dataframe(
                    df_results, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={"Lien": st.column_config.LinkColumn("Lien vers Fiche")}
                )
            else:
                st.error("❌ Aucun résultat trouvé dans les catalogues indexés.")
                st.info("💡 Utilisez les liens directs (Partsouq/SIV) à gauche pour une vérification manuelle.")
