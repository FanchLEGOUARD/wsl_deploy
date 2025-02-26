from flask import Flask, jsonify, request, render_template, redirect, url_for
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import joblib
from datetime import datetime

load_dotenv()

HOST_MONGODB = os.getenv("HOST_MONGODB")
MONGO_DB_APPNAME = os.getenv("MONGO_DB_APPNAME")
PASSWORD_MONGODB = os.getenv("PASSWORD_MONGODB")
USER_MONGODB = os.getenv("USER_MONGODB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
DB_NAME = os.getenv("DB_NAME")

joblib_path = "/mnt/c/Users/Utilisateur/Documents/fichier_python/___BRIEFS/TP13/deploy_surveill/"
joblib_path = ""

pipeline = joblib.load(joblib_path + "model.joblib", mmap_mode=None)

uri = f"mongodb+srv://{USER_MONGODB}:{PASSWORD_MONGODB}@{HOST_MONGODB}/?retryWrites=true&w=majority&appName={MONGO_DB_APPNAME}"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client[DB_NAME]  # Sélectionner la base de données
collection = db[COLLECTION_NAME]  # Sélectionner la collection

app = Flask(__name__)



@app.route('/create_collection', methods=['GET'])
def create_collection():
    # Ajouter un premier document si la collection est vide
    if collection.count_documents({}) == 0:
        collection.insert_one({"message": "Première insertion dans la collection"})
        return jsonify({"message": "Collection créée et premier document ajouté !"})
    return jsonify({"message": "La collection existe déjà."})


# Page d'accueil
@app.route("/", methods=["GET", "POST"])
def index():
    print("Page d'accueil chargée")
    return render_template("index.html")


# Page de feedback
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    # phrase = request.form.get("label_phrase")
    phrase = request.form.get("label_phrase")   
    prediction = request.form.get("prediction")   
    validation = request.form.get("feedback")
    current_dateTime = datetime.now()
    collection.insert_one({"message": phrase, "prediction":prediction, "validation":validation, "datetime":current_dateTime })
    
    print("Page de feedback chargée\n")
    return render_template("feedback.html", phrase_on_page=phrase, prediction_on_page=prediction, validation_on_page=validation)


# Page de résultat
@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        phrase = request.form.get("label_phrase")
        prediction = pipeline.predict([phrase])[0]  
        return render_template("result.html", phrase_on_page=phrase, prediction_on_page=prediction)
    
    # elif request.method == "GET":
    #     phrase = request.args.get("phrase")
    #     prediction = "prediction ..."
    #     return jsonify({"text": "Toutjours la même chose", "prediction":prediction})
    
    else:
        return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)


