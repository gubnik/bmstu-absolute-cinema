from flask import Blueprint, current_app, request, redirect, url_for

translation_bp= Blueprint('translation_bp', __name__)

@translation_bp.route("/set-locale", methods=["POST"])
def set_locale():
    new_locale = request.form.get("locale")
    if new_locale:
        current_app.translator.change_locale(new_locale) # pyright: ignore
    return redirect(request.referrer or url_for("menu.index"))


