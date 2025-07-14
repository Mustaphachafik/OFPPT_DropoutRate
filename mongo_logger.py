from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ofppt_app"] # Name of the database
logs_collection = db["logs"]
def log_upload(username, filename, rows, columns):
    logs_collection.insert_one({"Nom d'utilisateur": username,
                                "Action": "Téléchargement de fichier",
                                "Fichier": filename,
                                "Date et heure": datetime.now() })
def log_closure_change(username, efp, old_date, new_date):
    logs_collection.insert_one({"Nom d'utilisateur": username,
                                "Action": "Mise à jour de la date de clôture",
                                "Etablissement": efp,
                                "Ancienne Date": old_date,
                                "Nouvelle Date": new_date,
                                "Date et heure": datetime.now() })