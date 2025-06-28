import streamlit as st
import pandas as pd
import base64
import time
import requests
from bs4 import BeautifulSoup

# Set page config
st.set_page_config(
    page_title="My Data Scraper App",
    page_icon="🚗",
    layout="wide"
)

# Initialize session state
if 'vehicles_data' not in st.session_state:
    st.session_state['vehicles_data'] = None
if 'motorcycle_data' not in st.session_state:
    st.session_state['motorcycle_data'] = None
if 'rentals_data' not in st.session_state:
    st.session_state['rentals_data'] = None

# Sidebar
st.sidebar.header("Fonctionnalités supplémentaires")

# Pages indexes
st.sidebar.subheader("Pages indexes")
selected_pages = st.sidebar.selectbox("", [1, 2, 3, 4, 5], index=1)

# Options
st.sidebar.subheader("Options")
scraping_options = [
    "Scraper des données avec beautifulSoup",
    "Scraper des données avec Web Scraper",
    "Tableau de bord des données",
    "Remplir le formulaire"
]
selected_option = st.sidebar.selectbox("", scraping_options)

# Main content
st.title("MY DATA SCRAPER APP")

st.markdown("""
Cette application permet de scrapper des données de véhicules, motos et locations de voitures à partir du site dakar-auto.com en utilisant beautifulsoup et web scraper.

• **Librairies Python :** base64, pandas, streamlit, requests, bs4  
• **Data source :** dakar-auto.com
""")

# Fonction pour créer un lien de téléchargement
def create_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download data as CSV</a>'
    return href

# Fonction de scrappage pour le site d'achats devéhicules
def scrape_vehicles_data(max_pages):
    data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for p in range(1, max_pages + 1):
        status_text.text(f'Scraping page {p}/{max_pages}...')
        progress_bar.progress(p / max_pages)
        
        try:
            url = f"https://dakar-auto.com/senegal/voitures-4?&page={p}"
            content = requests.get(url)

            if content.status_code != 200: 
                st.warning(f"Page {p} est indisponible.")
                continue 
            
            st.write(f"Page {p} a été scrappée.")
            soup = BeautifulSoup(content.text, 'html.parser')
            containers = soup.find_all('div', class_="listings-cards__list-item mb-md-3 mb-3")
            
            for container in containers: 
                try:
                    marque = container.find('h2', class_="listing-card__header__title mb-md-2 mb-0").get_text(strip=True)
                    prix = container.find('h3', class_="listing-card__header__price font-weight-bold text-uppercase mb-0").get_text(strip=True).replace('\u202f', ' ')
                    adresse_1 = container.find('span', class_="province font-weight-bold d-inline-block").get_text(strip=True)
                    li_tags = container.find_all('li', class_="listing-card__attribute list-inline-item")

                    kilometrage = li_tags[1].get_text(strip=True) if len(li_tags) > 1 else "---"
                    boite_vitesse = li_tags[2].get_text(strip=True) if len(li_tags) > 2 else "---"
                    type_carburant = li_tags[3].get_text(strip=True) if len(li_tags) > 3 else "---"

                    proprietaire_tag = container.find('p', class_="time-author m-0")
                    proprietaire = proprietaire_tag.get_text(strip=True).strip("Par ") if proprietaire_tag else "---"

                    data.append({
                        'marque': marque.split(' ')[0],
                        'année': marque.split(' ')[2] if len(marque.split(' ')) > 2 and marque.split(' ')[2].isnumeric() else "---",
                        'prix': prix,
                        'adresse': adresse_1,
                        'kilométrage': kilometrage,
                        'boite vitesse': boite_vitesse,
                        'carburant': type_carburant, 
                        'propriétaire': proprietaire
                    })
                except Exception as e: 
                    st.error(f"Erreur lors du scraping d'un véhicule: {e}")
                    pass
        except Exception as e:
            st.error(f"Erreur lors du scraping de la page {p}: {e}")
            continue
        
        # Add delay between requests to be respectful
        time.sleep(1)
    
    status_text.text('Scraping terminé!')
    return pd.DataFrame(data)

