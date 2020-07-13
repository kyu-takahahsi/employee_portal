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

#データベース接続の鍵
host = 'localhost' # データベースのホスト名又はIPアドレス
username = 'root'  # MySQLのユーザ名
passwd   = 'kaA1ybB2ucC3d2c'    # MySQLのパスワード
dbname   = 'mydb'    # データベース名

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
#データベースに接続
def connectDatabase():
    cnx = mysql.connector.connect(host=host, user=username, password=passwd, database=dbname)
    cursor = cnx.cursor()

    return cursor, cnx


#従業員データを取得し、配列に代入する
def tableDataStorage():
    cursor, cnx = connectDatabase()

    query = "SELECT emp_id, emp_name, dept_name, image_id FROM emp_info_table as eit JOIN dept_table as dt ON eit.dept_id = dt.dept_id ORDER BY emp_id;"
    cursor.execute(query)

    emp_info = []
    for (id, name, dept, image_id) in cursor:
        item = {"id" : id, "name" : name, "dept" : dept, "image_id": image_id}
        emp_info.append(item)

    return emp_info


#ホーム画面
@app.route("/", methods=['GET', 'POST'])
def employeeList():
    emp_info = tableDataStorage()

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


#部署セレクター
def deptInfoData(cursor):
    query = "SELECT dept_id, dept_name FROM dept_table ORDER BY dept_id;"
    cursor.execute(query)

    dept_info = []
    for (id, name) in cursor:
        item = {"id" : id, "name" : name}
        dept_info.append(item)

    return dept_info


#新規追加クエリを保管
def setAddEmpQuery(emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image):
    if retire_date == "":
        info_add = f'INSERT INTO emp_info_table (emp_name, age, sex, image_id, post_code, pref, address, dept_id, join_date, retire_date) \
                    VALUES ("{emp_name}", {emp_age}, "{emp_sex}", "{image_id}", "{emp_postal}", "{emp_pref}", "{emp_address}", {emp_dept}, "{join_date}", "在籍")'
        img_add = f'INSERT INTO emp_img_table (image_id, emp_image) VALUES ("{image_id}", "{add_emp_image}")'
    else:
        info_add = f'INSERT INTO emp_info_table (emp_name, age, sex, image_id, post_code, pref, address, dept_id, join_date, retire_date) \
                    VALUES ("{emp_name}", {emp_age}, "{emp_sex}", "{image_id}", "{emp_postal}", "{emp_pref}", "{emp_address}", {emp_dept}, "{join_date}", "{retire_date}")'
        img_add = f'INSERT INTO emp_img_table (image_id, emp_image) VALUES ("{image_id}", "{add_emp_image}")'

    return info_add, img_add


#設定のボタンが押された場合
def exeAddEmpQuery(cursor, cnx,  emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image, emp_image, info_add, img_add):
    judge = ""
    result = ""

    if "setting" in request.form.keys():
        #値が入力されておらず空欄のまま
        if emp_name == "" or emp_age == "" or emp_sex == "" or emp_postal == "" or emp_pref == "" or emp_address == "" or emp_image == "" or emp_dept == "" or join_date == "":
            judge = "＊失敗：全ての項目を入力してください"
            result = "false"
        #年齢が数字以外で入力されている
        elif not emp_age.isdecimal():
            judge = "＊失敗：年齢は半角数字で入力してください"
            result = "false"
        #郵便番号が数字以外で入力されている
        elif not re.match(r"[0-9]{3}-?[0-9]{4}", emp_postal):
            judge = "＊失敗：郵便番号は半角数字で入力してください"
            result = "false"
        #名前の間に半角で空欄が入ってない
        elif not re.search(r"[ ]", emp_name):
            judge = "＊失敗：名前と苗字の間に半角で空欄を入力してください"
            result = "false"
        #条件通りなので新規追加
        else:
            cursor.execute(info_add)
            cursor.execute(img_add)
            cnx.commit()
            judge = "＊成功：データベースの追加が行われました"
            result = "success"

    return judge, result


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
    cursor, cnx = connectDatabase()

    #部署名セレクターのためのリスト
    dept_info = deptInfoData(cursor)

    #クエリの取得
    info_add, img_add = setAddEmpQuery(emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image)

    #クエリ実行するかの判定、結果
    judge, result = exeAddEmpQuery(cursor, cnx,  emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image, emp_image, info_add, img_add)

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


