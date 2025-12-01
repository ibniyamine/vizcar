import streamlit as st


### la fonction pour afficher le logo de l'application
def displayLogo(logo):
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: -20px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo}" 
                 style="border-radius: 50%; width:90px; height:90px; margin:10px;">
        </div>
        """,
        unsafe_allow_html=True
    )


def grandir_bouton_logout():
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
    

### la fonction pour afficher une carte KPI
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



def personaliser_body():
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