from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # importamos views y registramos los Blueprints
    from . import views
    app.register_blueprint(views.bp_image_post)
    app.register_blueprint(views.bp_images_get)
    app.register_blueprint(views.bp_download_image_get)
    app.register_blueprint(views.bp_tags_get)

    return app
