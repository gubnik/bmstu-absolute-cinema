from .app import create_app, CinemaApp

if __name__ == '__main__':
    app: CinemaApp = create_app()
    app.run(host="127.0.0.1", port=6969, debug=True)
