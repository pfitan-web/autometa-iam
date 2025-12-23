import streamlit as st
import pandas as pd
import cloudscraper # Installation : pip install cloudscraper
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro | Stealth Mode", layout="wide")
load_dotenv()

# 2. IA GEMINI (Expertise technique)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# LISTE TOP MARQUES OEM
PREMIUM_BRANDS = [
    "PURFLUX", "MANN-FILTER", "MAHLE", "KNECHT", "BOSCH", "TRW", "ATE", "BREMBO", 
    "DELPHI", "PHINIA", "KYB", "KAYABA", "MONROE", "LEMFÖRDER", "MEYLE", "SACHS", 
    "LUK", "VALEO", "SKF", "GATES", "INA", "DAYCO", "NTN-SNR", "SNR", "DENSO"
]

def get_iam_analysis(oe_ref, brand, iam_ref):
    prompt = f"Expert Aftermarket. Analyse {brand} {iam_ref} pour OE {oe_ref}. Donne Specs et Conseil montage (court)."
    try:
        response = model.generate_content(prompt)
        return response.text
    except: return "Analyse indisponible"

# 3. LE ROBOT "STEALTH" (Utilisant CloudScraper)
def scan_iam_stealth(oe_ref):
    clean_ref = oe_ref.replace(".", "").replace(" ", "").upper()
    url = f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean_ref}"
    
    # Création du scraper qui imite un navigateur réel
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    results = []
    try:
        res = scraper.get(url, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Sélecteurs mis à jour pour les agrégateurs
            items = soup.select('.p-results-list__item') or soup.select('.p-result-item')
            
            for i in items:
                b_tag = i.select_one('.p-result-item__manufacturer') or i.select_one('.brand-name')
                r_tag = i.select_one('.p-result-item__article-number') or i.select_one('.sku')
                
                if b_tag and r_tag:
                    results.append({
                        "Marque": b_tag.text.strip().upper(),
                        "Référence": r_tag.text.strip()
                    })
        return results
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return []

# 4. INTERFACE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("v3.6 | Stealth Engine")
oe_val = st.sidebar.text_input("Référence OE", value="1109AY")

tab1, tab2 = st.tabs(["🔍 IDENTIFICATION", "📊 EXPERTISE IAM"])

with tab2:
    if oe_val:
        st.subheader(f"Comparatif Technique pour {oe_val}")
        
        if st.button("⚡ Lancer l'Analyse Stealth", use_container_width=True):
            with st.spinner(f"Contournement des protections et extraction de {oe_val}..."):
                
                data = scan_iam_stealth(oe_val)
                
                if data:
                    st.success(f"✅ {len(data)} références trouvées.")
                    final_rows = []
                    for item in data:
                        is_top = any(m in item['Marque'] for m in PREMIUM_BRANDS)
                        analysis = get_iam_analysis(oe_val, item['Marque'], item['Référence'])
                        
                        final_rows.append({
                            "Priorité": "🔝 TOP MARQUE" if is_top else "Standard",
                            "Marque": item['Marque'],
                            "Référence": item['Référence'],
                            "Analyse IA": analysis
                        })
                    
                    df = pd.DataFrame(final_rows).sort_values(by="Priorité", ascending=False)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ Le site bloque toujours. Activation du mode 'IA Directe'...")
                    # Fallback IA si même cloudscraper est bloqué
                    prompt_fail = f"Donne les correspondances Purflux, Mann et Bosch pour OE {oe_val}."
                    res_fail = model.generate_content(prompt_fail)
                    st.info(res_fail.text)