#編集する社員の情報を取得し、変数やリストへ格納
def getEditEmpinfo(cursor, change_info):
    #常時実行するSQL
    query = "SELECT info.emp_id as emp_id, emp_name, age, sex, info.image_id, post_code, pref, address, dept_id, join_date, retire_date, emp_image \
            FROM emp_info_table as info JOIN emp_img_table as img ON info.image_id = img.image_id;"
    cursor.execute(query)

    #SQLで取得した値を格納(HTMLに送るためのリスト)
    edit_info = []
    dept_select = ""
    pref_select = ""

    #社員ID、名前、年齢、性別、都道府県、住所、部署ID、入社日、退社日、画像
    for (id, name, age, sex, image_id, post, pref, address, dept, join, retire, image) in cursor:
        item = {"id" : id, "name" : name, "age" : age, "sex" : sex, "image_id" : image_id,"post" : post, "pref" : pref, "address" : address, "dept" : dept, "join" : join, "retire" : retire , "image" : image}
        if str(item["id"]) == change_info:
            edit_info.append(item)
            dept_select = item["dept"]
            pref_select = item["pref"]

    return edit_info, dept_select, pref_select


#更新用のクエリを保管
def setEditEmpQuery(change_info, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image):
    img_update = ""

    if  add_emp_image == "":
        info_update = f'UPDATE emp_info_table SET emp_name = "{emp_name}", age = {emp_age}, sex = "{emp_sex}", post_code = "{emp_postal}", pref = "{emp_pref}", address = "{emp_address}", dept_id = {emp_dept}, join_date = "{join_date}", retire_date = "{retire_date}" WHERE emp_id = {change_info}'
    else:
        info_update = f'UPDATE emp_info_table SET emp_name = "{emp_name}", age = {emp_age}, sex = "{emp_sex}", post_code = "{emp_postal}", pref = "{emp_pref}", address = "{emp_address}", dept_id = {emp_dept}, join_date = "{join_date}", retire_date = "{retire_date}" WHERE emp_id = {change_info}'
        img_update = f'UPDATE emp_img_table SET emp_image = "{add_emp_image}" WHERE image_id = "{image_id}"'

    return info_update, img_update



#設定のボタンが押された場合
def exeEditQuery(cursor, cnx,  emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image, emp_image, info_update, img_update):
    judge = ""
    result = ""

    if "setting" in request.form.keys():
        #値が入力されておらず空欄のまま
        if emp_name == "" or emp_age == "" or emp_sex == "" or emp_postal == "" or emp_pref == "" or emp_address == "" or emp_dept == "" or join_date == "" or retire_date == "":
            judge = "＊失敗：データベースの変更ができませんでした"
            result = "fales"
        #年齢が数字以外で入力されている
        elif not emp_age.isdecimal():
            judge = "＊失敗：年齢は半角数字で入力してください"
            result = "false"
        #郵便番号が数字以外で入力されている
        elif not re.match(r"[0-9]{3}-?[0-9]{4}", emp_postal):
            judge = "＊失敗：郵便番号は半角数字で入力してください"
            result = "false"
        #名前の間に半角で空欄が入ってない
        elif not re.search(r"[ ]", emp_name):
            judge = "＊失敗：名前と苗字の間に半角で空欄を入力してください"
            result = "false"
        #条件通りなので情報変更(画像の変更なし)
        elif emp_image == "":
            cursor.execute(info_update)
            cnx.commit()
            judge = "＊成功：データベースの変更が行われました"
            result = "success"
        #条件通りなので情報変更(画像の変更あり)
        else:
            cursor.execute(info_update)
            cursor.execute(img_update)
            cnx.commit()
            judge = "＊成功：データベースの変更が行われました"
            result = "success"

    return judge, result


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
    cursor, cnx = connectDatabase()

    #部署名セレクターのためのリスト
    dept_info = deptInfoData(cursor)

    #編集を押した従業員のIDと都道府県を格納
    edit_info, dept_select, pref_select = getEditEmpinfo(cursor, change_info)

    #クエリの取得
    info_update, img_update = setEditEmpQuery(change_info, emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image)

    #クエリ実行するかの判定、結果
    judge, result = exeEditQuery(cursor, cnx,  emp_name, emp_age, emp_sex, emp_postal, emp_pref, emp_address, emp_dept, join_date, retire_date, image_id, add_emp_image, emp_image, info_update, img_update)

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


