from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pickle
import pandas as pd
import random
import json
df = pd.read_csv('training_data.csv')
input_symptoms = {}
output_prediction = ""
i_s = {}
for i in df.columns:    
    i_s[i] = random.randrange(0,2,1)
# print(list(df["prognosis"]))
prognosisList = []
for i in list(df["prognosis"]):
    if i not in prognosisList:
        prognosisList.append(i)
app = Flask(__name__)
app.secret_key = "abc"
DTCModel = pickle.load(open('DTCmodel.pkl','rb'))
RFCModel = pickle.load(open('RFCmodel.pkl','rb'))
t_x = pd.read_json(json.dumps([i_s]))
t_x.drop(columns=['prognosis','Unnamed: 133'],axis=1,inplace = True)
@app.route('/',methods=['GET','POST'])
def symptomGiver():
    symptomsList = list(t_x.columns)
    if(request.method == 'POST'):
        chosen_symptoms = request.form.getlist('symptoms')
        for i in df.columns:
            if i in chosen_symptoms:
                input_symptoms[i] = 1
            else:
                input_symptoms[i] = 0
        test_x = pd.read_json(json.dumps([input_symptoms]))
        test_x.drop(columns=['prognosis','Unnamed: 133'],axis=1,inplace = True)
        DTCprediction = DTCModel.predict(test_x)
        RFCprediction = RFCModel.predict(test_x)
        DTCprobs = DTCModel.predict_proba(test_x)
        RFCprobs = RFCModel.predict_proba(test_x)
        print(DTCModel.predict_proba(test_x))
        print(RFCModel.predict_proba(test_x))
        DTCoutput = DTCprediction
        RFCoutput = RFCprediction
        DTCRes = {}
        RFCRes = {}
        for i in range(0,41):
            if DTCprobs[0][i] != 0.0:
                DTCRes[prognosisList[i]] = DTCprobs[0][i]*100
        for i in range(0,41):
            if RFCprobs[0][i] != 0.0:
                RFCRes[prognosisList[i]] = RFCprobs[0][i]*100
        #print(DTCRes)
        #print(RFCRes)
        #output_prediction = {'RFC-result':df.iloc[RFCoutput[0],-2],'DTC-result':df.iloc[DTCoutput[0],-2],}
        output_prediction = {'RFC-result':RFCRes,}
        session["diagnosis"] = output_prediction
        return redirect(url_for('diagnosis'))
    return render_template('index.html',variable = symptomsList)
@app.route('/diagnosis')
def diagnosis():
    #print(session['diagnosis'])
    return render_template('diagnosis.html',variable=session['diagnosis'])
if __name__ == '__main__':
    app.run(port=5000,debug=True)