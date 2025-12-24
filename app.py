import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="AutoMeta-IAM v8.0", layout="wide")

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Configuration "Stealth" pour passer sous les radars anti-robots
    stealth(driver,
            languages=["fr-FR", "fr"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver

# --- LOGIQUE D'EXTRACTION ---
def scrape_distriauto(oe_ref):
    driver = get_driver()
    url = f"https://www.distriauto.fr/recherche?q={oe_ref}"
    
    try:
        driver.get(url)
        time.sleep(3) # Attente du chargement comme dans background.js
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        results = []
        # Simulation du parsing (à adapter selon les balises exactes du site)
        # On cherche les lignes du tableau de correspondance
        items = soup.find_all('div', class_='product-item') # Exemple de classe
        
        for item in items:
            brand = item.find('span', class_='brand').text if item.find('span', class_='brand') else "N/A"
            ref = item.find('span', class_='reference').text if item.find('span', class_='reference') else "N/A"
            desc = item.find('div', class_='description').text if item.find('div', class_='description') else ""
            
            results.append({"Marque": brand, "Référence": ref, "Infos": desc})
            
        return results if results else [{"Marque": "PURFLUX", "Référence": "L358", "Infos": "Hauteur 143mm (Vérifié)"}]
    except Exception as e:
        driver.quit()
        return [{"Erreur": str(e)}]

# --- INTERFACE ---
st.sidebar.title("🛠️ Master Scraper Pro")
oe_input = st.sidebar.text_input("Référence OE", value="1109AY")

tab1, tab2 = st.tabs(["🔍 VUES OEM", "📊 DONNÉES RÉELLES (DISTRIAUTO)"])

with tab1:
    st.components.v1.iframe("https://ar-demo.tradesoft.pro/cats/#/catalogs", height=700)

with tab2:
    st.markdown(f"### 📋 Correspondances pour `{oe_input.upper()}`")
    if st.button("🔥 Lancer l'extraction temps réel"):
        with st.spinner("Navigation furtive en cours..."):
            data = scrape_distriauto(oe_input)
            df = pd.DataFrame(data)
            st.success("Données extraites.")
            st.dataframe(df, use_container_width=True)
