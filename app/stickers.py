from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint("stickers", __name__)


@bp.route("/album")
@login_required
def album():
    return render_template("album.html")
