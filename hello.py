import os
import os.path

from flask import Flask, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


db_file_abspath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data.sqlite")

app = Flask(__name__)

app.config["SECRET_KEY"] = "44zgw&8v(M*L92{/,22)F"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file_abspath}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["FLASK_MAIL_SUBJECT_PREFIX"] = "[Flasky] "
app.config["FLASK_MAIL_SENDER"] = "Flasky Admin <admin@flasky.com>"
app.config["FLASKY_ADMIN"] = os.environ.get("FLASKY_ADMIN")

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __repr__(self):
        return f"<Role {self.name}>"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def __repr__(self):
        return f"<User {self.username}>"


class NameForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


def send_mail(to, subject, template, **kwargs):
    msg = Message(
        app.config["FLASK_MAIL_SUBJECT_PREFIX"] + subject,
        sender=app.config["FLASK_MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)


@app.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        session["known"] = True
        if not user:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session["known"] = False
            if app.config["FLASKY_ADMIN"]:
                send_mail(
                    to=app.config["FLASKY_ADMIN"],
                    subject="New User",
                    template="mail/new_user",
                    user=user,
                )
        session["name"] = form.name.data
        return redirect(url_for("index"))
    return render_template(
        "index.html", form=form, name=session.get("name"), known=session.get("known")
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User)