# Fonction de scrappage pour le site ded'achats de motos
def scrape_motorcycle_data(max_pages):
    data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for p in range(1, max_pages + 1):
        status_text.text(f'Scraping page {p}/{max_pages}...')
        progress_bar.progress(p / max_pages)
        
        try:
            url = f"https://dakar-auto.com/senegal/motos-and-scooters-3?&page={p}"
            content = requests.get(url)

            if content.status_code != 200: 
                st.warning(f"Page {p} est indisponible.")
                continue 
            
            st.write(f"Page {p} a été scrappée.")
            soup = BeautifulSoup(content.text, 'html.parser')
            containers = soup.find_all('div', class_="listing-card__content__inner")
            
            for container in containers: 
                try:
                    product_title_tag = container.find('h2', class_="listing-card__header__title mb-md-2 mb-0").get_text(strip=True)
                    prix = container.find('h3', class_="listing-card__header__price font-weight-bold text-uppercase mb-0").get_text(strip=True).replace('\u202f', ' ')
                    adresse_1 = container.find('span', class_="town-suburb d-inline-block").get_text(strip=True)
                    adresse_2 = container.find('span', class_="province font-weight-bold d-inline-block").get_text(strip=True)
                    kilometrage = container.find_all('li', class_="listing-card__attribute list-inline-item")
                    proprietaire = container.find('p', class_="time-author m-0").get_text(strip=True).strip('Par')
                    
                    data.append({
                        'marque': product_title_tag.split(' ')[0],
                        'annee': product_title_tag.split(' ')[-1],
                        'prix': prix,
                        'adresse': f"{adresse_1}, {adresse_2}",
                        'kilometrage': kilometrage[1].get_text(strip=True) if len(kilometrage) > 1 else "---",
                        'proprietaire': proprietaire
                    })
                except Exception as e: 
                    st.error(f"Erreur lors du scraping d'une moto: {e}")
                    pass
        except Exception as e:
            st.error(f"Erreur lors du scraping de la page {p}: {e}")
            continue
        
        # Add delay between requests to be respectful
        time.sleep(1)
    
    status_text.text('Scraping terminé!')
    return pd.DataFrame(data)

# Fonction de scrappage pour le site de location
def scrape_rentals_data(max_pages):
    data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for p in range(1, max_pages + 1):
        status_text.text(f'Scraping page {p}/{max_pages}...')
        progress_bar.progress(p / max_pages)
        
        try:
            url = f"https://dakar-auto.com/senegal/location-de-voitures-19?&page={p}"
            content = requests.get(url)

            if content.status_code != 200: 
                st.warning(f"Page {p} est indisponible.")
                continue 
            
            st.write(f"Page {p} a été scrappée.")
            soup = BeautifulSoup(content.text, 'html.parser')
            containers = soup.find_all('div', class_="listing-card__content__inner")
            
            for container in containers: 
                try:
                    marque = container.find('h2', class_="listing-card__header__title mb-md-2 mb-0").get_text(strip=True)
                    prix = container.find('h3', class_="listing-card__header__price font-weight-bold text-uppercase mb-0").get_text(strip=True).replace('\u202f', ' ')
                    adresse_1 = container.find('span', class_="town-suburb d-inline-block").get_text(strip=True)
                    adresse_2 = container.find('span', class_="province font-weight-bold d-inline-block").get_text(strip=True)   
                    proprietaire = container.find('p', class_="time-author m-0").get_text(strip=True)
                    
                    data.append({
                        'marque': marque.split(' ')[0] if marque else "---",
                        'annee': marque.split(' ')[-1] if marque and len(marque.split(' ')) > 1 else "---",
                        'prix': prix,
                        'adresse': f"{adresse_1}, {adresse_2}",
                        'proprietaire': proprietaire
                    })
                except Exception as e: 
                    st.error(f"Erreur lors du scraping d'une location: {e}")
                    pass
        except Exception as e:
            st.error(f"Erreur lors du scraping de la page {p}: {e}")
            continue
        
        # Add delay between requests to be respectful
        time.sleep(1)
    
    status_text.text('Scraping terminé!')
    return pd.DataFrame(data)

