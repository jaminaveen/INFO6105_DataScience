from flask import Flask, request, jsonify, render_template,url_for, redirect
import pandas as pd
from ast import literal_eval
from controller import *

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    error = "None"
    student_dict = {}
    try:
        if request.method == "POST":
            if request.form["tokenfield"] == "registration":
                student_dict["user_name"] = request.form["username"]
                student_dict["email"] = request.form["email"]
                student_dict["password"] = request.form["password1"]
                student_dict["full_name"] = request.form["name"]
                student_dict["gender"] = request.form["gender"]
                student_dict["undergrad_university"] = request.form["univ"]
                student_dict["passYear"] = request.form["passYear"]
                student_dict["number"] = request.form["number"]
                student_dict["location"] = request.form["location"]
                df_student = pd.DataFrame.from_dict([student_dict])

                is_reg_student = save_student_details(student_dict)
                if is_reg_student['email'].count() > 0:
                    return redirect(url_for("studenthome", is_reg_student=is_reg_student.iloc[0]['user_name']))
                else:
                    return render_template('index.html')
            elif request.form["tokenfield"] == "login":
                email = request.form["inputEmail"]
                password = request.form["inputPassword"]
                is_reg_student = get_student_details(email, password)
                if is_reg_student['email'].count() >0:
                    return redirect(url_for("studenthome", is_reg_student=is_reg_student.iloc[0]['user_name']))
                else:
                    return render_template('index.html')
        else:
            return render_template('index.html')
    except Exception as e:
        error = "Provide valid input"
        return render_template('index.html')

@app.route("/studenthome", methods=["GET", "POST"])
def studenthome():
    stud_details= {}
    if request.method == "GET":
        user_name = request.args.get('is_reg_student')
        universities = get_universities()
        return render_template('studenthome.html', user_name=user_name, universities=universities)
    elif request.method == "POST":
        stud_details["user_name"] = request.form["username"]
        stud_details["course"] = request.form["course"]
        stud_details["gre_quants"] = request.form["gre_quants"]
        stud_details["gre_verbal"] = request.form["gre_verbal"]
        stud_details["gre"]= int(stud_details["gre_quants"])+int(stud_details["gre_verbal"])
        stud_details["english_mode"] = request.form["english_mode"]
        stud_details["english_score"] = request.form["english_score"]
        stud_details["ugscore"] = request.form["ugscore"]
        stud_details["ugmode"] = request.form["ugmode"]
        stud_details["workex"] = request.form["workex"]
        stud_details["term"] = request.form["term"]
        stud_details["university_choice"] = request.form["university_choice"]
        # stud_details["undergraduation_score"]= to_cgpa(request.form["ugscore"],request.form["ugmode"])
        stud_details["papers_published"] = request.form["papers_published"]
        df_student = pd.DataFrame.from_dict([stud_details])
        df_student = runDask(df_student) # For scaling IELTS and TOEFL Score
        model = request.form["model_name"]
        pred = student_admit_predict(df_student,model)

        return redirect(url_for("student_predict", stud_details=stud_details, pred=pred))
        print(df_student)

@app.route("/student_predict", methods=["GET", "POST"])
def student_predict():
    if request.method == "GET":
        stud_details = literal_eval(request.args.get('stud_details'))
        df_student = pd.DataFrame.from_dict([stud_details])
        df_with_pred = df_student
        data = df_with_pred.to_dict(orient="records")
        headers = df_with_pred.columns
        return render_template("student_predict.html", data=data,univ_pred="None", headers=headers,
                               username=df_with_pred.iloc[0]['user_name'], pred=request.args.get('pred'))
    elif request.method == "POST":
        stud_details = literal_eval(request.form["data"])
        df_student = pd.DataFrame.from_dict(stud_details)
        df_student = ielts_to_toefl(df_student) # For scaling IELTS and TOEFL Score
        df_student = to_cgpa(df_student) # For percentage to cgpa
        df_with_recommend = student_admit_recommend(df_student)
        univ_pred = df_with_recommend.to_dict(orient="records")
        data = df_student.to_dict(orient="records")
        headers = df_with_recommend.columns
        return render_template("student_predict.html", data=data, univ_pred=univ_pred, headers=headers,
                               username=request.form['username'], pred=request.form['pred'])


@app.route("/university_home", methods=["GET", "POST"])
def university_home():
    if request.method == "GET":
        stud = get_university_student_applied_list()
        stud_list_dict = stud.head(20).to_dict(orient="records")
        headers = stud.columns
        return render_template("university_home.html", stud_list_dict=stud_list_dict, headers=headers, pred='None')
    if request.method == "POST":
        stud_details= literal_eval(request.form["student_data"])

        df_student = pd.DataFrame.from_dict([stud_details])
        stud_list_dict= df_student.to_dict(orient="records")
        pred = get_univ_model(df_student)
        print(pred[0])
        return render_template("university_student_predict.html", stud_list_dict=stud_list_dict, pred= pred[0])

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")

# run Flask app
if __name__ == "__main__":
    app.run("host=0.0.0.0")