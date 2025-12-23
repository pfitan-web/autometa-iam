import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(page_title="AutoMeta-IAM Pro", layout="wide")
load_dotenv()

# 2. IA GEMINI (Expertise technique)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

def get_technical_specs(oe_ref, brand, iam_ref):
    """Interroge Gemini pour obtenir les spécifications techniques type TecDoc"""
    prompt = f"""
    En tant qu'expert en pièces détachées, donne les caractéristiques techniques clés de la pièce {brand} {iam_ref} 
    qui correspond à l'OE {oe_ref}.
    Format souhaité (très court) : ex: '19 dents, diam. 30mm, avec joint' ou 'Sans consigne, 12V'.
    Si c'est une pompe à eau, précise le matériau de la turbine (Plastique/Métal).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except: return "Données techniques non trouvées"

# 3. LE ROBOT (Extraction des références)
def scan_iam(oe_ref):
    clean_ref = oe_ref.replace(".", "").replace(" ", "").upper()
    url = f"https://www.distriauto.fr/pieces-auto/oem/{clean_ref}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Extraction des cartes produits (On adapte aux balises courantes)
            cards = soup.select('.product-item-info') or soup.select('.product-card')
            for c in cards[:5]:
                brand = c.select_one('.brand-name').text.strip() if c.select_one('.brand-name') else "Inconnu"
                ref = c.select_one('.sku').text.strip() if c.select_one('.sku') else "N/A"
                results.append({"Marque": brand, "Référence IAM": ref})
        return results
    except: return []

# 4. INTERFACE
st.sidebar.title("🚀 AutoMeta-IAM Pro")
oe_val = st.sidebar.text_input("Référence OE", placeholder="Ex: 03L121011J")

tab1, tab2 = st.tabs(["🔍 IDENTIFICATION", "📊 TABLEAU TECHNIQUE IAM"])

with tab2:
    if oe_val:
        st.subheader(f"Analyse Comparative pour {oe_val}")
        
        if st.button("🤖 Générer le tableau technique", use_container_width=True):
            with st.spinner("Extraction et analyse des critères..."):
                data = scan_iam(oe_val)
                
                if data:
                    enriched = []
                    for item in data:
                        # On demande à l'IA de remplir les colonnes de critères
                        specs = get_technical_specs(oe_val, item['Marque'], item['Référence IAM'])
                        
                        enriched.append({
                            "Statut": "✅ Match",
                            "Marque": item['Marque'],
                            "Référence": item['Référence IAM'],
                            "Critères Techniques (Type TecDoc)": specs,
                            "Analyse Fiabilité": "Vérifier suffixe" if "VAG" in specs else "Standard"
                        })
                    
                    # Affichage du tableau stylisé
                    df = pd.DataFrame(enriched)
                    st.table(df)
                else:
                    st.warning("Aucune donnée trouvée par le robot.")
    else:
        st.info("Saisissez une référence en barre latérale.")
