from imagekitio import ImageKit
import requests
import json
from sqlalchemy import create_engine, text
from flask import make_response

# Variables de models
path_images = "/home/resources/images/"
path_credentials = "/home/resources/credentials/"


def get_credentials(servicio:str):

    # Cargamos el fichero de credenciales proporcionado al docker
    with open(path_credentials+"credentials.json",'r') as f:
        credentials = json.load(f)

    # Filtramos solo las credenciales del servicio
    credentials_servicio=credentials[servicio]
    
    return credentials_servicio

def connect_imagekit():

    # Leemos fichero de credenciales obtenido al levantar el contenedor - credentials.json
    credentials = get_credentials("imagekit")
    
    # Conexión con ImageKit
    imagekit = ImageKit(
            private_key=credentials["private_key"],
            public_key=credentials["public_key"],
            url_endpoint=credentials["url_endpoint"]
            )
    
    return imagekit

def generate_url(data):
    try:
        # conexión a ImageKit 
        imagekit = connect_imagekit()
        
        # upload an image 
        upload_info = imagekit.upload(file=data, file_name='nombre_imagen_temporal')

        # la url para acceder a la imagen
        image_url = upload_info.url
        # el tamaño de la imagen
        image_size = upload_info.size
        # obtenemos el uuid para guardar la imagen
        image_id = upload_info.file_id
    
    except:
        return make_response({"description": "data must be an image converted to base64."}, 400)

    return image_url,image_size,image_id

def generate_tags(image_url,min_confidence):

    # Leemos credenciales de imagga proporcionadas
    credentials = get_credentials("imagga")

    # Conectamos a Imagga pasando las credenciales
    response = requests.get(f"https://api.imagga.com/v2/tags?image_url={image_url}", auth=(credentials["api_key"], credentials["api_secret"]))

    # Recuperamos solamente las tags que seam >= al min_confidence indicado
    tags = [
        {
            "tag": t["tag"]["en"],
            "confidence": t["confidence"]
        }
        for t in response.json()["result"]["tags"]
        if t["confidence"] >= min_confidence
    ]
        
    return tags

def delete_url(image_id):
     
     # conexión a ImageKit 
    imagekit = connect_imagekit()

    # Borramos la imagen 
    delete = imagekit.delete_file(file_id=image_id)

    return delete.response_metadata.http_status_code

def save_image(data, image_id):

    # Guardamos la imagen en la ruta de imágenes
    with open(path_images+image_id,'w') as f:
        f.write(data)

    return path_images+image_id

def load_image(path):

    # Cargo la imagen de la ruta de imágenes
    with open(path,'r') as f:
        data = f.read()

    return data

def connect_bbdd():
    
    # Variables para la conexión
    user="mbit"
    passw="mbit"
    server="mysql:3306"
    database="Pictures"

    # create sqlalchemy engine
    engine = create_engine(f"mysql+pymysql://{user}:{passw}@{server}/{database}")

    # conexión
    conn = engine.connect()

    return conn

def insert_bbdd_image(conexion_bbdd,id,path,size):
    
    # Obtenemos conexión bbdd
    conn = conexion_bbdd

    # Insertamos en tabla pictures
    conn.execute(text(f"INSERT INTO pictures (id,path,size) VALUES ('{id}','{path}','{size}')"))
    conn.commit()

    # Obtenemos la fecha de creación tras la inserción
    result = conn.execute(text(f"SELECT date FROM pictures WHERE id='{id}'")).fetchone()

    # Lo guardamos en variable para devolverlo
    creation_date=result[0]

    return creation_date
    
def insert_bbdd_tags(conexion_bbdd,tag, picture_id,confidence, creation_date):

    # Conectamos con la bbdd
    conn = conexion_bbdd

    # Insertamos en la tabla tags
    conn.execute(text(f"INSERT INTO tags (tag,picture_id,confidence,date) VALUES ('{tag}','{picture_id}',{confidence},'{creation_date}')"))
    conn.commit()

    return 1

def select_images(min_date, max_date, tags:str, image_id):

    # Vamos a conformar la condición where de la query en base a los query params pasados
    if (min_date!="" or max_date!="" or tags!="" or image_id!=""):
        filtro=" WHERE"
        if min_date!="":
            filtro = (filtro+" pictures.date>='"+min_date+"'")
            if (max_date!="" or tags!="" or image_id!=""):
                filtro = (filtro+" AND")
        if max_date != "":
            filtro = filtro+" pictures.date<='"+max_date+"'"
            if (tags!="" or image_id!=""):
                filtro = (filtro+" AND")
        if tags!="":
            tags_formatted = ("'" + tags.replace(",","','") + "'")
            filtro = (filtro+" tag IN ("+tags_formatted+")")
            if image_id!="":
                filtro = (filtro+" AND")
        if image_id!="":
            filtro = filtro+" id='"+image_id+"'"
    else:
        # Si no se proporcionara ningun filtro, devolvería todas las imagenes almacenadas
        filtro = ""

    # Query con los campos de la select y los joins, añadiendo el filtro antes calculado
    query=("SELECT id, size, pictures.date, tag, confidence, path FROM pictures LEFT JOIN tags ON pictures.id=tags.picture_id"+filtro)

    # Conexión con la bbdd
    conn = connect_bbdd()

    # Ejecutamos de la query
    result = conn.execute(text(query)).fetchall()

    # Convertimos en lista de diccionarios
    result_dict=[]
    for row in result:
        result_dict.append(
            {'id':row[0],
            'size':row[1],
            'date':row[2],
            'tag':row[3],
            'confidence':row[4],
            'path':row[5]}
            )

    return result_dict

def select_tags(min_date, max_date):

    #filtramos por min_date y/o max_date
    if (min_date!="" or max_date!=""):
        filtro=" WHERE"
        if min_date!="":
            filtro = (filtro+" tags.date>='"+min_date+"'")
            if (max_date!=""):
                filtro = (filtro+" AND")
        if max_date != "":
            filtro = filtro+" tags.date<='"+max_date+"'"
    
    # Creamos la query a ejecutar para selecionar las tags, agruparlas, contarlas y calcular max, min y avg de confidence
    query=("SELECT tag, count(tag), min(confidence), max(confidence), avg(confidence) FROM tags"+filtro+" GROUP BY tag")

    # Conectamos bbdd
    conn = connect_bbdd()

    # Ejecutamos query
    result = conn.execute(text(query)).fetchall()

    return result
