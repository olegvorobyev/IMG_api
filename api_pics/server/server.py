import click
from flask import Flask, request
from flask.cli import with_appcontext
from flask_restful import Api, Resource, reqparse
import psycopg2
import os

app = Flask(__name__)
api = Api(app)

db_host="localhost"
db_database="api_db"
db_user="postgres"
db_password="qwerty"

class ImageApi(Resource):

    def get_by_id(id):

        sql_string = "SELECT img_name,img FROM images WHERE img_id = {};".format(id)

        conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
        cur = conn.cursor()
        cur.execute(sql_string)
        res_name, res_img = cur.fetchone()
        cur.close()
        conn.close()

        return res_name, res_img

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("img_id")
        parser.add_argument("img_path")
        parser.add_argument("tags")
        params = parser.parse_args()

        img_name = os.path.basename(params["img_path"])
        img_binary = psycopg2.Binary(open(params["img_path"],'rb').read())

        sql_string = "UPDATE images SET img_name = \'{}\', img = {} WHERE img_id = {};".format(img_name,img_binary,params["img_id"])

        conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
        cur = conn.cursor()
        cur.execute(sql_string)
        conn.commit()
        cur.close()
        conn.close()

        return 201

    def put(self):
        parser = reqparse.RequestParser()

        parser.add_argument("img_path")
        parser.add_argument("tags",action = "append")
        params = parser.parse_args()

        img_name = os.path.basename(params["img_path"])
        img_binary = psycopg2.Binary(open(params["img_path"],'rb').read())

        sql_string = "INSERT INTO images (img_name,img) VALUES(\'{}\',{});".format(img_name,img_binary)

        conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
        cur = conn.cursor()
        cur.execute(sql_string)
        conn.commit()

        sql_string = "SELECT MAX(img_id) FROM images"
        cur.execute(sql_string)
        max_id = cur.fetchone()

        cur.close()
        conn.close()

        for tag in params["tags"]:
            self.add_tag_to_image(int(max_id[0]),tag)

        return 201

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument("img_id")
        params = parser.parse_args()

        conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
        cur = conn.cursor()
        sql_string = "DELETE FROM images WHERE img_id = {};".format(params["img_id"])
        cur.execute(sql_string)


        tags_list = []
        sql_string = "SELECT tag FROM tags;"
        cur.execute(sql_string)
        sql_result = cur.fetchone()
        while sql_result:
            tags_list.append(sql_result)
            sql_result = cur.fetchone()

        for cur_tag in tags_list:
            sql_string = "UPDATE tags SET pictures_id = array_remove(pictures_id,{}) WHERE tag = \'{}\';".format(params["img_id"],cur_tag[0])
            cur.execute(sql_string)

        conn.commit()
        cur.close()
        conn.close()
        return 200

    def add_tag_to_image(self,id,tag_name):
        conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
        cur = conn.cursor()

        sql_string = "SELECT EXISTS(SELECT 1 FROM  tags WHERE tag = \'{}\');".format(tag_name)
        cur.execute(sql_string)
        res = cur.fetchone()
        if res[0]==True:
            sql_string = "UPDATE tags SET pictures_id = array_append(pictures_id,{}) WHERE tag = \'{}\';".format(id,tag_name)
            cur.execute(sql_string)
        else:
            sql_string = "INSERT INTO tags (tag,pictures_id) VALUES (\'"+tag_name+"\',\'{"+str(id)+"}\');"
            cur.execute(sql_string)

        conn.commit()
        cur.close()
        conn.close()

    def delete_tag_from_image(self,id,tag_name):
        conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
        cur = conn.cursor()
        sql_string = "UPDATE tags SET pictures_id = array_remove(pictures_id,{}) WHERE tag = \'{}\';".format(id, tag_name)
        cur.execute(sql_string)
        conn.commit()
        cur.close()
        conn.close()

    def get_all_tags_to_image(self,id):

        result_list = []
        sql_string = "SELECT tag FROM tags WHERE \'{}\'=ANY(pictures_id);".format(id)

        conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
        cur = conn.cursor()
        cur.execute(sql_string)
        sql_result = cur.fetchone()
        while sql_result:
            result_list.append(sql_result[0])
            sql_result = cur.fetchone()
        cur.close()
        conn.close()

        return result_list

@app.route('/image-api/download_by_id', methods=['GET', 'POST'])
def download_by_id():
    parser = reqparse.RequestParser()
    parser.add_argument("img_id")
    parser.add_argument("save_path")
    params = parser.parse_args()

    img_name,img = ImageApi.get_by_id(params["img_id"])

    with open(params["save_path"]+"/"+img_name, 'wb') as f:
        f.write(img)

    return '',200

@app.route('/image-api/get_all_images_list', methods=['GET', 'POST'])
def get_all_images_list():

    result_list = []
    sql_string = "SELECT img_id,img_name FROM images;"

    conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
    cur = conn.cursor()
    cur.execute(sql_string)
    sql_result = cur.fetchone()
    while sql_result:
        img = {
            "id": sql_result[0],
            "name": sql_result[1]
            }
        result_list.append(img)
        sql_result = cur.fetchone()
    cur.close()
    conn.close()

    for e in result_list:
        tags_list = ImageApi.get_all_tags_to_image(ImageApi(),e["id"])
        e.update({"tags": tags_list})

    return ''.join(str(e) for e in result_list),200

@app.route('/image-api/add_tag_to_image', methods=['GET', 'POST'])
def add_tag_to_image():
    parser = reqparse.RequestParser()
    parser.add_argument("img_id")
    parser.add_argument("tag")
    params = parser.parse_args()

    ImageApi.add_tag_to_image(ImageApi(),params["img_id"],params["tag"])

    return '',200

@app.route('/image-api/delete_tag_from_image', methods=['GET', 'POST'])
def delete_tag_from_image():
    parser = reqparse.RequestParser()
    parser.add_argument("img_id")
    parser.add_argument("tag")
    params = parser.parse_args()

    ImageApi.delete_tag_from_image(ImageApi(),params["img_id"],params["tag"])

    return '',200

@app.route('/image-api/filter_by_tags', methods=['GET', 'POST'])
def filter_by_tags():
    parser = reqparse.RequestParser()
    parser.add_argument("tags",action = "append")
    params = parser.parse_args()

    conn = psycopg2.connect(host=db_host, database=db_database, user=db_user, password=db_password)
    cur = conn.cursor()

    res_array = []
    sql_string = "SELECT img_id FROM images;"
    cur.execute(sql_string)
    sql_result = cur.fetchone()
    while sql_result:
        res_array.append(sql_result[0])
        sql_result = cur.fetchone()

    for tag in params["tags"]:
        sql_string = "SELECT pictures_id FROM tags WHERE tag = \'{}\';".format(tag)
        cur.execute(sql_string)
        sql_result = cur.fetchone()[0]
        res_array = list(set(res_array) & set(sql_result))


    return ''.join(str(e)+" " for e in res_array),200

api.add_resource(ImageApi,"/image-api", "/image-api/")

if __name__ == '__main__':
    app.run(debug=True)
