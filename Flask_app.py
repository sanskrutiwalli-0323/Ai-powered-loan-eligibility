from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import pickle
import numpy as np
import mysql.connector


app = Flask(__name__)
app.secret_key = "ai_loan_secret_key"

# ========================= DATABASE CONNECTION =========================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Walli@1234",
        database="loan_project"
    )

# Load model
model = pickle.load(open("C:\\Users\\sanskruti\\OneDrive\\Desktop\\Al_Powered_loan_eligibility\\model (1).pkl", 'rb'))

# ========================= LOGIN SYSTEM =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor()

        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials!")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# Login Required Decorator
def login_required(route_func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return route_func(*args, **kwargs)
    wrapper.__name__ = route_func.__name__
    return wrapper


# ========================= MAIN ROUTES =========================
@app.route('/')
@login_required
def home():
    return render_template("home.html")

@app.route('/explore')
@login_required
def explore():
    return render_template("explore.html")
    
@app.route('/check')
@login_required
def check():
    return render_template("index.html")

@app.route('/predict', methods=["POST"])
@login_required
def predict():

    gender = request.form['gender']
    married = request.form['married']
    dependents = request.form['dependents']
    education = request.form['education']
    employed = request.form['employed']
    credit = float(request.form['credit'])
    area = request.form['area']
    ApplicantIncome = float(request.form['ApplicantIncome'])
    CoapplicantIncome = float(request.form['CoapplicantIncome'])
    LoanAmount = float(request.form['LoanAmount'])
    Loan_Amount_Term = float(request.form['Loan_Amount_Term'])

    male = 1 if gender == "Male" else 0
    married_yes = 1 if married == "Yes" else 0
    not_graduate = 1 if education == "Not Graduate" else 0
    employed_yes = 1 if employed == "Yes" else 0

    if dependents == '1':
        dependents_1, dependents_2, dependents_3 = 1, 0, 0
    elif dependents == '2':
        dependents_1, dependents_2, dependents_3 = 0, 1, 0
    elif dependents == '3+':
        dependents_1, dependents_2, dependents_3 = 0, 0, 1
    else:
        dependents_1, dependents_2, dependents_3 = 0, 0, 0

    if area == "Semiurban":
        semiurban, urban = 1, 0
    elif area == "Urban":
        semiurban, urban = 0, 1
    else:
        semiurban, urban = 0, 0

    ApplicantIncomeLog = np.log(ApplicantIncome)
    totalincomelog = np.log(ApplicantIncome + CoapplicantIncome)
    LoanAmountLog = np.log(LoanAmount)
    Loan_Amount_Termlog = np.log(Loan_Amount_Term)

    prediction = model.predict([[credit, ApplicantIncomeLog, LoanAmountLog,
                                 Loan_Amount_Termlog, totalincomelog, male, married_yes,
                                 dependents_1, dependents_2, dependents_3, not_graduate,
                                 employed_yes, semiurban, urban]])

    result = "Yes 🎉 Congratulations!" if prediction == "Y" else "No ❌ Loan Application Rejected"
    return render_template("prediction.html", prediction_text=f"Loan Status: {result}")


# ========================= CHATBOT SYSTEM =========================

@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")


@app.route('/chatbot_response', methods=['POST'])
def chatbot_response():
    try:
        data = request.get_json()

        # Direct keys from your frontend
        gender = data.get("gender")
        married = data.get("married")
        dependents = data.get("dependents")
        education = data.get("education")
        employed = data.get("employed")
        ApplicantIncome = float(data.get("ApplicantIncome"))
        CoapplicantIncome = float(data.get("CoapplicantIncome"))
        LoanAmount = float(data.get("LoanAmount"))
        Loan_Amount_Term = float(data.get("Loan_Amount_Term"))
        credit = float(data.get("credit"))
        area = data.get("area")

        # Encoding
        male = 1 if gender == "Male" else 0
        married_yes = 1 if married == "Yes" else 0
        not_graduate = 1 if education == "Not Graduate" else 0
        employed_yes = 1 if employed == "Yes" else 0

        if dependents == '1':
            dependents_1, dependents_2, dependents_3 = 1, 0, 0
        elif dependents == '2':
            dependents_1, dependents_2, dependents_3 = 0, 1, 0
        elif dependents == '3+':
            dependents_1, dependents_2, dependents_3 = 0, 0, 1
        else:
            dependents_1, dependents_2, dependents_3 = 0, 0, 0

        if area == "Semiurban":
            semiurban, urban = 1, 0
        elif area == "Urban":
            semiurban, urban = 0, 1
        else:
            semiurban, urban = 0, 0

        # Log values
        ApplicantIncomeLog = np.log(ApplicantIncome)
        totalincomelog = np.log(ApplicantIncome + CoapplicantIncome)
        LoanAmountLog = np.log(LoanAmount)
        Loan_Amount_Termlog = np.log(Loan_Amount_Term)

        # Prediction
        prediction = model.predict([[credit, ApplicantIncomeLog, LoanAmountLog,
                                     Loan_Amount_Termlog, totalincomelog, male, married_yes,
                                     dependents_1, dependents_2, dependents_3, not_graduate,
                                     employed_yes, semiurban, urban]])[0]

        result = "🎉 Congratulations! Your loan is Approved." if prediction == "Y" else "❌ Sorry, your loan is Rejected."

        return jsonify({"result": result})

    except Exception as e:
        print("Chatbot Error:", e)
        return jsonify({"result": "Error processing your request."})




# ========================= RUN APP =========================
if __name__ == "__main__":
    app.run(debug=True)
