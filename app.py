import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_authenticator as stauth
import yaml
import base64



#from streamlit_dynamic_filters import DynamicFilters"

st.set_page_config(layout="wide", page_icon=":bar_chart:")

from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
   
)



# CSS personnalisé
st.markdown("""
    <style>
        body {
            background-color: #0E1117;
        }
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #111827 60%, #0b1220 100%)
        }
    </style>
""", unsafe_allow_html=True)

# Fonction pour convertir une image locale en base64
def get_base64_of_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Charger ton logo
logo_base64 = get_base64_of_image("assets/logo.png")




try:
    authenticator.login()
except LoginError as e:
    st.error(e)

# Authenticating user

if st.session_state.get('authentication_status') and not st.session_state.get('already_logged_in'):
    st.session_state['already_logged_in'] = True

    # 🔑 Injecter la compagnie depuis le YAML
    username = st.session_state["username"]
    user_config = config["credentials"]["usernames"].get(username, {})
    st.session_state["compagnie"] = user_config.get("compagnie", None)

    st.rerun()


# Réinitialiser le flag après déconnexion
if st.session_state.get('authentication_status') is False or st.session_state.get('authentication_status') is None:
    st.session_state['already_logged_in'] = False

# Affichage conditionnel
if st.session_state.get('authentication_status'):
    compagnie = st.session_state.get("compagnie", None)
    with st.sidebar:

        ### affichage du logo
        st.markdown(
        f"""
        <div style="text-align: center; margin-top: -20px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo_base64}" 
                 style="border-radius: 50%; width:90px; height:90px; margin:10px;">
        </div>
        """,
        unsafe_allow_html=True
        )
        authenticator.logout("Logout", "main")

        # CSS pour agrandir le bouton logout et étendre son conteneur
        st.markdown(
            """
            <style>
            /* Étendre le conteneur du bouton */
            div.stButton {
                display: flex;
                justify-content: stretch;   /* étire le bouton */
                width: 100%;                /* conteneur prend toute la largeur */
            }

            /* Styliser le bouton */
            div.stButton > button:first-child {
                background-color: #ff4b4b;
                color: white;
                width: 100%;                /* bouton occupe toute la largeur du conteneur */
                padding: 9px 24px;
                font-size: 20px;
                border-radius: 8px;
                border: none;
            }

            div.stButton > button:first-child:hover {
                background-color: #ff1c1c;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.write(f'👨‍✈️*{st.session_state["name"]}*')
    st.title("Tableau de bord de visualisation des vehicules")
    df = pd.read_parquet("vehicule11.parquet")
    if compagnie:
        df = df[df['Compagnie'] == compagnie]

    # filtrer par date
    ## conversion de la colonne date
    df['veh_date_circulation'] = pd.to_datetime(df['veh_date_circulation'], errors='coerce')

    # Définir la date limite
    # date_limite = pd.Timestamp('2025-08-31')

    # Remplacer les dates supérieures à la limite
    # df.loc[df['veh_date_circulation'] > date_limite, 'veh_date_circulation'] = date_limite

    # Définir les bornes possibles
    min_date = df['veh_date_circulation'].min().date()
    max_date = df['veh_date_circulation'].max().date()
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input(
            "Date de début",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with col2:
        date_fin = st.date_input(
            "Date de fin",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    # Vérification des dates
    if date_debut > date_fin:
        st.warning("La date de début ne peut pas être postérieure à la date de fin.")

        # Filtrage
    date_debut = pd.to_datetime(date_debut)
    date_fin = pd.to_datetime(date_fin)
        
    df = df[(df['veh_date_circulation'] >= date_debut) & (df['veh_date_circulation'] <= date_fin)]

    st.sidebar.markdown("---")

    # Filtrage par matricule spécifique
    matricule_input = st.sidebar.text_input("Chercher une matricule")
    if matricule_input:

        df = df[df['veh_immatriculation']==matricule_input.upper()]

    st.sidebar.write('Filtrer par :')
    # Filtrage par marque
    veh_marque_dispo = df['veh_marque'].unique().tolist()
    veh_marque = st.sidebar.multiselect("marques", veh_marque_dispo)

    if veh_marque:
        df = df[df['veh_marque'].isin(veh_marque)]


    #Filtrage par model
    model_dispo = df['veh_modele'].unique().tolist()
    model = st.sidebar.multiselect("modeles", model_dispo)
    if model:
        df = df[df['veh_modele'].isin(model)]


    #Filtrage par matricule


    if not compagnie:
        compagnie_disponible = df['Compagnie'].unique().tolist()
        veh_immatriculation = st.sidebar.multiselect("Compagnies", compagnie_disponible)
        if veh_immatriculation:
            df = df[df['Compagnie'].isin(veh_immatriculation)]

    statuts_disponibles = df['anomalie'].unique().tolist()

    # Multiselect dans la sidebar
    statut_selection = st.multiselect(
        "Filtrer par statut d'anomalie oui/non:",
        options=statuts_disponibles
    )

    # Filtrage du DataFrame
    if statut_selection:
        df = df[df['anomalie'].isin(statut_selection)]


    enregistrement = df['veh_nombre_de_place'].count()
    nb_vehicule = df['veh_immatriculation'].nunique()
    nb_vehicule_anomalie = df[df['anomalie'] == 'oui']['veh_immatriculation'].nunique()
    nb_vehicule_clean = nb_vehicule - nb_vehicule_anomalie
    nb_compagnie = df['Compagnie'].nunique()


    


    # Fonction pour créer une carte
    def kpi_card(title, value, emoji):
        st.markdown(f"""
            <div style='
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            '>
                <div style='font-size:14px; color:#555;'>{emoji} {title}</div>
                <div style='font-size:28px; font-weight:bold; color:#1f77b4;'>{value}</div>
            </div>
        """, unsafe_allow_html=True)

    # Affichage en colonnes
    if not compagnie:
        col1, col2, col3, col4, col5 = st.columns(5)
    else:
        col1, col2, col3, col4 = st.columns(4)


    with col1:
        kpi_card("Enregistrements", f"{enregistrement:,.0f}", "👥")

    with col2:
        kpi_card("vehicules", nb_vehicule, "🚙")

    with col3:
        kpi_card("veh anomalies", nb_vehicule_anomalie, "🎟️")

    with col4:
        kpi_card("veh cleans", nb_vehicule_clean, "🧾")
    if not compagnie:
        with col5:
            kpi_card("compagnies", nb_compagnie, "🧾")



    st.write("")

    with st.expander("Aperçu des données"):
        # Trier par date croissante
        df_sorted = df.sort_values('veh_date_circulation')

        # Afficher les 100 premières lignes triées
        st.dataframe(df_sorted.head(100))


    # Nombre de voiture par mois/année

    # Créer deux colonnes : pour l'affichage et pour le tri
    df['Mois_Annee_affichage'] = df['veh_date_circulation'].dt.strftime('%b %Y')  # ex: Jan 2024
    df['Mois_Annee_tri'] = df['veh_date_circulation'].dt.to_period('M').astype(str)

    # Grouper par mois-année tri
    ventes_par_mois = df.groupby('Mois_Annee_tri').size().reset_index(name='Total_ventes')

    # Ajouter la version affichable pour les labels
    ventes_par_mois['Mois_Annee_affichage'] = pd.to_datetime(ventes_par_mois['Mois_Annee_tri']).dt.strftime('%b %Y')

    # Trier par date réelle
    ventes_par_mois['Mois_Annee_date'] = pd.to_datetime(ventes_par_mois['Mois_Annee_tri'])
    ventes_par_mois = ventes_par_mois.sort_values('Mois_Annee_date')

    # Tracer la courbe
    fig7 = px.line(
        ventes_par_mois,
        x='Mois_Annee_affichage',
        y='Total_ventes',
        markers=True,
        title="Nombre total d'immatriculation par mois"
    )
    fig7.update_xaxes(tickangle=45)
    st.plotly_chart(fig7)



         # Distribution par marque
    if "veh_marque" in df.columns:
        marque_counts = df["veh_marque"].astype(str).value_counts().reset_index()
        marque_counts.columns = ["veh_marque", "count"]
        fig_marque = px.bar(
            marque_counts.head(20),
            x="veh_marque",
            y="count",
            title="Top 20 Marques",
            color="count",
            color_continuous_scale="teal",
        )
        fig_marque.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_marque, width='stretch')
      
      # Distribution par modèle
    if "veh_modele" in df.columns:
        modele_counts = df["veh_modele"].astype(str).value_counts().reset_index()
        modele_counts.columns = ["veh_modele", "count"]
        fig_modele = px.bar(
            modele_counts.head(20),
            x="veh_modele",
            y="count",
            title="Top 20 Modèles",
            color="count",
            color_continuous_scale="bluered",
        )
        fig_modele.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_modele, width='stretch')

    if not compagnie:
        # Pie par marque (part de parc)
        if "Compagnie" in df.columns:
            pie_counts = df["Compagnie"].astype(str).value_counts().reset_index()
            pie_counts.columns = ["Compagnie", "count"]
            fig_pie = px.pie(
                pie_counts.head(15), values="count", names="Compagnie", title="Répartition des compagnies"
            )
            fig_pie.update_layout(template="plotly_dark", height=420)
            st.plotly_chart(fig_pie, width='stretch')



        # Sélection des compagnies (via Streamlit)
        compagnies_selectionnees = st.multiselect(
            "Sélectionnez deux compagnies d'assurance",
            options=df['Compagnie'].unique(),
            default=df['Compagnie'].unique()[:2]
        )

        # Vérifier qu'on a bien deux compagnies
        if len(compagnies_selectionnees) == 2:
            # Filtrer les données
            df_filtré = df[df['Compagnie'].isin(compagnies_selectionnees)].copy()

            # Créer les colonnes de tri et d'affichage
            df_filtré['Mois_Annee_tri'] = df_filtré['veh_date_circulation'].dt.to_period('M').astype(str)
            df_filtré['Mois_Annee_date'] = pd.to_datetime(df_filtré['Mois_Annee_tri'])
            df_filtré['Mois_Annee_affichage'] = df_filtré['Mois_Annee_date'].dt.strftime('%b %Y')

            # Grouper par mois et compagnie
            ventes_par_mois = (
                df_filtré.groupby(['Mois_Annee_date', 'Compagnie'])
                .size()
                .reset_index(name='Total_ventes')
            )

            # Tracer la courbe avec une couleur par compagnie
            fig = px.line(
                ventes_par_mois,
                x='Mois_Annee_date',
                y='Total_ventes',
                color='Compagnie',
                markers=True,
                title="Comparaison des immatriculations par compagnie d'assurance"
            )
            fig.update_xaxes(
                tickformat="%b\n%Y",
                tickangle=0,
                title="Mois"
            )
            fig.update_yaxes(title="Nombre d'immatriculations")
            fig.update_layout(legend_title_text="Compagnie")

            # Afficher dans Streamlit
            st.plotly_chart(fig)

        else:
            st.warning("Veuillez sélectionner exactement deux compagnies pour la comparaison.")
    

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
