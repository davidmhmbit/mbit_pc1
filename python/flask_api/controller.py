from . import models


def post_image(data, min_confidence):

    # Subimos imagen a Imagekit para obtener url y tamaño
    image_url,image_size, image_id = models.generate_url(data)

    # Con la url obtenemos los tags de Imagga que tiene una confianza mínima
    tags = models.generate_tags(image_url, min_confidence)

    # guardamos la imagen en path del volumen docker
    path = models.save_image(data, image_id)

    # conectamos con la BBDD
    conn = models.connect_bbdd()

    # Guardamos la información en la BBDD
    creation_date = models.insert_bbdd_image(conn,image_id, path, image_size)
    
    for row in tags:
        tag = row["tag"]
        confidence = row["confidence"]
        models.insert_bbdd_tags(conn,tag, image_id, confidence, creation_date)

    # Borramos la imagen de Imagekit
    models.delete_url(image_id)

    return image_id, image_size, creation_date, tags

def agrupar_tags(lista_imagenes):

    # Recorremos la lista de imágenes para agrupar los tags de cada imagen
    resultado_agg=[]
    for row in lista_imagenes:
        posicion=0
        nueva=True
        for row_agg in resultado_agg:
            if row['id'] == row_agg['id']:
                resultado_agg[posicion]['tags'].append({'tag':row['tag'],'confidence':row['confidence']})
                nueva=False
                continue
            posicion+=1
        if nueva==True:
            resultado_agg.append({
                'id':row['id'],
                'size': row['size'],
                'date': str(row['date']),
                'tags':[{'tag':row['tag'],'confidence':row['confidence']}]}
                )
    
    return resultado_agg
    
def get_images(min_date, max_date,tags:str):

    # Obtenemos las imágenes que estan entre las diferentes fechas, paso tags y id vacios para que traiga todos
    resultado = models.select_images(min_date, max_date,"","")

    # Agregamos las tags de cada imagen
    resultado_agg = agrupar_tags(resultado)

    # Si se han propocionado tags, filtramos solo las imágenes que tienen todas las tags proporcionadas
    resultado_tags_matched=[]
    if tags != "":
        lista_tags=list(tags.split(','))
        for row in resultado_agg:
            numero_tags=0
            for tag in lista_tags:
                for tag_row in row['tags']:
                    if tag == tag_row['tag']:
                        numero_tags+=1
            if numero_tags==len(lista_tags):
                resultado_tags_matched.append(row)
        # Al haber recibido tags se pasa la lista de las imagenes que tiene todos los tags
        resultado_agg=resultado_tags_matched

    
    return resultado_agg

def get_download_image(image_id):
    
    # Obtengo las imágenes que estan entre las diferentes fechas
    resultado = models.select_images("","","",image_id)
    
    # Agrupo los tags de la imagen a descargar
    resultado_download = agrupar_tags(resultado)[0]
    
    # añado el data al json
    data = models.load_image(resultado[0]["path"])
    resultado_download['data']=data

    return resultado_download

def get_tags(min_date, max_date):
    
    # Obtengo las imágenes que cumplen las condiciones
    resultado = models.select_tags(min_date, max_date)

    # Lo transformo para formato json
    resultado_json=[]
    for row in resultado:
        resultado_json.append({'tag': row[0],'n_images':row[1],'min_confidence':row[2],'max_confidence':row[3],'avg_confidence':row[4]})

    return resultado_json
