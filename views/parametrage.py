import streamlit as st
import pandas as pd
from pathlib import Path
from mongo_logger import log_closure_change

st.title("⚙️ Gestion de la Date de Clôture")
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
# Check if student data is loaded
if 'df' in st.session_state:
    df = st.session_state.df
    # Username check
    username = st.session_state.get("username")
    if not username:
        st.error("❌ Nom d'utilisateur non défini.")
        st.stop() 
    DATE_FILE_PATH = Path("data/efp_date_cloture.xlsx") # File Path
    # Load data from Excel file
    df_dates = pd.read_excel(DATE_FILE_PATH)
    st.session_state.df_dates = df_dates  # Save the current version
    # Check Essential Columns
    required_cols = ['EFP', 'Code EFP', 'Date Clôture']
    if not all(col in df_dates.columns for col in required_cols):
        st.error(f"Le fichier doit contenir les colonnes : {required_cols}")
        st.stop()
    # Select EFP and Modify Closure Date
    col1, col2, col3 = st.columns([0.4, 0.4, 0.2])
    with col1:
        selected_efp = st.selectbox("🏢 Choisissez un établissement", df_dates['EFP'].unique())
        current_date = df_dates.loc[df_dates['EFP'] == selected_efp, 'Date Clôture'].values[0]
        # Format the current date before display
        current_date_formatted = pd.to_datetime(current_date).strftime('%d/%m/%Y')  # Desired format
    with col2:
        selected_date = st.date_input("🗓️ Date de clôture", pd.to_datetime(current_date))
        selected_date = pd.to_datetime(selected_date)
    st.session_state["selected_date"] = selected_date
    # Save Updated Closure Date
    if st.session_state.get("role") != "viewer":
        if st.button("💾 Mettre à jour la date de clôture"):
            old_date = pd.to_datetime(current_date)
            new_date = pd.to_datetime(selected_date)
            # Update dataframe
            df_dates.loc[df_dates['EFP'] == selected_efp, 'Date Clôture'] = new_date.strftime('%d/%m/%Y')
            df_dates.to_excel(DATE_FILE_PATH, index=False)
            # Log the closure change to MongoDB
            log_closure_change(username, selected_efp, old_date.strftime('%d/%m/%Y'), new_date.strftime('%d/%m/%Y'))        
            # Update session state
            st.session_state["selected_efp"] = selected_efp
            st.session_state["selected_date"] = selected_date
            st.session_state.df_dates = df_dates
            st.success("✅ Données mises à jour.")
    else:
        st.info("👀 Les utilisateurs en mode 'lecture seule' ne peuvent pas modifier la date de clôture.")
    # Display updated table
    st.write("### Liste des établissements")
    st.dataframe(df_dates[['EFP', 'Code EFP', 'Date Clôture']])
else:
    st.error("Aucune donnée disponible. Veuillez télécharger un fichier.")