# Les boutons principaux
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Données de véhicules", use_container_width=True):
        if selected_option == "Scraper des données avec beautifulSoup":
            st.subheader("Scraping des données de véhicules")

            with st.spinner("Scraping en cours..."):
                df_vehicles = scrape_vehicles_data(selected_pages)
            
            if not df_vehicles.empty:
                st.success(f"Scrappage réussi de {len(df_vehicles)} véhicules depuis {selected_pages} pages!")
                st.dataframe(df_vehicles, use_container_width=True)
                st.markdown(create_download_link(df_vehicles, "vehicles_data.csv"), unsafe_allow_html=True)
                st.session_state['vehicles_data'] = df_vehicles
            else:
                st.warning("Aucune donnée de véhicule trouvée.")

        elif selected_option == "Scraper des données avec Web Scraper":
            st.subheader("Téléchargement des données Web Scraper (non nettoyées)")
            
            with st.spinner("Chargement des données Web Scraper..."):
                time.sleep(2) 
                try:
                    df_raw_webscraper = pd.read_csv("C:\\Users\\skabo\\OneDrive\\Bureau\\DIT - Maitrise en Intelligence Artificielle\\Data Collection\\Examen\\data\\dakar-auto.csv")
                    st.success(f"{len(df_raw_webscraper)} lignes chargées depuis Web Scraper.")
                    st.dataframe(df_raw_webscraper)
                    st.markdown(create_download_link(df_raw_webscraper, "dakar-auto.csv"), unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error("Fichier non trouvé. Assurez-vous d'avoir placé 'dakar-auto.csv' dans le dossier /data.")

            
        elif selected_option == "Download scraped data":
            if st.session_state['vehicles_data'] is not None and not st.session_state['vehicles_data'].empty:
                st.subheader("Downloaded Vehicles Data")
                st.dataframe(st.session_state['vehicles_data'], use_container_width=True)
                st.markdown(create_download_link(st.session_state['vehicles_data'], "vehicles_data.csv"), unsafe_allow_html=True)
            else:
                st.warning("Aucune donnée récupérée n'est disponible. Veuillez d'abord récupérer les données.")

with col2:
    if st.button("Données de moto", use_container_width=True):
        if selected_option == "Scraper des données avec beautifulSoup":
            st.subheader("Scraping des données de moto")

            with st.spinner("Scraping en cours..."):
                df_motorcycles = scrape_motorcycle_data(selected_pages)
            
            if not df_motorcycles.empty:
                st.success(f"Scraping réussi de {len(df_motorcycles)} motos depuis {selected_pages} pages !")
                st.dataframe(df_motorcycles, use_container_width=True)
                st.markdown(create_download_link(df_motorcycles, "motorcycle_data.csv"), unsafe_allow_html=True)
                st.session_state['motorcycle_data'] = df_motorcycles
            else:
                st.warning("Aucune donnée de moto trouvée.")

        elif selected_option == "Scraper des données avec Web Scraper":
            st.subheader("Téléchargement des données Web Scraper (non nettoyées)")
            
            with st.spinner("Chargement des données Web Scraper..."):
                time.sleep(2) 
                try:
                    df_raw_webscraper = pd.read_csv("C:\\Users\\skabo\\OneDrive\\Bureau\\DIT - Maitrise en Intelligence Artificielle\\Data Collection\\Examen\\data\\dakar-auto-scooter.csv")
                    st.success(f"{len(df_raw_webscraper)} lignes chargées depuis Web Scraper.")
                    st.dataframe(df_raw_webscraper)
                    st.markdown(create_download_link(df_raw_webscraper, "dakar-auto-scooter.csv"), unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error("Fichier non trouvé. Assurez-vous d’avoir placé 'dakar-auto-scooter.csv' dans le dossier /data.")


        elif selected_option == "Download scraped data":
            if st.session_state['motorcycle_data'] is not None and not st.session_state['motorcycle_data'].empty:
                st.subheader("Downloaded Motorcycle Data")
                st.dataframe(st.session_state['motorcycle_data'], use_container_width=True)
                st.markdown(create_download_link(st.session_state['motorcycle_data'], "motorcycle_data.csv"), unsafe_allow_html=True)
            else:
                st.warning("No scraped data available. Please scrape data first.")

with col3:
    if st.button("Données de location", use_container_width=True):
        if selected_option == "Scraper des données avec beautifulSoup":
            st.subheader("Scraping des données de location")

            with st.spinner("Scraping en cours..."):
                df_rentals = scrape_rentals_data(selected_pages)
            
            if not df_rentals.empty:
                st.success(f"Successfully scraped {len(df_rentals)} rentals from {selected_pages} pages!")
                st.dataframe(df_rentals, use_container_width=True)
                st.markdown(create_download_link(df_rentals, "rentals_data.csv"), unsafe_allow_html=True)
                st.session_state['rentals_data'] = df_rentals
            else:
                st.warning("Aucune donnée de location trouvée.")
        
        elif selected_option == "Scraper des données avec Web Scraper":
            st.subheader("Téléchargement des données Web Scraper (non nettoyées)")
            
            with st.spinner("Chargement des données Web Scraper..."):
                time.sleep(2) 
                try:
                    df_raw_webscraper = pd.read_csv("C:\\Users\\skabo\\OneDrive\\Bureau\\DIT - Maitrise en Intelligence Artificielle\\Data Collection\\Examen\\data\\dakar-auto-location.csv")
                    st.success(f"{len(df_raw_webscraper)} lignes chargées depuis Web Scraper.")
                    st.dataframe(df_raw_webscraper)
                    st.markdown(create_download_link(df_raw_webscraper, "dakar-auto-location.csv"), unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error("Fichier non trouvé. Assurez-vous d’avoir placé 'dakar-auto-location.csv' dans le dossier /data.")


        elif selected_option == "Download scraped data":
            if st.session_state['rentals_data'] is not None and not st.session_state['rentals_data'].empty:
                st.subheader("Downloaded Rentals Data")
                st.dataframe(st.session_state['rentals_data'], use_container_width=True)
                st.markdown(create_download_link(st.session_state['rentals_data'], "rentals_data.csv"), unsafe_allow_html=True)
            else:
                st.warning("Aucune donnée récupérée n'est disponible. Veuillez d'abord récupérer les données.")


# Formulaire d'évaluation
if selected_option == "Remplir le formulaire":
    st.subheader("Formulaire d'évaluation de l'application")

    with st.form("evaluation_form"):
        st.write("Veuillez évaluer cette application :")

        rating = st.select_slider(
            "Note globale :",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: "⭐" * x
        )
        
        ease_of_use = st.radio(
            "Facilité d'utilisation :",
            ["Très facile", "Facile", "Modéré", "Difficile", "Très difficile"]
        )
        
        usefulness = st.radio(
            "Utilité de cette application :",
            ["Très utile", "Utile", "Assez utile", "Peu utile", "Pas utile"]
        )
        
        performance = st.radio(
            "Comment évaluez-vous la performance du scraping ?",
            ["Excellent", "Bon", "Moyen", "Pauvre", "Très pauvre"]
        )
        
        feedback = st.text_area("Commentaires ou suggestions supplémentaires :")

        submitted = st.form_submit_button("Soumettre l'évaluation")

        if submitted:
            st.success("Merci pour vos commentaires !")
            st.balloons()
            
            # Display submitted data
            st.write("**Votre évaluation :**")
            st.write(f"- Note : {'⭐' * rating}")
            st.write(f"- Facilité d'utilisation : {ease_of_use}")
            st.write(f"- Utilité : {usefulness}")
            st.write(f"- Performance : {performance}")
            if feedback:
                st.write(f"- Commentaires : {feedback}")
elif selected_option == "Tableau de bord des données":
    st.subheader("Tableau de bord des données")

    dataset_choice = st.radio("Choisissez le dataset à afficher :", 
                              ("Véhicules", "Motos", "Locations"))

    file_map = {
        "Véhicules": "C:\\Users\\skabo\\OneDrive\\Bureau\\DIT - Maitrise en Intelligence Artificielle\\Data Collection\\Examen\\data\\vehicles.csv",
        "Motos": "C:\\Users\\skabo\\OneDrive\\Bureau\\DIT - Maitrise en Intelligence Artificielle\\Data Collection\\Examen\\data\\motorcycles.csv",
        "Locations": "C:\\Users\\skabo\\OneDrive\\Bureau\\DIT - Maitrise en Intelligence Artificielle\\Data Collection\\Examen\\data\\locations.csv"
    }

    selected_file = file_map[dataset_choice]

    try:
        df_dashboard = pd.read_csv(selected_file)
        st.success(f"{len(df_dashboard)} lignes chargées pour {dataset_choice}")
        st.dataframe(df_dashboard, use_container_width=True)

        if dataset_choice == "Véhicules":
            st.write("### Top Marques")
            marque_counts = df_dashboard['marque'].value_counts().head(10)
            st.bar_chart(marque_counts)

            st.write("### Prix moyen par marque (Top 5)")
            df_dashboard['prix'] = pd.to_numeric(df_dashboard['prix'], errors='coerce')
            prix_moyens = df_dashboard.groupby('marque')['prix'].mean().sort_values(ascending=False).head(5)
            st.bar_chart(prix_moyens)

        elif dataset_choice == "Motos":
            st.write("### Kilométrage moyen par marque (Top 5)")
            df_dashboard['kilométrage'] = pd.to_numeric(df_dashboard['kilométrage'], errors='coerce')
            km_moyens = df_dashboard.groupby('marque')['kilométrage'].mean().sort_values(ascending=False).head(5)
            st.bar_chart(km_moyens)

            st.write("### Distribution des années")
            annee_counts = df_dashboard['année'].value_counts().sort_index()
            st.bar_chart(annee_counts)

        elif dataset_choice == "Locations":
            st.write("### Répartition par propriétaires")
            proprios = df_dashboard['propriétaire'].value_counts().head(10)
            st.bar_chart(proprios)

            st.write("### Prix moyen par marque")
            df_dashboard['prix'] = pd.to_numeric(df_dashboard['prix'], errors='coerce')
            prix_loc = df_dashboard.groupby('marque')['prix'].mean().sort_values(ascending=False).head(5)
            st.bar_chart(prix_loc)

    except FileNotFoundError:
        st.warning(f"Fichier introuvable : {selected_file}")
    except Exception as e:
        st.error(f"Erreur lors du chargement ou de l'affichage : {e}")


# Footer
st.markdown("---")
st.info("""
**A propos de l'application:**
Cette application a été développée dans le cadre de l'examen de data collection.
""")