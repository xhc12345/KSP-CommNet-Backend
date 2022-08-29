import os
import glob
from pathlib import Path
import yaml
import csv
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

def getProjectRoot() -> Path:
    return str(Path(__file__).parent)

def loadConfig():
    with open("config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            print(exc)

print("=== loading yaml config")
config = loadConfig()
print("=== done with yaml")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class KSP_CelestialBody(db.Model):
    __tablename__ = 'KSP_CelestialBody'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), index=True, unique=True)
    mass = db.Column(db.Integer, index=True)
    radius = db.Column(db.Integer, index=True)

def loadCelestialBodyData():
    fileName = config['data']['celestialBodies']['fileName']
    fileExtension = config['data']['celestialBodies']['fileExtension']
    fullFile = fileName+'.'+fileExtension
    dataFile = getProjectRoot()+'\\'+config['data']['path']+'\\'+fullFile
    print('==== loading up file at: '+dataFile)
    fields = []
    with open(dataFile, 'r') as csvFile:
        csvReader = csv.reader(csvFile)
        fields = next(csvReader)
        for row in csvReader:
            db.session.add(KSP_CelestialBody(name=row[0], mass=row[1], radius=row[2]))
    db.session.commit()
    print('==== finished feeding db with file data')

@event.listens_for(KSP_CelestialBody.__table__, 'after_create')
def db_init_planets(*args, **kwargs):
    print("### Initializing database table ###")
    loadCelestialBodyData()
    print("### Finished populating database ###")

db.create_all()


@app.get("/", strict_slashes=False)
def home():
    return "Welcome to the KSP CommNet Backend!\nThis is where the fancy stuff happens."

@app.route("/planets", strict_slashes=False)
def allPlanets():
    planetsQuery = db.session.query(KSP_CelestialBody).all()
    planetList = []
    for planet in planetsQuery:
        planetList.append({ 'name':     planet.name,
                            'mass':     planet.mass,
                            'radius':   planet.radius})
    return planetList

@app.route('/image/', strict_slashes=False)
def get_image_none():
    return "no image for you today lol"

@app.route('/image/<imageName>', strict_slashes=False)
def get_image(imageName):
    imgFolder = getProjectRoot() + "\\assets\img\\"
    filePath = imgFolder+imageName
    print('requesting '+filePath)
    for infile in glob.glob( os.path.join(imgFolder, imageName+'.*') ):
        return send_file(infile, mimetype='image/gif')

@app.route('/planet/<planetName>', strict_slashes=False)
def get_planet(planetName):
    # TODO: check if planet is in db, return all data for this planet
    pass

@app.errorhandler(404)
def invalidRequest(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def invalidRequest(e):
    return "Internal server error", 500