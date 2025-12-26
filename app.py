import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v13.0", layout="wide")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", None)
HOST = "tecdoc-catalog.p.rapidapi.com"

# Marques prioritaires
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST", "FEBI"]

# --- 2. FONCTIONS ---

def get_clean_iam(oem_ref):
    """Recherche IAM avec dédoublonnage strict sur articleNo"""
    clean_ref = oem_ref.replace(" ", "").upper()
    url = f"https://{HOST}/articles-oem/search-by-article-oem-no/lang-id/6/article-oem-no/{clean_ref}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            unique_refs = {}
            for item in res.json():
                ref_no = item.get('articleNo')
                # On ne garde que la 1ère occurrence pour éviter les doublons
                if ref_no not in unique_refs:
                    unique_refs[ref_no] = {
                        "Aperçu": item.get('s3image'),
                        "Marque": item.get('supplierName', '').upper(),
                        "Référence": ref_no,
                        "Produit": item.get('articleProductName'),
                        "ID": item.get('articleId')
                    }
            return list(unique_refs.values())
        return []
    except: return []

# --- 3. INTERFACE ---
st.sidebar.title("⚙️ Expertise Auto")
oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY").upper()

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "🏆 2. CATALOGUE IAM NETTOYÉ"])

# --- TAB 1 : VUES ECLATEES (Restauration) ---
with tab1:
    st.subheader(f"🌐 Schémas Constructeurs : `{oe_input}`")
    c1, c2, c3 = st.columns(3)
    # Liens basés sur les snippets précédents
    c1.link_button("🚀 Partsouq (Mondial)", f"https://partsouq.com/en/search/all?q={oe_input}")
    c2.link_button("🇯🇵 Amayama (Japon/Euro)", f"https://www.amayama.com/en/search?q={oe_input}")
    c3.link_button("🇷🇺 SSG.asia", f"https://www.ssg.asia/search/?search={oe_input}")
    
    st.info("💡 Ces liens ouvrent directement la vue éclatée si la pièce est encore référencée chez le constructeur.")

# --- TAB 2 : CATALOGUE IAM ---
with tab2:
    if oe_input:
        with st.spinner("Nettoyage du catalogue..."):
            items = get_clean_iam(oe_input)
            
            if items:
                # Filtrage Premium vs Reste
                premium = [i for i in items if any(p in i['Marque'] for p in PREMIUM_BRANDS)]
                others = [i for i in items if i not in premium]

                # Affichage Premium
                st.markdown("### ⭐ Marques Premium (Sans doublons)")
                if premium:
                    st.dataframe(
                        pd.DataFrame(premium),
                        column_config={
                            "Aperçu": st.column_config.ImageColumn("Image", width="small"),
                            "ID": None
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                
                # Sélecteur technique
                st.divider()
                selected = st.selectbox("⚖️ Sélectionner pour comparer les dimensions :", 
                                      [f"{x['Marque']} - {x['Référence']}" for x in premium + others[:10]])
                
                if st.button("Afficher la fiche technique"):
                    st.write(f"Analyse des critères pour `{selected}`...")
                    # Ici l'appel GET Article Criteria

                # Reste du catalogue
                with st.expander("📦 Reste du catalogue (Marques secondaires)"):
                    st.dataframe(pd.DataFrame(others), column_config={"Aperçu": st.column_config.ImageColumn(), "ID": None}, hide_index=True)
            else:
                st.warning("Aucune donnée Aftermarket trouvée.")
