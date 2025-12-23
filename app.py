import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION & DESIGN
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide")
load_dotenv()

# Style CSS pour l'interface "Workspace"
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 60px; 
        background-color: #f8f9fa; 
        border-radius: 5px 5px 0 0;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1f4e79 !important; 
        color: white !important; 
    }
    thead tr th { background-color: #1f4e79 !important; color: white !important; }
    .main .block-container { padding-top: 1rem; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONFIGURATION IA GEMINI
# Utilise les Secrets de Streamlit Cloud ou le .env local
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Clé API Gemini manquante. Configurez les Secrets.")

def get_ai_expertise(oe_ref, brand, design):
    """Analyse technique par Gemini"""
    if not api_key: return "IA non configurée"
    prompt = f"""
    Expert automobile Aftermarket. Analyse la compatibilité entre la référence constructeur {oe_ref} 
    et la pièce trouvée : {brand} ({design}). 
    S'il s'agit d'une pompe à eau ou d'un turbo VAG, préviens s'il y a un risque de variante (suffixe).
    Réponds en 20 mots max.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Analyse indisponible."

# 3. LE ROBOT SCANNER (VRAIE EXTRACTION)
def scan_distri_auto(oe_ref):
    """Robot qui extrait les vraies données de DistriAuto"""
    clean_ref = oe_ref.replace(".", "").replace(" ", "").upper()
    url = f"https://www.distriauto.fr/pieces-auto/oem/{clean_ref}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Recherche des cartes produits sur le site
            # Note : Les sélecteurs 'product-item' sont à adapter selon la structure exacte
            products = soup.find_all('div', class_='product-item-details') or soup.find_all('div', class_='product-card')
            
            for p in products[:8]: # On prend les 8 premiers résultats
                brand = p.find('span', class_='brand-name').text.strip() if p.find('span', class_='brand-name') else "Inconnue"
                ref_iam = p.find('span', class_='sku').text.strip() if p.find('span', class_='sku') else "N/A"
                designation = p.find('a', class_='product-item-link').text.strip() if p.find('a', class_='product-item-link') else "Pièce Auto"
                
                results.append({
                    "Marque": brand,
                    "Référence IAM": ref_iam,
                    "Désignation": designation
                })
        return results
    except Exception as e:
        return []

# 4. BARRE LATÉRALE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("Station d'Expertise v2.6")

st.sidebar.subheader("🚗 Véhicule")
st.sidebar.link_button("🌐 SIV-Auto (Plaque ⮕ VIN)", "https://siv-auto.fr/", use_container_width=True)
vin_input = st.sidebar.text_input("VIN / Châssis", placeholder="Coller ici...")

st.sidebar.subheader("📦 Pièce")
oe_val = st.sidebar.text_input("Référence OE", placeholder="Ex: 03L121011J")

st.sidebar.divider()
# État de connexion PartsLink24 (via secrets)
if st.secrets.get("PL24_USER"):
    st.sidebar.success("🟢 PartsLink24 : Connecté")
else:
    st.sidebar.warning("🟡 Mode Visiteur")

# 5. INTERFACE PRINCIPALE
tab_oem, tab_iam = st.tabs(["🔍 IDENTIFICATION & VUES OEM", "📊 EXPERTISE IAM & TECDOC"])

with tab_oem:
    st.subheader("Documentation Constructeur")
    col1, col2, col3 = st.columns(3)
    with col1: st.link_button("🚀 PartsLink24", "https://www.partslink24.com/", use_container_width=True)
    with col2: st.link_button("🌍 PartSouq", "https://partsouq.com/", use_container_width=True)
    with col3: st.link_button("📘 CatCar.info", "https://www.catcar.info/", use_container_width=True)
    
    st.divider()
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750, scrolling=True)

with tab_iam:
    st.subheader("Analyse Comparative & Intelligence Artificielle")
    
    if oe_val:
        st.info(f"Cible : **{oe_val.upper()}**")
        
        if st.button("🤖 Lancer le Robot d'Analyse", use_container_width=True):
            with st.spinner("Le robot scanne les catalogues et consulte Gemini..."):
                # On lance le scan réel
                real_data = scan_distri_auto(oe_val)
                
                if real_data:
                    enriched_data = []
                    for item in real_data:
                        # Analyse IA pour chaque ligne trouvée
                        analysis = get_ai_expertise(oe_val, item['Marque'], item['Désignation'])
                        enriched_data.append({
                            "Marque": item['Marque'],
                            "Référence IAM": item['Référence IAM'],
                            "Désignation": item['Désignation'],
                            "Analyse Gemini 2.5 Flash": analysis
                        })
                    
                    st.table(pd.DataFrame(enriched_data))
                else:
                    st.warning("Aucun résultat automatique. Le site bloque peut-être le robot ou la référence est introuvable.")
                    st.write("Vérifiez manuellement ici :")
                    st.link_button("📦 DistriAuto", f"https://www.distriauto.fr/pieces-auto/oem/{oe_val}")

        st.divider()
        st.write("🔍 **Vérifications Manuelles Rapides :**")
        b1, b2 = st.columns(2)
        with b1: st.link_button("📦 DistriAuto (Direct)", f"https://www.distriauto.fr/pieces-auto/oem/{oe_val}", use_container_width=True)
        with b2: st.link_button("🔎 Daparto", f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{oe_val}?ref=fulltext", use_container_width=True)
    else:
        st.warning("Veuillez saisir une référence OE dans la barre latérale.")
