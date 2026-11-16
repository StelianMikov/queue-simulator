from flask import Flask

from app.controllers.pages import pages
from app.views import formatting


def create_app():
    app = Flask(__name__)
    app.register_blueprint(pages)
    app.add_template_filter(formatting.minutes)
    app.add_template_filter(formatting.percent)
    app.add_template_filter(formatting.plain_number)
    return app
