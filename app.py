from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class KSP_Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planetName = db.Column(db.String(100))

db.create_all()



@app.get("/", strict_slashes=False)
def home():
    return "Welcome to the KSP CommNet Backend!\nThis is where the fancy stuff happens."

@app.route("/planets", strict_slashes=False)
def allPlanets():
    planetList = db.session.query(KSP_Planet).all()
    return planetList

@app.errorhandler(404)
def invalidRequest(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def invalidRequest(e):
    return "Internal server error", 500