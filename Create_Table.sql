--社員情報テーブル：社員ID、名前、年齢、性別、写真ID、郵便番号、都道府県、住所、部署ID、入社日、退社日、更新日
CREATE TABLE emp_info_table(
    --emp_id INT AUTO_INCREMENT,
    emp_name VARCHAR(100),
    age INT(100),
    sex VARCHAR(100),
    image_id VARCHAR(100),
    post_code VARCHAR(100),
    pref VARCHAR(100),
    address VARCHAR(100),
    dept_id INT(100),
    join_date VARCHAR(100),
    retire_date VARCHAR(100),
    --update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (emp_id)
);


--社員画像テーブル：写真ID、画像パス、更新日
CREATE TABLE emp_img_table(
    image_id VARCHAR(100),
    emp_image VARCHAR(100),
    --update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


--部署情報テーブル：部署ID、部署名、作成日、更新日
CREATE TABLE dept_table(
    --dept_id INT AUTO_INCREMENT,
    dept_name VARCHAR(100),
    --edit_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    --update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (dept_id)
);

--CSV出力用
SELECT info.emp_id as emp_id, emp_name, age, sex, info.image_id, post_code, pref, address, dt.dept_id, dt.dept_name, join_date, retire_date, emp_image FROM emp_info_table as info JOIN emp_img_table as img ON info.image_id = img.image_i JOIN dept_table as dt 
ON info.dept_id = dt.dept_id;

--社員情報閲覧用
SELECT emp_id, emp_name, age, sex, image_id post_code, pref, dept_id, join_date, retire_date, update_date FROM emp_info_table;