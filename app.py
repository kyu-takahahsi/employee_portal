#Flask関係
from flask import Flask, render_template, request, make_response, session, flash, redirect, url_for
app = Flask(__name__)
#データベース操作
import mysql.connector
from mysql.connector import errorcode
#正規表現
import re
#時間取得
import datetime
#画像保存のため
import os
#画像保存のため
from werkzeug.utils import secure_filename
#ランダム選択
import random
#ランダムな文字列作成
import string
#21章
#画像のためのパスや定義
UPLOAD_FOLDER = './static/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#MVC
import model.database as db
from model.item import EMP, DEPT

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
    #値の取得
    add, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, emp_image = getEmpInfo()

    #画像にパスを通す
    add_emp_image, emp_image = imageSetVariable(emp_image)

    #データベースに接続
    cursor, cnx = db.connectDatabase()

    #部署名セレクターのためのリスト
    dept_info = db.deptInfoData(cursor)

    #クエリの取得
    info_add, img_add = db.setAddEmpQuery(emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image)

    #クエリ実行するかの判定、結果
    judge, result = db.exeAddEmpQuery(cursor, cnx,  emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image, emp_image, info_add, img_add)

    #HTMLに送る全ての値をparamsに格納
    params = correctAddEmpValue(add, judge, result, dept_info)

    #HTMLへ変数を送る
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
    join_date = request.form.get("retire_date", "")
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
    #値の取得
    change_info, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, emp_image = getChangeEmpInfo()

    #画像にパスを通す
    add_emp_image, emp_image = imageSetVariable(emp_image)

    #データベースに接続
    cursor, cnx = db.connectDatabase()

    #部署名セレクターのためのリスト
    dept_info = db.deptInfoData(cursor)

    #編集を押した従業員のIDと都道府県を格納
    edit_info, dept_select, pref_select = db.getEditEmpinfo(cursor, change_info)

    #クエリの取得
    info_update, img_update = db.setEditEmpQuery(change_info, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image)

    #クエリ実行するかの判定、結果
    judge, result = db.exeEditQuery(cursor, cnx,  emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image, emp_image, info_update, img_update)

    #HTMLに送る全ての値をparamsに格納
    params = correctEditValue(pref_select, dept_select, dept_info, edit_info, judge, result)

    #HTMLへ変数を送る
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
    #検索条件の値の取得
    search_dept, search_emp_id, search_name = getSearchEmpInfo()

    #データベースに接続
    cursor, cnx = db.connectDatabase()

    #部署名セレクターのためのリスト
    dept_info = db.deptInfoData(cursor)

    #クエリの取得
    query = db.setSearchQuery(search_dept, search_emp_id, search_name)

    #クエリ実行するかの判定、結果
    emp_info, emp_count = db.exeSearchEmpQuery(cursor, query)

    #HTMLに送る全ての値をparamsに格納
    params = correctSearchEmpValue(search_name, search_emp_id, search_dept, dept_info, emp_info, emp_count)

    #HTMLへ変数を送る
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
    #検索条件の値の取得
    delete_info, emp_name = getDeleteEmpInfo()

    #データベースに接続
    cursor, cnx = db.connectDatabase()

    #部署名のためのリスト
    dept_info = db.deptInfoData(cursor)

    #クエリの取得
    info_delete, img_delete = db.setDeleteEmpQuery(delete_info)

    #社員情報のリスト
    emp_info = db.tableDataStorage()

    #情報が存在するかの確認
    exist_info = db.comformDeleteEmpInfo(emp_info, delete_info)

    #クエリ実行するかの判定、結果
    message, emp_info = db.exeDeleteEmpQuery(cursor, cnx, info_delete, img_delete, delete_info, emp_name, exist_info)

    #HTMLに送る全ての値をparamsに格納
    params = correctDeleteEmpValue(emp_info, message)

    #HTMLへ変数を送る
    return render_template("all_emp.html", **params)


#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー


#部署画面
#ホーム画面
@app.route("/dept", methods=["GET", "POST"])
def deptList():
    #データベース接続
    cursor, cnx = db.connectDatabase()

    #部署データを取得
    dept_info = db.deptInfoData(cursor)

    #値の入った変数やリストをHTMLに渡すための変数に格納
    params = {
        "dept_info" : dept_info
    }

    #HTMLへ変数を送る
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
    #追加するための値取得
    add, dept_name = getAddDeptInfo()

    #データベース接続
    cursor, cnx = db.connectDatabase()

    #部署データを取得
    dept_info = db.deptInfoData(cursor)

    #部署を追加するためのクエリ
    dept_add = db.setAddDeptQuery(dept_name)

    #条件による判定
    judge, result = db.exeAddDeptQuery(cursor, cnx, dept_name, dept_add)

    #値を集約
    params = correctAddDeptValue(add, judge, result, dept_info)

    #HTMLへ変数を送る
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
    #追加するための値取得
    dept_name, change_info = getChangeDeptInfo()

    #データベース接続
    cursor, cnx = db.connectDatabase()

    #部署データを取得
    dept_info = db.deptInfoData(cursor)

    #部署を更新するためのクエリ
    dept_update = db.setEditDeptQuery(change_info, dept_name)

    #条件による判定
    judge, result = db.exeEditDeptQuery(cursor, cnx, change_info, dept_name, dept_update)

    #値を集約
    params = correctEditDeptValue(judge, result, change_info, dept_name)

    #HTMLへ変数を送る
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
    #追加するための値取得
    delete_info, dept_name = getDeleteDeptInfo()

    #データベース接続
    cursor, cnx = db.connectDatabase()

    #部署データを取得
    dept_info = db.deptInfoData(cursor)

    #部署を更新するためのクエリ
    dept_delete = db.setDeleteDeptQuery(delete_info)

    #情報が存在するかの確認
    exist_info = db.comformDeleteInfo(dept_info, delete_info)

    #条件による判定
    message, dept_info = db.exeDeleteDeptQuery(cursor, cnx, delete_info, dept_name, dept_delete, exist_info, dept_info)

    #値を集約
    params = correctDeleteDeptValue(dept_info, message)

    #HTMLへ変数を送る
    return render_template("all_dept.html", **params)
