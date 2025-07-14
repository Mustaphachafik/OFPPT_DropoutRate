import pandas as pd
import streamlit as st
from pathlib import Path
from mongo_logger import log_upload

st.title("📂 Téléchargement de fichier")
# Authentication check
if st.session_state.get("authenticated", False):
    with st.sidebar:
        if st.button("🔒 Se déconnecter"):
            st.session_state.authenticated = False
            st.success("✅ Vous avez été déconnecté.")
            st.rerun()
else:
    st.sidebar.info("🔑 Veuillez vous connecter depuis la page d'accueil.")
    st.error("❌ Vous devez être connecté pour accéder à cette page.")
    st.stop()  # Stop execution here if not connected
# Username check
username = st.session_state.get("username")
if not username:
    st.error("❌ Nom d'utilisateur non défini.")
    st.stop()    
DATA_FILE_PATH = Path("data/data_stagiaires.xlsx") # Define path to saved file
# Check for saved file
if DATA_FILE_PATH.exists():
    choice = st.radio("📁 Un fichier enregistré a été trouvé.:", 
                      ["📂 Utiliser le fichier enregistré", "⬆️ Télécharger un nouveau fichier"], horizontal=True, index=1)
else:
    st.info("Aucun fichier enregistré trouvé.")
    choice = "⬆️ Télécharger un nouveau fichier"
# Upload new file
if choice == "⬆️ Télécharger un nouveau fichier":
    if st.session_state.get("role") == "viewer":
        st.warning("👀 Les utilisateurs en mode 'lecture seule' ne peuvent pas téléverser de nouveaux fichiers.")
    else:
        uploaded_file = st.file_uploader("📂 Télécharger un fichier Excel", type=["xlsx"])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                required_columns = {'Année Scolaire', 'Etudiant Actif', 'Date PV', 'Type Formation'}
                if required_columns.issubset(df.columns):
                    # Save the file locally
                    with open(DATA_FILE_PATH, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                        # Log the upload to MongoDB
                        rows, cols = df.shape
                        log_upload(username, "data_stagiaires.xlsx", rows, cols)
                        st.success("✅ Fichier enregistré sur le stockage local.")
                        st.session_state.df = df
                else:
                    st.error("❌ Le fichier ne contient pas toutes les colonnes requises.")
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
# Use existing saved file
elif choice == "📂 Utiliser le fichier enregistré":
    with st.spinner("⏳ Veuillez patienter, chargement du fichier..."):
        try:
            df = pd.read_excel(DATA_FILE_PATH)
            st.success("✅ Fichier chargé à partir du stockage local.")
            st.session_state.df = df
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du fichier enregistré : {e}")