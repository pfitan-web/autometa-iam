import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM Pro v12.8", layout="wide")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", None)
HOST = "tecdoc-catalog.p.rapidapi.com"

# Configuration IDs validés
LANG_ID = "6"      # Français
COUNTRY_ID = "85"  # France

# Liste des marques Premium à surveiller
PREMIUM_BRANDS = ["PURFLUX", "MANN-FILTER", "KNECHT", "MAHLE", "VALEO", "BOSCH", "HENGST FILTER"]

# --- 2. FONCTIONS API ---

def get_iam_catalog(oem_ref):
    """Recherche OEM avec images"""
    clean_ref = oem_ref.replace(" ", "").upper()
    url = f"https://{HOST}/articles-oem/search-by-article-oem-no/lang-id/{LANG_ID}/article-oem-no/{clean_ref}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        return res.json() if res.status_code == 200 else []
    except: return []

def get_detailed_specs(article_id):
    """Critères techniques via votre curl"""
    url = f"https://{HOST}/api/v1/articles/selection-of-all-specifications-criterias-for-the-article/article-id/{article_id}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": HOST}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        return res.json() if res.status_code == 200 else []
    except: return []

# --- 3. INTERFACE ---
st.sidebar.title("⚙️ Expertise Pro")
oe_input = st.sidebar.text_input("📦 Référence OE", value="1109AY")

tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "🏆 2. CATALOGUE IAM FILTRÉ"])

with tab2:
    if oe_input:
        if not RAPIDAPI_KEY:
            st.error("🔑 Clé API manquante.")
        else:
            with st.spinner("Analyse du catalogue..."):
                all_items = get_iam_catalog(oe_input)
                
                if all_items:
                    # Séparation des marques : Premium vs Autres
                    premium_list = []
                    others_list = []
                    
                    for item in all_items:
                        brand_name = item.get('supplierName', '').upper()
                        # On prépare la ligne
                        row = {
                            "Photo": item.get('s3image'),
                            "Marque": brand_name,
                            "Référence": item.get('articleNo'),
                            "Produit": item.get('articleProductName'),
                            "articleId": item.get('articleId')
                        }
                        
                        if any(p in brand_name for p in PREMIUM_BRANDS):
                            premium_list.append(row)
                        else:
                            others_list.append(row)

                    # --- AFFICHAGE PREMIUM ---
                    st.subheader("⭐ Marques Premium Sélectionnées")
                    if premium_list:
                        df_p = pd.DataFrame(premium_list)
                        st.dataframe(df_p, column_config={"Photo": st.column_config.ImageColumn("Aperçu"), "articleId": None}, hide_index=True, use_container_width=True)
                        
                        # Sélecteur pour voir les dimensions d'une marque précise
                        selected_brand = st.selectbox("🔍 Voir les dimensions techniques de :", [p['Marque'] + " (" + p['Référence'] + ")" for p in premium_list])
                        
                        if st.button("Extraire les dimensions"):
                            # On récupère l'ID correspondant au choix
                            idx = [p['Marque'] + " (" + p['Référence'] + ")" for p in premium_list].index(selected_brand)
                            target_id = premium_list[idx]['articleId']
                            
                            with st.spinner("Lecture des critères..."):
                                specs = get_detailed_specs(target_id)
                                if specs:
                                    st.write(f"📏 **Spécifications pour {selected_brand} :**")
                                    cols = st.columns(3)
                                    for i, s in enumerate(specs[:6]): # Affiche les 6 premiers critères
                                        cols[i%3].metric(label=s.get('criteriaDescription'), value=s.get('criteriaValue'))
                    else:
                        st.info("Aucune marque Premium détectée pour cette référence.")

                    # --- AFFICHAGE AUTRES ---
                    with st.expander("📦 Voir le reste du catalogue (Autres marques)"):
                        if others_list:
                            st.dataframe(pd.DataFrame(others_list), column_config={"Photo": st.column_config.ImageColumn("Aperçu"), "articleId": None}, hide_index=True, use_container_width=True)

        st.divider()
        # Boutons de secours
        c1, c2, c3, c4 = st.columns(4)
        clean = oe_input.lower().replace(" ", "")
        c1.link_button("Distriauto", f"https://www.distriauto.fr/pieces-auto/oem/{clean}")
        c2.link_button("Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean}?ref=fulltext")
        c3.link_button("Oscaro", f"https://www.oscaro.com/fr/search?q={clean}")
        c4.link_button("Autodoc", f"https://www.auto-doc.fr/search?keyword={clean}")
