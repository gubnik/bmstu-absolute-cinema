from flask import Flask, render_template

from blueprints.auth.route import auth_bp
from blueprints.menu.route import menu_bp
from blueprints.queries_menu.route import queries_menu_bp
from blueprints.films_search.route import films_search_bp
from blueprints.available_seats.route import available_seats_bp
from blueprints.halls_list.route import halls_list_bp
from blueprints.ticket_report.route import ticket_report_bp
from blueprints.ticket_cart.route import ticket_cart_bp
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=False)

app = Flask(__name__)
app.secret_key = 'secret_cinema_key'

app.register_blueprint(menu_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(queries_menu_bp)
app.register_blueprint(films_search_bp)
app.register_blueprint(available_seats_bp)
app.register_blueprint(halls_list_bp)
app.register_blueprint(ticket_report_bp)
app.register_blueprint(ticket_cart_bp)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('main_menu.html'), 404

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=6969, debug=True)
