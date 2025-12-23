import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro | Expert OEM", layout="wide")
load_dotenv()

# --- LISTE ÉLARGIE DES MARQUES "TOP 20/80" (OEM & LEADERS IAM) ---
PREMIUM_BRANDS = [
    # Filtration & Moteur
    "PURFLUX", "MANN-FILTER", "MAHLE", "KNECHT", "BOSCH", "HENGST",
    # Freinage & Liaison au sol
    "TRW", "ATE", "BREMBO", "DELPHI", "PHINIA", "FERODO", "KYB", "KAYABA", 
    "MONROE", "LEMFÖRDER", "MOOG", "MEYLE", "SACHS", "BILSTEIN",
    # Transmission & Distribution
    "LUK", "SACHS", "VALEO", "SKF", "GATES", "INA", "DAYCO", "CONTINENTAL", "CONTITECH",
    # Électrique & Thermique
    "MAGNETI MARELLI", "DENSO", "NGK", "BERU", "PIERBURG", "HELLA", "BEHR", "NRF", "NISSENS",
    # Spécialistes Qualité
    "FEBI BILSTEIN", "SWAG", "VAICO", "VEMO", "METELLI", "GRAF"
]

# 2. IA GEMINI (Expertise technique ciblée)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

def get_rich_specs(oe_ref, brand, iam_ref):
    """Génère les données techniques façon TecDoc"""
    prompt = f"""
    Expert automobile Aftermarket. Pour {brand} {iam_ref} (OE {oe_ref}) :
    1. Description précise du produit.
    2. Critères techniques (cotes, dents, connectique, spécificités).
    3. Note de montage ou vigilance technique.
    Format : DESC | SPECS | NOTE
    """
    try:
        response = model.generate_content(prompt)
        parts = response.text.split('|')
        return [p.strip() for p in parts] if len(parts) == 3 else ["N/A"]*3
    except: return ["Données indisponibles"]*3

# 3. LE ROBOT (Scan large Daparto/Aggregateurs)
def scan_full_market(oe_ref):
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

# 4. INTERFACE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
st.sidebar.caption("Version 3.4 | Top Marques OEM")

oe_input = st.sidebar.text_input("Référence OE", value="03L121011J")

tab1, tab2 = st.tabs(["🔍 VUES OEM", "📊 ANALYSE IAM PREMIUM"])

with tab2:
    if oe_input:
        st.subheader(f"Comparatif Technique IAM : {oe_input}")
        
        if st.button("⚡ Lancer l'Analyse (Priorité Top Marques)", use_container_width=True):
            with st.spinner("Recherche et analyse des équipementiers..."):
                raw_data = scan_full_market(oe_input)
                
                if raw_data:
                    final_data = []
                    for item in raw_data:
                        # Vérification de l'appartenance au Top Marques
                        is_top = any(m in item['Marque'] for m in PREMIUM_BRANDS)
                        
                        specs = get_rich_specs(oe_input, item['Marque'], item['Référence'])
                        
                        final_data.append({
                            "Rang": "🔝 TOP MARQUE" if is_top else "Standard",
                            "Marque": item['Marque'],
                            "Référence": item['Référence'],
                            "Description": specs[0],
                            "Critères (Dents/Cotes)": specs[1],
                            "Expertise / Montage": specs[2]
                        })
                    
                    # Tri : Les Top Marques remontent systématiquement
                    df = pd.DataFrame(final_data).sort_values(by="Rang", ascending=False)
                    
                    st.dataframe(
                        df,
                        column_config={
                            "Rang": st.column_config.TextColumn("Statut", help="Marques de première monte ou leaders qualité"),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.warning("Aucun résultat trouvé pour cette référence.")
    else:
        st.info("Saisissez une référence OE dans le menu à gauche.")
