from flask import Flask, render_template, request, make_response, session, flash, redirect, url_for
import re
import mysql.connector
from mysql.connector import errorcode
from model.const import DB
from model.item import EMP, DEPT, EMP_ALL, EMP_COUNT


#データベースに接続
def connectDatabase():
    cnx= mysql.connector.connect(
                    user=DB["DB_USER_NAME"],
                    password=DB["DB_PASSWORD"],
                    host=DB["DB_HOST"],
                    database=DB["DB_NAME"])
    cursor = cnx.cursor()
    return cursor, cnx


#従業員データを取得し、配列に代入する
def tableDataStorage():
    cursor, cnx = connectDatabase()

    query = "SELECT emp_id, emp_name, dept_name, image_id FROM emp_info_table as eit JOIN dept_table as dt ON eit.dept_id = dt.dept_id ORDER BY emp_id;"
    cursor.execute(query)

    emp_info = []
    for (id, name, dept, image_id) in cursor:
        item = EMP(id, name, dept, image_id)
        emp_info.append(item)

    return emp_info


#部署情報
def deptInfoData(cursor):
    query = "SELECT dept_id, dept_name FROM dept_table ORDER BY dept_id;"
    cursor.execute(query)

    dept_info = []
    for (id, name) in cursor:
        item = DEPT(id, name)
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
        item = EMP_ALL(id, name, age, sex, image_id, post, pref, address, dept, join, retire, image)
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
        item = EMP_COUNT(id, name, dept)
        emp_info.append(item)
        emp_count += 1

    return emp_info, emp_count


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


#従業員データを取得し、配列に代入する
"""
def tableData():
    cursor, cnx = connectDatabase()

    query = "SELECT emp_id, emp_name, dept_name, image_id FROM emp_info_table as eit JOIN dept_table as dt ON eit.dept_id = dt.dept_id ORDER BY emp_id;"
    cursor.execute(query)

    emp_info = []
    for (id, name, dept, image_id) in cursor:
        item = {"id" : id, "name" : name, "dept" : dept, "image_id": image_id}
        emp_info.append(item)

    return emp_info
"""

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



#更新用のクエリを保管
def setEditDeptQuery(change_info, dept_name):
    dept_update = f'UPDATE dept_table SET dept_name = "{dept_name}" WHERE dept_id = {change_info}'

    return dept_update


#情報削除用のクエリ
def setDeleteEmpQuery(delete_info):
    info_delete = f'DELETE FROM emp_info_table WHERE image_id = "{delete_info}"'
    img_delete = f'DELETE FROM emp_img_table WHERE image_id = "{delete_info}"'

    return info_delete, img_delete


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
