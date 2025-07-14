import streamlit as st
import pandas as pd
from pymongo import MongoClient

st.title("📚 Historique des actions")
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
# Role check (block viewers)
if st.session_state.get("role") == "viewer":
    st.warning("⛔ Vous n'avez pas accès à l'historique des actions.")
    st.stop()
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ofppt_app"]
logs_collection = db["logs"]
# Button to reset history
if st.button("🗑️ Réinitialiser l'historique"):
    logs_collection.delete_many({})
    st.success("✅ Historique réinitialisé avec succès.")
    st.rerun()
# Load logs
logs = list(logs_collection.find({}))
if logs:
    df_logs = pd.DataFrame(logs)
    if "Date et heure" in df_logs.columns:
        df_logs["Date et heure"] = pd.to_datetime(df_logs["Date et heure"])
        df_logs = df_logs.sort_values(by="Date et heure", ascending=False)
        # Format as string and replace original column
        df_logs["Date et heure"] = df_logs["Date et heure"].dt.strftime("%d/%m/%Y %H:%M:%S")
    # Display cleaned logs
    st.dataframe(df_logs.drop(columns=["_id"]))
else:
    st.info("⬆️ Aucune activité enregistrée pour le moment.")
