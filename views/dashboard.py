import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Tableau de Bord")
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
if 'df' in st.session_state:
    df = st.session_state.df
    # Load closure date and dates from session state
    df_dates = st.session_state.get("df_dates")
    selected_date = st.session_state.get("selected_date")
    # Stop execution if the required values are not available
    if df_dates is None or selected_date is None:
        st.warning("⚠️ La date de clôture n'est pas disponible. Veuillez la définir au préalable dans la page Paramétrage.")
        st.stop()
    # Define default year
    default_year = 2024
    # Use session state to persist selected year
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = default_year
    # Input to allow user to change the year
    if st.session_state.get("role") == "viewer":
        selected_year = st.session_state.selected_year
        st.sidebar.info(f"📅 Année scolaire : {selected_year}")
        st.sidebar.warning(" Vous ne pouvez pas modifier l'année scolaire en mode 'lecture seule'.")
    else:
        selected_year = st.sidebar.number_input("📅 Année scolaire (modifiable) :", min_value=2000, max_value=2030, 
                                            value=st.session_state.selected_year, step=1 )
        # Update session state if changed
        st.session_state.selected_year = selected_year
    # Filter data for the year and Type Formation = 'Diplômante'
    year_data = df[(df['Année Scolaire'] == selected_year) & (df['Type Formation'] == 'Diplômante')]
    # Delete duplicates by Matricule Etudiant
    year_data = year_data.drop_duplicates(subset=['Matricule Etudiant'])
    # Convert 'Date PV' to datetime for filtering, handle errors if any value is invalid
    year_data['Date PV'] = pd.to_datetime(year_data['Date PV'], errors='coerce')
    year_data = year_data.dropna(subset=['Date PV'])
    # Clean the 'Etudiant Actif' column to remove extra spaces and handle case issues (Nettoyage des données qualitatives)
    year_data['Etudiant Actif'] = year_data['Etudiant Actif'].str.strip().str.lower()
    # Calculations for the Table of Institutions
    efps = year_data['Code EFP'].dropna().unique()
    efp_results = []
    for efp in efps:
        efp_data = df[(df['Année Scolaire'] == selected_year) &
                      (df['Type Formation'] == 'Diplômante') &
                      (df['Code EFP'] == efp)]
        efp_data = efp_data.drop_duplicates(subset=['Matricule Etudiant'])
        total_efp_students = len(efp_data)  
        efp_data['Date PV'] = pd.to_datetime(efp_data['Date PV'], errors='coerce')
        efp_data = efp_data.dropna(subset=['Date PV'])
        efp_data['Etudiant Actif'] = efp_data['Etudiant Actif'].str.strip().str.lower()
        # Filter out non-active students and those with registration after the closure date
        efp_dropout_data = efp_data[(efp_data['Type Formation'] == 'Diplômante')&
                                    (efp_data['Etudiant Actif'] == 'non') & 
                                    (efp_data['Date PV'] > pd.to_datetime(selected_date))]
        total_efp_non_active_students = len(efp_dropout_data)
        efp_reorientation_data = efp_data[(efp_data['Type Formation'] == 'Diplômante') &
                                          (efp_data['Etudiant Actif'] == 'non') & 
                                          (efp_data['Date PV'] > pd.to_datetime(selected_date)) & 
                                          (efp_data['Commentairesfs'].str.contains(r'(?i)\b(reo|réo|réorientation|reorientation)\b', regex=True, na=False))]
        total_efp_reorientation_students = len(efp_reorientation_data)
        total_efp_non_active_students = total_efp_non_active_students - total_efp_reorientation_students
        total_efp_active_students = total_efp_students - total_efp_non_active_students
        dropout_efp_rate_1 = (total_efp_non_active_students / total_efp_students) * 100 if total_efp_students > 0 else 0
        dropout_efp_rate_2 = (total_efp_non_active_students / total_efp_active_students) * 100 if total_efp_active_students > 0 else 0
        dropout_efp_rate_percentage_1 = f"{dropout_efp_rate_1:.2f}%"
        dropout_efp_rate_percentage_2 = f"{dropout_efp_rate_2:.2f}%"
        # Store the result for the efp
        efp_results.append({"Code EFP": efp,
                            "Total des stagiaires diplômantes": total_efp_students,
                            "Stagiaires diplômantes actifs": total_efp_active_students,
                            "Stagiaires diplômantes déperdus": total_efp_non_active_students,
                            "Taux de déperdition des inactifs par total": dropout_efp_rate_percentage_1,
                            "Taux de déperdition des inactifs par actifs": dropout_efp_rate_percentage_2 })
    # Calculations for Department's chart
    depts = year_data['Dept'].dropna().unique()
    dept_results = []
    for dept in depts:
        dept_data = df[(df['Année Scolaire'] == selected_year) &
                      (df['Type Formation'] == 'Diplômante') &
                      (df['Dept'] == dept)]
        dept_data = dept_data.drop_duplicates(subset=['Matricule Etudiant'])
        total_dept_students = len(dept_data)  
        dept_data['Date PV'] = pd.to_datetime(dept_data['Date PV'], errors='coerce')
        dept_data = dept_data.dropna(subset=['Date PV'])
        dept_data['Etudiant Actif'] = dept_data['Etudiant Actif'].str.strip().str.lower()
        # Filter out non-active students and those with registration after the closure date
        dept_dropout_data = dept_data[(dept_data['Type Formation'] == 'Diplômante')&
                                    (dept_data['Etudiant Actif'] == 'non') & 
                                    (dept_data['Date PV'] > pd.to_datetime(selected_date))]
        total_dept_non_active_students = len(dept_dropout_data)
        dept_reorientation_data = dept_data[(dept_data['Type Formation'] == 'Diplômante') &
                                          (dept_data['Etudiant Actif'] == 'non') & 
                                          (dept_data['Date PV'] > pd.to_datetime(selected_date)) & 
                                          (dept_data['Commentairesfs'].str.contains(r'(?i)\b(reo|réo|réorientation|reorientation)\b', regex=True, na=False))]
        total_dept_reorientation_students = len(dept_reorientation_data)
        total_dept_non_active_students = total_dept_non_active_students - total_dept_reorientation_students
        total_dept_active_students = total_dept_students - total_dept_non_active_students
        dropout_dept_rate_1 = (total_dept_non_active_students / total_dept_students) * 100 if total_dept_students > 0 else 0
        dropout_dept_rate_2 = (total_dept_non_active_students / total_dept_active_students) * 100 if total_dept_active_students > 0 else 0
        dropout_dept_rate_percentage_1 = f"{dropout_dept_rate_1:.2f}%"
        dropout_dept_rate_percentage_2 = f"{dropout_dept_rate_2:.2f}%"
        # Store the result for the efp
        dept_results.append({"Dept": dept,
                             "Total des stagiaires diplômantes": total_dept_students,
                             "Stagiaires diplômantes actifs": total_dept_active_students,
                             "Stagiaires diplômantes déperdus": total_dept_non_active_students,
                             "Taux de déperdition des inactifs par total": dropout_dept_rate_percentage_1,
                             "Taux de déperdition des inactifs par actifs": dropout_dept_rate_percentage_2 })
    if 'df_dates' in st.session_state:
        df_dates = st.session_state.df_dates
        # Establishment Section
        efp_df = pd.DataFrame(efp_results) # Convert the results to a DataFrame
        if not efp_df.empty and 'Code EFP' in efp_df.columns:
            merged_df = pd.merge(df_dates, efp_df, how="left", on="Code EFP") # Merge efp_df with the df_dates
            # Display the merged data in the dashboard
            st.write(f"### 📋 Tableau des établissements")
            st.dataframe(merged_df)
            # Display the Establishment chart
            efp_df['Taux de déperdition (%)'] = efp_df['Taux de déperdition des inactifs par actifs'].str.rstrip('%').astype(float) # Convertir la colonne en numérique
            fig_efp = px.bar(efp_df, 
                         x="Code EFP", 
                         y="Taux de déperdition (%)",
                         color="Code EFP", 
                         barmode="group", 
                         width=4000,
                         height=600,
                         title="📊 Taux de déperdition par établissement")
            fig_efp.update_traces(width=0.8)
            fig_efp.update_layout(xaxis_tickangle=-45,
                              margin=dict(l=40, r=40, t=80, b=150),
                              hovermode='x unified',
                              hoverdistance=100)
            st.plotly_chart(fig_efp)
            # Display the Department chart
            dept_df = pd.DataFrame(dept_results)
            dept_df['Taux de déperdition (%)'] = dept_df['Taux de déperdition des inactifs par actifs'].str.rstrip('%').astype(float)
            fig_dept = px.pie(dept_df,
                          names="Dept",
                          values="Taux de déperdition (%)",
                          title="📊 Taux de déperdition par département")
            st.plotly_chart(fig_dept)
        else:
            st.warning(f"⚠️ Aucune donnée trouvée pour l'année sélectionnée ({selected_year}). Veuillez en choisir une autre.")    
    else:
        st.warning("⚠️ Les dates de clôture ne sont pas chargées. Veuillez les définir dans la page Paramétrage.")
        st.stop()
else:
    st.error("Aucune donnée disponible. Veuillez télécharger un fichier.")