import os
import json
from sklearn.externals import joblib

import numpy as np

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b530422e14f25b:8126be0f@us-cdbr-iron-east-01.cleardb.net/heroku_0f223e2ec5f08f7'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 499
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20

db = SQLAlchemy(app)

loan_model = joblib.load("loan_model.pkl")
class Applicant(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(45))
    gender = db.Column(db.Boolean)
    married = db.Column(db.Boolean)
    dependents = db.Column(db.Integer)
    education = db.Column(db.String(45))
    self_employed = db.Column(db.Boolean)
    applicant_income = db.Column(db.Float)
    coapplicant_income = db.Column(db.Float)
    loan_amount = db.Column(db.Float)
    loan_amount_term = db.Column(db.Float)
    credit_history = db.Column(db.Integer)
    property_area = db.Column(db.String(45))
    loan_status = db.Column(db.String)
    def __repr__(self):
        return str(self.__dict__)


@app.route('/', methods=["GET"])
def home():    
    applicants = Applicant.query.all()
    print(applicants)
    return render_template("home.html", applicants=applicants)


@app.route('/create_view', methods=["GET"])
def create_view():    
    return render_template("create.html")


@app.route('/update_view', methods=["POST"])
def update_view():    
    applicant_id = request.form.get("id")
    applicant = Applicant.query.filter_by(id=applicant_id).first()
    return render_template("update.html", applicant=applicant)

@app.route('/process', methods=["POST"])
def process():    
    applicant_id = request.form.get("id")
    applicant = Applicant.query.filter_by(id=applicant_id).first()
    data={
        "Gender": int(applicant.gender),
        "Married": int(applicant.married),
        "Dependents": applicant.dependents,
        "Education": int(applicant.education),
        "Self_Employed": int(applicant.self_employed),
        "ApplicantIncome": applicant.applicant_income,
        "CoapplicantIncome": applicant.coapplicant_income,
        "LoanAmount": applicant.loan_amount,
        "Loan_Amount_Term": applicant.loan_amount_term,
        "Credit_History": applicant.credit_history,
        "Property_Area": int(applicant.property_area),
    }
    print(data)
    pred = loan_model.predict(np.array(list(data.values())).reshape(1,-1))
    print(pred[0][0])
    applicant.loan_status = int(pred[0][0])
    db.session.commit()
    return render_template("process.html", applicant=applicant)

@app.route("/create", methods=["POST"])
def create():
    try:
        applicant = Applicant(
                          name=request.form.get("name"), 
                          gender=bool(request.form.get("gender")),
                          married=bool(request.form.get("married")),
                          dependents=request.form.get("dependents"),
                          education=request.form.get("education"),
                          self_employed=bool(request.form.get("self_employed")),
                          applicant_income=request.form.get("applicant_income"),
                          coapplicant_income=request.form.get("coapplicant_income"),
                          loan_amount=request.form.get("loan_amount"),
                          loan_amount_term=request.form.get("loan_amount_term"),
                          credit_history=request.form.get("credit_history"),
                          property_area=request.form.get("property_area"),
                          )
        db.session.add(applicant)
        db.session.commit()
    except Exception as e:
        print("Failed to add applicant")
        print(e)
    return redirect("/")

@app.route("/update", methods=["POST"])
def update():
    try:
        new_applicant_income = request.form.get("applicant_income")
        print(new_applicant_income)
        new_coapplicant_income = request.form.get("coapplicant_income")
        new_loan_amount = request.form.get("loan_amount")
        new_loan_amount_term = request.form.get("loan_amount_term")
        new_credit_history = request.form.get("credit_history")
        applicant_id = request.form.get("id")
        applicant = Applicant.query.filter_by(id=applicant_id).first()
        applicant.applicant_income = new_applicant_income
        applicant.coapplicant_income = new_coapplicant_income
        applicant.loan_amount = new_loan_amount
        applicant.loan_amount_term = new_loan_amount_term
        applicant.credit_history = new_credit_history
        db.session.commit()
    except Exception as e:
        print("Couldn't update applicant")
        print(e)
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    applicant_id = request.form.get("id")
    applicant = Applicant.query.filter_by(id=applicant_id).first()
    db.session.delete(applicant)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(threaded=False)