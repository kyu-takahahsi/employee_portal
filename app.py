#Flask関係
from flask import Flask, render_template, request, make_response, session, flash, redirect, url_for
app = Flask(__name__)
#データベース操作
import mysql.connector
from mysql.connector import errorcode
#正規表現
import re
#画像保存のため
import os
#画像保存のため
from werkzeug.utils import secure_filename
#ランダム選択
import random
#ランダムな文字列作成
import string
#MVC
import model.database as db
#from model.item import EMP, DEPT
#21章
#画像のためのパスや定義
UPLOAD_FOLDER = './static/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#ホーム画面
@app.route("/", methods=['GET', 'POST'])
def employeeList():
    emp_info = db.tableDataStorage()
    params = {
    "emp_info" : emp_info
    }
    return render_template("all_emp.html", **params)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
#HTMLから情報を受け取る
def getEmpInfo():
    add = "新規追加"
    emp_name = request.form.get("emp_name", "")
    emp_age = request.form.get("emp_age", "")
    emp_sex = request.form.get("emp_sex", "")
    emp_postal = request.form.get("emp_postal", "")
    emp_pref = request.form.get("emp_pref", "")
    emp_address = request.form.get("emp_address", "")
    emp_dept = request.form.get("emp_dept", "")
    join_date = request.form.get("join_date", "")
    retire_date = request.form.get("retire_date", "")
    emp_image = request.files.get("emp_image", "")
    image_id = ""
    #画像ID作成
    for i in range(10):
        image_id += (random.choice(string.ascii_letters))
    return add, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, emp_image


#画像の有無
def imageSetVariable(emp_image):
    add_emp_image = ""
    if emp_image != "":
        filename = secure_filename(emp_image.filename)
        if filename != "":
            emp_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            add_emp_image = "../static/" + filename
        else:
            emp_image = ""
    return add_emp_image, emp_image


#値を集約
def correctAddEmpValue(add, judge, result, dept_info):
    params = {
        "add" : add,
        "judge" : judge,
        "result" : result,
        "dept_info" : dept_info
    }
    return params


#新規追加URL(部品を集めて実行する)
@app.route("/emp/add", methods=["POST"])
def addNewEmp():
    add, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, emp_image = getEmpInfo()
    add_emp_image, emp_image = imageSetVariable(emp_image)
    cursor, cnx = db.connectDatabase()
    dept_info = db.deptInfoData(cursor)
    info_add, img_add = db.setAddEmpQuery(emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image)
    judge, result = db.exeAddEmpQuery(cursor, cnx,  emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image, emp_image, info_add, img_add)
    params = correctAddEmpValue(add, judge, result, dept_info)
    return render_template("emp_add.html", **params)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#編集する社員の情報を取得
def getChangeEmpInfo():
    #編集が押された社員のidを取得
    change_info = request.form.get("change_info", "")
    #編集が押された社員の基本情報を取得
    emp_name = request.form.get("emp_name", "")
    emp_age = request.form.get("emp_age", "")
    emp_sex = request.form.get("emp_sex", "")
    emp_postal = request.form.get("emp_postal", "")
    emp_pref = request.form.get("emp_pref", "")
    emp_address = request.form.get("emp_address", "")
    emp_dept = request.form.get("emp_dept", "")
    join_date = request.form.get("join_date", "")
    retire_date = request.form.get("retire_date", "")
    emp_image = request.files.get("emp_image", "")
    image_id = request.form.get("image_id", "")
    return change_info, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, emp_image


#値を集約
def correctEditValue(pref_select, dept_select, dept_info, edit_info, judge, result):
    params = {
        "pref_select" : pref_select,
        "dept_select" : dept_select,
        "dept_info" : dept_info,
        "edit_info" : edit_info,
        "result" : result,
        "judge" : judge
    }
    return params


#編集のURL(部品を集めて実行する)
@app.route("/emp/edit", methods=["POST"])
def editEmp():
    change_info, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, emp_image = getChangeEmpInfo()
    add_emp_image, emp_image = imageSetVariable(emp_image)
    cursor, cnx = db.connectDatabase()
    dept_info = db.deptInfoData(cursor)
    edit_info, dept_select, pref_select = db.getEditEmpinfo(cursor, change_info)
    info_update, img_update = db.setEditEmpQuery(change_info, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image)
    judge, result = db.exeEditQuery(cursor, cnx,  emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image, emp_image, info_update, img_update)
    params = correctEditValue(pref_select, dept_select, dept_info, edit_info, judge, result)
    return render_template("emp_add.html", **params)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#検索条件の取得
def getSearchEmpInfo():
    search_dept = request.form.get("search_dept", "")
    search_emp_id = request.form.get("search_emp_id", "")
    search_name = request.form.get("search_name", "")
    return search_dept, search_emp_id, search_name


#値を集約
def correctSearchEmpValue(search_name, search_emp_id, search_dept, dept_info, emp_info, emp_count):
    params = {
        "search_name" : search_name,
        "search_emp_id" : search_emp_id,
        "search_dept" : search_dept,
        "emp_count" : emp_count,
        "dept_info" : dept_info,
        "emp_info" : emp_info
    }
    return params


