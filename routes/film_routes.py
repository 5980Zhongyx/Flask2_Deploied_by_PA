from flask import Blueprint, render_template
from models.film import Film

film_bp = Blueprint("film", __name__)

@film_bp.route("/")
def index():
    films = Film.query.limit(12).all()
    return render_template("index.html", films=films)
