FROM python:3.11

COPY ./resources/requirements/requirements.txt /home/resources/requirements/

# Rellenar con las credenciales personales de cada uno en el fichero credentiasl.json
COPY ./resources/credentials/credentials.json /home/resources/credentials/

COPY ./flask_api /home/flask_api/

RUN pip install --upgrade pip
RUN pip install -r /home/resources/requirements/requirements.txt


WORKDIR /home
###################################################
# AÑADIR LEVANTAR APP CON WAITRESS EN EL PUERTO 80
###################################################
EXPOSE 80

CMD ["waitress-serve", "--port=80", "--call", "flask_api:create_app"]