#社員情報のSQL
def setSearchQuery(search_dept, search_emp_id, search_name):
    query = f'SELECT emp_id, emp_name, dept_name \
            FROM emp_info_table as eit JOIN dept_table as dt ON eit.dept_id = dt.dept_id \
            WHERE emp_id IS NOT NULL '
    #もし検索条件があれば条件を加えていく
    if search_dept != "" or search_emp_id != "" or search_name != "":
        if search_dept != "":
            query += f'AND dt.dept_id = {search_dept} '
        if search_emp_id != "":
            query += f'AND emp_id = {search_emp_id} '
        if search_name != "":
            query += f'AND emp_name LIKE "%{search_name}%" '
    query += 'ORDER BY emp_id'

    return query


#SQLの結果をリストに格納
def exeSearchEmpQuery(cursor, query):
    emp_count = 0
    #どんな時でも実行
    cursor.execute(query)

    #SQLで取得した値を格納(HTMLに送るためのリスト)
    emp_info = []
    for (id, name, dept) in cursor:
        item = {"id" : id, "name" : name, "dept" : dept}
        emp_info.append(item)
        emp_count += 1

    return emp_info, emp_count


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
    cursor, cnx = connectDatabase()

    #部署名セレクターのためのリスト
    dept_info = deptInfoData(cursor)

    #クエリの取得
    query = setSearchQuery(search_dept, search_emp_id, search_name)

    #クエリ実行するかの判定、結果
    emp_info, emp_count = exeSearchEmpQuery(cursor, query)

    #HTMLに送る全ての値をparamsに格納
    params = correctSearchEmpValue(search_name, search_emp_id, search_dept, dept_info, emp_info, emp_count)

    #HTMLへ変数を送る
    return render_template("emp_search.html", **params)


#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
#csv出力
def downloads(cursor):
    csv = "社員ID, 名前, 年齢, 性別, 郵便番号, 都道府県, 住所, 部署ID, 部署名, 入社日, 退社日, 画像ID, 画像パス\n"
    query = "SELECT info.emp_id as emp_id, emp_name, age, sex, post_code, pref, address, dt.dept_id, dt.dept_name, join_date, retire_date, info.image_id, emp_image \
            FROM emp_info_table as info JOIN emp_img_table as img ON info.image_id = img.image_id \
            JOIN dept_table as dt ON info.dept_id = dt.dept_id;"
    cursor.execute(query)
    for (id, name, age, sex, post, pref, address, dept_id, dept_name, join, retire, image_id, image) in cursor:
        csv += f"{id}, {name}, {age}, {sex}, {post}, {pref}, {address}, {dept_id}, {dept_name}, {join}, {retire}, {image_id}, {image}\n"

    return csv


@app.route('/emp/output', methods=["GET", "POST"])
def outputCsv():
    cursor, cnx = connectDatabase()
    csv = downloads(cursor)
    response = make_response(csv)
    response.headers["Content-Disposition"] = f"attachment; filename=employee_information.csv"

    return response


#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#削除する社員の情報取得
def getDeleteEmpInfo():
    delete_info = request.form.get("delete_info", "")
    emp_name = request.form.get("emp_name", "")

    return delete_info, emp_name


#情報削除用のクエリ
def setDeleteEmpQuery(delete_info):
    info_delete = f'DELETE FROM emp_info_table WHERE image_id = "{delete_info}"'
    img_delete = f'DELETE FROM emp_img_table WHERE image_id = "{delete_info}"'

    return info_delete, img_delete


#従業員データを取得し、配列に代入する
def tableData():
    cursor, cnx = connectDatabase()

    query = "SELECT emp_id, emp_name, dept_name, image_id FROM emp_info_table as eit JOIN dept_table as dt ON eit.dept_id = dt.dept_id ORDER BY emp_id;"
    cursor.execute(query)

    emp_info = []
    for (id, name, dept, image_id) in cursor:
        item = {"id" : id, "name" : name, "dept" : dept, "image_id": image_id}
        emp_info.append(item)

    return emp_info


def comformDeleteEmpInfo(emp_info, delete_info):
    exist_info = ""
    for i in emp_info:
        if i["image_id"] == delete_info:
            exist_info = "in"
    return exist_info


