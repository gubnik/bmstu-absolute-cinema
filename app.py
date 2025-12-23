import os
from flask import Flask, render_template
from markupsafe import Markup

from blueprints.translation.route import translation_bp
from blueprints.auth.route import auth_bp
from blueprints.menu.route import menu_bp
from blueprints.queries_menu.route import queries_menu_bp
from blueprints.films_search.route import films_search_bp
from blueprints.available_seats.route import available_seats_bp
from blueprints.halls_list.route import halls_list_bp
from blueprints.ticket_report.route import ticket_report_bp
from blueprints.ticket_cart.route import ticket_cart_bp
from dotenv import load_dotenv

from translation.ts_provider import JsonTranslationProvider
from translation.locale_holder import SessionLocaleHolder
from translation.translator import Translator

from typing import Self

class CinemaApp(Flask):
    def __init__(self: Self,
                 app_name: str,
                 translator: Translator,
                 **kwargs):
        super().__init__(import_name=app_name, **kwargs)
        self.translator = translator


def register_blueprints(app: CinemaApp):
    app.register_blueprint(translation_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(queries_menu_bp)
    app.register_blueprint(films_search_bp)
    app.register_blueprint(available_seats_bp)
    app.register_blueprint(halls_list_bp)
    app.register_blueprint(ticket_report_bp)
    app.register_blueprint(ticket_cart_bp)


def create_app() -> CinemaApp:
    load_dotenv(dotenv_path=".env", override=False)
    ts_path = os.getenv("LOCALE_DIR")

    ts_provider = JsonTranslationProvider(ts_path if ts_path is not None else "locales")
    locale_holder = SessionLocaleHolder()
    translator = Translator(ts_provider, locale_holder)

    app = CinemaApp(__name__, translator)
 
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('main_menu.html'), 404

    app.secret_key = os.getenv("SECRET_KEY", "secret_cinema_key")

    def t(key: str) -> str:
        val: str = app.translator.get_text(key)
        return Markup(val)

    app.jinja_env.globals["t"] = t

    def locales() -> list[str]:
        return list(set(app.translator.ts_provider.get_all_translations().keys()))

    app.jinja_env.globals["locales"] = locales

    app.jinja_env.globals["translator"] = app.translator

    register_blueprints(app)
    return app