#検索のURL(部品を集めて実行する)
@app.route("/emp/search", methods=["POST"])
def searchEmp():
    search_dept, search_emp_id, search_name = getSearchEmpInfo()
    cursor, cnx = db.connectDatabase()
    dept_info = db.deptInfoData(cursor)
    query = db.setSearchQuery(search_dept, search_emp_id, search_name)
    emp_info, emp_count = db.exeSearchEmpQuery(cursor, query)
    params = correctSearchEmpValue(search_name, search_emp_id, search_dept, dept_info, emp_info, emp_count)
    return render_template("emp_search.html", **params)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#csv出力
@app.route('/emp/output', methods=["GET", "POST"])
def outputCsv():
    cursor, cnx = db.connectDatabase()
    csv = db.downloads(cursor)
    response = make_response(csv)
    response.headers["Content-Disposition"] = f"attachment; filename=employee_information.csv"
    return response

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#削除する社員の情報取得
def getDeleteEmpInfo():
    delete_info = request.form.get("delete_info", "")
    emp_name = request.form.get("emp_name", "")
    return delete_info, emp_name


#値を集約
def correctDeleteEmpValue(emp_info, message):
    params = {
        "emp_info" : emp_info,
        "message" : message
    }
    return params


#削除のURL(部品を集めて実行する)
@app.route("/emp/delete", methods=["POST"])
def deleteEmp():
    delete_info, emp_name = getDeleteEmpInfo()
    cursor, cnx = db.connectDatabase()
    dept_info = db.deptInfoData(cursor)
    info_delete, img_delete = db.setDeleteEmpQuery(delete_info)
    emp_info = db.tableDataStorage()
    exist_info = db.comformDeleteEmpInfo(emp_info, delete_info)
    message, emp_info = db.exeDeleteEmpQuery(cursor, cnx, info_delete, img_delete, delete_info, emp_name, exist_info)
    params = correctDeleteEmpValue(emp_info, message)
    return render_template("all_emp.html", **params)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#部署画面
#ホーム画面
@app.route("/dept", methods=["GET", "POST"])
def deptList():
    cursor, cnx = db.connectDatabase()
    dept_info = db.deptInfoData(cursor)
    params = {
        "dept_info" : dept_info
    }
    return render_template("all_dept.html", **params)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#編集する社員の情報を取得
def getAddDeptInfo():
    add = "新規作成"
    dept_name = request.form.get("dept_name", "")
    return add, dept_name


#値を集約
def correctAddDeptValue(add, judge, result, dept_info):
    params = {
        "add" : add,
        "judge" : judge,
        "result" : result,
        "dept_info" : dept_info
    }
    return params


#新規追加URL(部品を集めて実行する)
@app.route("/dept/add", methods=["POST"])
def addNewDept():
    add, dept_name = getAddDeptInfo()
    cursor, cnx = db.connectDatabase()
    dept_info = db.deptInfoData(cursor)
    dept_add = db.setAddDeptQuery(dept_name)
    judge, result = db.exeAddDeptQuery(cursor, cnx, dept_name, dept_add)
    params = correctAddDeptValue(add, judge, result, dept_info)
    return render_template("dept_add.html", **params)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#編集する部署の情報を取得
def getChangeDeptInfo():
    dept_name = request.form.get("dept_name", "")
    change_info = request.form.get("change_info", "")
    return dept_name, change_info


#値を集約
def correctEditDeptValue(judge, result, change_info, dept_name):
    params = {
        "judge" : judge,
        "result" : result,
        "change_info" : change_info,
        "dept_name" : dept_name
    }
    return params


#編集のURL(部品を集めて実行する)
@app.route("/dept/edit", methods=["POST"])
def editDept():
    dept_name, change_info = getChangeDeptInfo()
    cursor, cnx = db.connectDatabase()
    dept_info = db.deptInfoData(cursor)
    dept_update = db.setEditDeptQuery(change_info, dept_name)
    judge, result = db.exeEditDeptQuery(cursor, cnx, change_info, dept_name, dept_update)
    params = correctEditDeptValue(judge, result, change_info, dept_name)
    return render_template("dept_add.html", **params)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#削除する部署の情報取得
def getDeleteDeptInfo():
    delete_info = request.form.get("delete_info", "")
    dept_name = request.form.get("dept_name", "")
    return delete_info, dept_name


#値を集約
def correctDeleteDeptValue(dept_info, message):
    params = {
        "dept_info" : dept_info,
        "message" : message
    }
    return params


#削除のURL(部品を集めて実行する)
@app.route("/dept/delete", methods=["POST"])
def deleteDept():
    delete_info, dept_name = getDeleteDeptInfo()
    cursor, cnx = db.connectDatabase()
    dept_info = db.deptInfoData(cursor)
    dept_delete = db.setDeleteDeptQuery(delete_info)
    exist_info = db.comformDeleteInfo(dept_info, delete_info)
    message, dept_info = db.exeDeleteDeptQuery(cursor, cnx, delete_info, dept_name, dept_delete, exist_info, dept_info)
    params = correctDeleteDeptValue(dept_info, message)
    return render_template("all_dept.html", **params)
