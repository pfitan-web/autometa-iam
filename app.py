import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION & DESIGN
st.set_page_config(page_title="AutoMeta-IAM Pro | Expert OEM", layout="wide")
load_dotenv()

# Style pour un rendu professionnel type catalogue
st.markdown("""
    <style>
    .stDataFrame { font-size: 13px; }
    thead tr th { background-color: #1f4e79 !important; color: white !important; }
    .main .block-container { padding-top: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONFIGURATION IA GEMINI
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- LISTE "ELITE" DES TOP MARQUES (OEM / RANG 1) ---
PREMIUM_BRANDS = [
    "PURFLUX", "MANN-FILTER", "MAHLE", "KNECHT", "BOSCH", "HENGST",
    "TRW", "ATE", "BREMBO", "DELPHI", "PHINIA", "FERODO", "KYB", "KAYABA", 
    "MONROE", "LEMFÖRDER", "MOOG", "MEYLE", "SACHS", "BILSTEIN",
    "LUK", "VALEO", "SKF", "GATES", "INA", "DAYCO", "CONTINENTAL", "CONTITECH",
    "NTN-SNR", "SNR", "DENSO", "MAGNETI MARELLI", "NGK", "BERU", 
    "PIERBURG", "HELLA", "BEHR", "NRF", "NISSENS", "FEBI BILSTEIN", 
    "VAICO", "VEMO", "METELLI", "GRAF"
]

def get_tecdoc_data(oe_ref, brand, iam_ref):
    """Analyse technique IA type fiche TecDoc"""
    prompt = f"""
    En tant qu'expert Aftermarket, pour la pièce {brand} {iam_ref} (OE {oe_ref}) :
    Donne : 1. Description | 2. Critères techniques (cotes, dents, connectique) | 3. Conseil de pose.
    Format : DESC | SPECS | CONSEIL (très court)
    """
    try:
        response = model.generate_content(prompt)
        parts = response.text.split('|')
        return [p.strip() for p in parts] if len(parts) == 3 else ["N/A"]*3
    except: return ["Données indisponibles"]*3

# 3. LE ROBOT SCANNER (Recherche large sur agrégateurs)
def scan_aftermarket(oe_ref):
    clean_ref = oe_ref.replace(".", "").replace(" ", "").upper()
    url = f"https://www.daparto.fr/recherche-piece/pieces-auto/toutes-marques/{clean_ref}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('.p-results-list__item') or soup.select('.p-result-item')
            for i in items:
                b_tag = i.select_one('.p-result-item__manufacturer') or i.select_one('.brand-name')
                r_tag = i.select_one('.p-result-item__article-number') or i.select_one('.sku')
                if b_tag and r_tag:
                    results.append({"Marque": b_tag.text.strip().upper(), "Référence": r_tag.text.strip()})
        return pd.DataFrame(results).drop_duplicates().to_dict('records')
    except: return []

# 4. BARRE LATÉRALE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("v3.5 | Test Mode OEM")

st.sidebar.subheader("🚗 Identification")
vin = st.sidebar.text_input("VIN", placeholder="WVWZZZ...")
st.sidebar.link_button("🌐 SIV-Auto", "https://siv-auto.fr/", use_container_width=True)

st.sidebar.subheader("📦 Pièce")
oe_input = st.sidebar.text_input("Référence OE", value="03L121011J")

st.sidebar.divider()
if st.secrets.get("PL24_USER"):
    st.sidebar.success("🟢 Session PartsLink24 Active")

# 5. CORPS PRINCIPAL
tab1, tab2 = st.tabs(["🔍 1. VUES ÉCLATÉES OEM", "📊 2. EXPERTISE TECHNIQUE IAM"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=750)

with tab2:
    if oe_input:
        st.markdown(f"### 📋 Comparatif Aftermarket pour `{oe_input.upper()}`")
        
        if st.button("⚡ Lancer l'Analyse (Top Marques Prioritaires)", use_container_width=True):
            with st.spinner("Analyse des équipementiers en cours..."):
                raw_data = scan_aftermarket(oe_input)
                
                if raw_data:
                    final_data = []
                    for item in raw_data:
                        # Vérifier si c'est une Top Marque
                        is_top = any(m in item['Marque'] for m in PREMIUM_BRANDS)
                        
                        specs = get_tecdoc_data(oe_input, item['Marque'], item['Référence'])
                        
                        final_data.append({
                            "Statut": "🔝 TOP MARQUE" if is_top else "Alternative",
                            "Marque": item['Marque'],
                            "Référence": item['Référence'],
                            "Description": specs[0],
                            "Critères (Cotes/Dents)": specs[1],
                            "Expertise Montage": specs[2]
                        })
                    
                    # Tri : Top Marques en premier
                    df = pd.DataFrame(final_data).sort_values(by="Statut", ascending=False)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Aucun résultat trouvé sur les catalogues publics.")
    else:
        st.info("Saisissez une référence OE pour activer l'expertise.")
