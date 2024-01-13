from flask import Blueprint, request, make_response
from . import controller
import json

# Definimos los Blueprints
bp_image_post = Blueprint('image_post', __name__, url_prefix='/')
bp_images_get = Blueprint('images_get', __name__, url_prefix='/')
bp_download_image_get = Blueprint('download_image_get', __name__, url_prefix='/')
bp_tags_get = Blueprint('tags_get', __name__, url_prefix='/')


@bp_image_post.post("/add_image")
def post_image():

    # Comprobamos que venga en el body el campo data en el json
    if not "data" in request.json:
        return make_response({"description": "The body must contain 'data' with image in base64"}, 400)
    
    # recogemos si se ha indicado min_confidence como query parameters, y si no quedaría 80 por defecto
    min_confidence = float(request.args.get("min_confidence", "80"))

    # cargamos a variable la imagen en base64 que se ha pasado
    data = request.json.get("data")

    # generamos url, obtenemos tags, guardamos en volumen, insertamos en bbdd y borramos url
    image_id, image_size, creation_date, tags = controller.post_image(data, min_confidence)

    # creamos diccionario de respuesta
    response = {"id":image_id, "size": image_size, "date":str(creation_date), "tags":tags, "data":data}

    # convertimos en json
    response_json=json.dumps(response,indent=4)

    return response_json


@bp_images_get.get("/images")
def get_images():
    
    # Podría poner aquí el condicional para que si no se proporciona ninguna tag no devuelva nada
    '''if "tags" not in request.args:
    return make_response({"cause":"You must include query params 'tags'"})'''
    

    # Se decide que si no indica tags también sera válido, y devolverá imágenes sin mirar tags 
    # Si no viene ningún query params se devolverán todas
    tags = str(request.args.get("tags", "")) 
    # Compruebo si viene min_date y/o max_date
    min_date = str(request.args.get("min_date", ""))
    max_date = str(request.args.get("max_date", ""))

    # Llamamos a controller para obtener las imágenes en base a los filtros
    res = controller.get_images(min_date,max_date,tags)

    return res


@bp_download_image_get.get("/download_image/<id>")
def get_download_image(id):
    
    try:
        # Obtenemos el id del path params
        image_id = request.view_args['id']
        
        # Llamada a controller para obtener los datos de la imagen
        res = controller.get_download_image(image_id)

    except:
        return make_response({"cause": "Must define some path params <id> for download the image"})
    
    return res


@bp_tags_get.get("/tags")
def get_tags():
    
    # Se recogen los query params, si no se pasan, se recuperaran todos los tags
    min_date = str(request.args.get("min_date", ""))
    max_date = str(request.args.get("max_date", ""))

    # Llamamos a controller para obtener los tags
    res = controller.get_tags(min_date,max_date)

    return res

