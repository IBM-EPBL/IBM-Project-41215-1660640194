from pyexpat import features, model
import numpy
import pickle
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests
import json

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "PQBr9MBF7mFuSh2VVLfOE-liIA04VH-h5VEk8EfjFIuw"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]
print("ML Token",mltoken)

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}



# Declare a Flask app
app = Flask(__name__,template_folder='template')

model = pickle.load(open("rainfall.pkl",'rb'))
scale = pickle.load(open("scale.pkl",'rb'))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/chance/',methods=['GET', 'POST'])
def chance():
    return render_template("chance.html")

@app.route('/nochance/',methods=['GET', 'POST'])
def nochance():
    return render_template("noChance.html")


@app.route('/help/')
def help():
    return render_template("help.html")

@app.route('/contact/')
def contact():
    return render_template("contact.html")

@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/predict',methods=['POST','GET'])
def predict():
    res = " "
     # If a form is submitted
    if request.method == "POST":
        Location = request.form.get('Location')
        MinTemp = request.form['MinTemp']
        MaxTemp = request.form['MaxTemp']
        Rainfall = request.form['Rainfall']
        WindGustSpeed = request.form['WindGustSpeed']
        WindSpeed9am = request.form['WindSpeed9am']
        WindSpeed3pm = request.form['WindSpeed3pm']
        Humidity9am = request.form['Humidity9am']
        Humidity3pm = request.form['Humidity3pm']
        Pressure9am = request.form['Pressure9am']
        Pressure3pm = request.form['Pressure3pm']
        Temp9am = request.form['Temp9am']
        Temp3pm = request.form['Temp3pm']
        RainToday = request.form.get('RainToday')
        WindGustDir = request.form.get('WindGustDir')
        WindDir9am = request.form.get('WindDir9am')
        WindDir3pm = request.form.get('WindDir3pm')   

        new_row = {'Location':Location,'MinTemp':MinTemp,'MaxTemp':MaxTemp,'Rainfall':Rainfall,'WindGustSpeed':WindGustSpeed,'WindSpeed9am':WindSpeed9am,'WindSpeed3pm':WindSpeed3pm,'Humidity9am':Humidity9am,'Humidity3pm':Humidity3pm,'Pressure9am':Pressure9am,'Pressure3pm':Pressure3pm,'Temp9am':Temp9am,'Temp3pm':Temp3pm,'RainToday':RainToday,'WindGustDir':WindGustDir,'WindDir9am':WindDir9am,'WindDir3pm':WindDir3pm}
        print(new_row)
        new_df = pd.DataFrame(columns=['Location','MinTemp','MaxTemp','Rainfall','WindGustSpeed','WindSpeed9am','WindSpeed3pm','Humidity9am','Humidity3pm','Pressure9am','Pressure3pm','Temp9am','Temp3pm','RainToday','WindGustDir','WindDir9am','WindDir3pm'])
        new_df = new_df.append(new_row,ignore_index=True)
        labeled = new_df[['Location','MinTemp','MaxTemp','Rainfall','WindGustSpeed','WindSpeed9am','WindSpeed3pm','Humidity9am','Humidity3pm','Pressure9am','Pressure3pm','Temp9am','Temp3pm','RainToday','WindGustDir','WindDir9am','WindDir3pm']]
        X = labeled.values
        print(X)
        payload_scoring = {"input_data": [{"field": [['Location','MinTemp','MaxTemp','Rainfall','WindGustSpeed','WindSpeed9am','WindSpeed3pm','Humidity9am','Humidity3pm','Pressure9am','Pressure3pm','Temp9am','Temp3pm','RainyToday','WindGustDir','WindDir9am','WindDir3pm']], "values": X.tolist()}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/73230b85-51ea-45db-baa7-e86b5d528fbe/predictions?version=2022-11-14', json=payload_scoring,headers={'Authorization': 'Bearer ' + mltoken})
        print("Scoring response")
        predictions = response_scoring.json()
        print(predictions)
        output =  predictions['predictions'][0]['values'][0][0]
        print(output)
    else:
        output = ""

    if output == 1:
       return redirect(url_for('chance'))

    elif output == 0:
        return redirect(url_for('nochance'))
 
    return render_template("index.html", output = res)
 
#Running the app

if __name__== "___main___":
    app.run(debug = True,host='0.0.0.0',port=80)