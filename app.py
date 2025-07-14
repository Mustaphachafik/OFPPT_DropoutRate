import streamlit as st
# Hide Streamlit Style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# Page and Navigation setup
st.logo('images/OfpptLogo.png')
st.sidebar.text("""
    📈 Cette application permet aux administrateurs de visualiser les taux de déperdition sous forme de tableau et de graphique à barres après avoir téléchargé le fichier Excel contenant les données nécessaires. 
""")
home_page = st.Page("homepage.py",
                    title="Page d'accueil",
                    icon="🏠",
                    default=True,)   
file_upload_page = st.Page("views/file_upload.py",
                           title="Upload",
                           icon="📂",)
parametrage_page = st.Page("views/parametrage.py",
                           title="Parametrage",
                           icon="⚙️",)
dashboard_page = st.Page("views/dashboard.py",
                         title="Dashboard",
                         icon="📊",)
history_page = st.Page("views/log_history.py",
                         title="Historique des actions",
                         icon="📚",)
pg = st.navigation(pages= [home_page, file_upload_page, parametrage_page, dashboard_page, history_page])
pg.run()