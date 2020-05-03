from datetime import datetime

from flask import Flask, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config["SECRET_KEY"] = "44zgw&8v(M*L92{/,22)F"


@app.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session["name"] = form.name.data
        return redirect(url_for("index"))
    return render_template(
        "index.html", current_time=datetime.utcnow(), name=session.get("name"), form=form
    )


@app.route("/user/<name>")
def user(name: str):
    return render_template("user.html", name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("501.html"), 500