#削除のクエリ
def exeDeleteEmpQuery(cursor, cnx, info_delete, img_delete, delete_info, emp_name, exist_info):
    message = ""

    if "delete_info" in request.form.keys() and exist_info != "":
        #削除ボタンが押された
        cursor.execute(info_delete)
        cursor.execute(img_delete)
        cnx.commit()
        message = "＊成功：" + emp_name + "をデータベースから削除しました"
    else:
        message = "＊失敗：" + emp_name + "という名前はデータベース上に情報がありません"
    emp_info = tableDataStorage()

    return message, emp_info


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
    cursor, cnx = connectDatabase()

    #部署名のためのリスト
    dept_info = deptInfoData(cursor)

    #クエリの取得
    info_delete, img_delete = setDeleteEmpQuery(delete_info)

    #社員情報のリスト
    emp_info = tableDataStorage()

    #情報が存在するかの確認
    exist_info = comformDeleteEmpInfo(emp_info, delete_info)

    #クエリ実行するかの判定、結果
    message, emp_info = exeDeleteEmpQuery(cursor, cnx, info_delete, img_delete, delete_info, emp_name, exist_info)

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
    cursor, cnx = connectDatabase()

    #部署データを取得
    dept_info = deptInfoData(cursor)

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


#設定のボタンが押された場合に実行するクエリ
def setAddDeptQuery(dept_name):
    dept_add = f"INSERT INTO dept_table (dept_name) VALUES ('{dept_name}')"

    return dept_add


#設定のボタンが押された場合に用意していたクエリを実行
def exeAddDeptQuery(cursor, cnx, dept_name, dept_add):
    result = ""
    judge = ""
    if "setting" in request.form.keys():
        #値が入力されておらず空欄のまま
        if dept_name == "" or not "部" in dept_name:
            judge = "＊失敗：部署名を入力してください"
            result = "false"
        #条件通りなので新規追加
        else:
            cursor.execute(dept_add)
            cnx.commit()
            judge = "＊成功：データベースの追加が行われました"
            result = "success"

    return judge, result


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
    cursor, cnx = connectDatabase()

    #部署データを取得
    dept_info = deptInfoData(cursor)

    #部署を追加するためのクエリ
    dept_add = setAddDeptQuery(dept_name)

    #条件による判定
    judge, result = exeAddDeptQuery(cursor, cnx, dept_name, dept_add)

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


#更新用のクエリを保管
def setEditDeptQuery(change_info, dept_name):
    dept_update = f'UPDATE dept_table SET dept_name = "{dept_name}" WHERE dept_id = {change_info}'

    return dept_update


#設定のボタンが押された場合
def exeEditDeptQuery(cursor, cnx, change_info, dept_name, dept_update):
    result = ""
    judge = ""
    if "setting" in request.form.keys() and change_info != "":
        if dept_name == "":
            judge = "＊失敗：データベースの変更ができませんでした"
            result = "fales"
        else:
            cursor.execute(dept_update)
            cnx.commit()
            judge = "＊成功：データベースの変更が行われました"
            result = "success"

    return judge, result


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
    cursor, cnx = connectDatabase()

    #部署データを取得
    dept_info = deptInfoData(cursor)

    #部署を更新するためのクエリ
    dept_update = setEditDeptQuery(change_info, dept_name)

    #条件による判定
    judge, result = exeEditDeptQuery(cursor, cnx, change_info, dept_name, dept_update)

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


#情報削除用のクエリ
def setDeleteDeptQuery(delete_info):
    dept_delete = f'DELETE FROM dept_table WHERE dept_id = {delete_info}'

    return dept_delete


#情報が存在するかの確認
def comformDeleteInfo(dept_info, delete_info):
    exist_info = ""
    for i in dept_info:
        if i["id"] == int(delete_info):
            exist_info = "in"
    return exist_info


#削除のクエリ
def exeDeleteDeptQuery(cursor, cnx, delete_info, dept_name, dept_delete, exist_info, dept_info):
    message = ""
    if "delete_info" in request.form.keys() and exist_info != "":
        cursor.execute(dept_delete)
        cnx.commit()
        message = "＊成功：" + dept_name + "をデータベースから削除しました"
    else:
        message = "＊失敗：" + dept_name + "という情報はデータベース上に情報がありません"
    dept_info = deptInfoData(cursor)

    return message, dept_info


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
    cursor, cnx = connectDatabase()

    #部署データを取得
    dept_info = deptInfoData(cursor)

    #部署を更新するためのクエリ
    dept_delete = setDeleteDeptQuery(delete_info)

    #情報が存在するかの確認
    exist_info = comformDeleteInfo(dept_info, delete_info)

    #条件による判定
    message, dept_info = exeDeleteDeptQuery(cursor, cnx, delete_info, dept_name, dept_delete, exist_info, dept_info)

    #値を集約
    params = correctDeleteDeptValue(dept_info, message)

    #HTMLへ変数を送る
    return render_template("all_dept.html", **params)
