import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from models import db, Planets
from models import db, People
from models import db, Starships
from models import db, FavoriteCharacters
from models import db, FavoritePlanets
from models import db, FavoriteStarships
app = Flask(__name__)
app.url_map.strict_slashes = False
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_serialized_map = list(map(lambda x: x.serialize(), users))
    response_body = {
        "msg": "ok",
        "result": users_serialized_map
    }
    return jsonify(response_body), 200

@app.route('/users/favorites', methods=['GET'])
def favorites_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'user_id' not in body:
        return jsonify({'msg': 'El campo user_id es obligatorio'}), 400
    user = User.query.get(body['user_id'])
    if user is None:
        return jsonify({'msg': "El usuario con el id: {} no existe".format(body['user_id'])}), 404
    favorite_planets = db.session.query(FavoritePlanets, Planets).join(Planets).filter(FavoritePlanets.user_id == body['user_id']).all()
    favorite_characters = db.session.query(FavoriteCharacters, People).join(People).filter(FavoriteCharacters.user_id == body['user_id']).all()
    favorite_starships = db.session.query(FavoriteStarships, Starships).join(Starships).filter(FavoriteStarships.user_id == body['user_id']).all()
    favorite_planets_serialized = []
    for favorite_item, planet_item in favorite_planets:
        favorite_planets_serialized.append({'favorite_planet_id': favorite_item.id, 'planet': planet_item.serialize()})
    favorite_characters_serialized = []
    for favorite_item, character_item in favorite_characters:
        favorite_characters_serialized.append({'favorite_characters_id': favorite_item.id, 'character': character_item.serialize()})
    favorite_starships_serialized = []
    for favorite_item, starship_item in favorite_starships:
        favorite_starships_serialized.append({'favorite_starships_id': favorite_item.id, 'starship': starship_item.serialize()})
    return jsonify({'msg':'ok', 'results': {"naves_favoritas": favorite_starships_serialized, "personajes_favoritos": favorite_characters_serialized, "planetas_favoritos": favorite_planets_serialized}})

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    planets_serialized_map = list(map(lambda x: x.serialize(), planets))
    response_body = {
        "msg": "ok",
        "result": planets_serialized_map
    }
    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_serialized_map = list(map(lambda x: x.serialize(), people))
    response_body = {
        "msg": "ok",
        "result": people_serialized_map
    }
    return jsonify(response_body), 200

@app.route('/starships', methods=['GET'])
def get_starship():
    starships = Starships.query.all()
    starships_serialized_map = list(map(lambda x: x.serialize(), starships))
    response_body = {
        "msg": "ok",
        "result": starships_serialized_map
    }
    return jsonify(response_body), 200

@app.route('/planets/<int:id>', methods=['GET'])
def get_single_planets(id):
    planet = Planets.query.get(id)
    return jsonify({"msg": "ok", "planet": planet.serialize()}), 200

@app.route('/people/<int:id>', methods=['GET'])
def get_single_person(id):
    people = People.query.get(id)
    return jsonify({"msg": "ok", "people": people.serialize()}), 200

@app.route('/starships/<int:id>', methods=['GET'])
def get_single_starship(id):
    starships = Starships.query.get(id)
    return jsonify({"msg": "ok", "planet": starships.serialize()}), 200

@app.route('/planets', methods=['POST'])
def add_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify()
    if "name" not in body:
        return jsonify()
    new_planet = Planets()
    new_planet.name = body["name"]
    new_planet.population = body["population"]
    db.session.add(new_planet)
    db.session.commit()
    return jsonify("Planeta añadido"), 200

@app.route('/people', methods=['POST'])
def add_person():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify()
    if "name" not in body:
        return jsonify()
    new_person = People()
    new_person.name = body["name"]
    new_person.height = body["height"]
    new_person.mass = body["mass"]
    db.session.add(new_person)
    db.session.commit()
    return jsonify("Persona añadida"), 200

@app.route('/starships', methods=['POST'])
def add_starship():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify()
    if "name" not in body:
        return jsonify()
    new_starship = Starships()
    new_starship.name = body["name"]
    new_starship.model = body["model"]
    db.session.add(new_starship)
    db.session.commit()
    return jsonify("Nave añadida"), 200

@app.route('/planets/favorite/<int:id>', methods=['POST'])
def add_favorite_planet(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"message": "No se proporcionó ningún dato"}), 400
    if "user_id" not in body:
        return jsonify({"message": "Se requiere el ID del usuario"}), 400
    new_favorite_planet = FavoritePlanets(
        user_id = body["user_id"],
        planet_id = id
    )
    db.session.add(new_favorite_planet)
    db.session.commit()
    return jsonify({"message": "Planeta favorito añadido correctamente"}), 200

@app.route('/starships/favorite/<int:id>', methods=['POST'])
def add_favorite_starship(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"message": "No se proporcionó ningún dato"}), 400
    if "user_id" not in body:
        return jsonify({"message": "Se requiere el ID del usuario"}), 400
    new_favorite_starship = FavoriteStarships(
        user_id = body["user_id"],
        starship_id = id
    )
    db.session.add(new_favorite_starship)
    db.session.commit()
    return jsonify({"message": "Nave favorita añadida correctamente"}), 200

@app.route('/people/favorite/<int:id>', methods=['POST'])
def add_favorite_character(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"message": "No se proporcionó ningún dato"}), 400
    if "user_id" not in body:
        return jsonify({"message": "Se requiere el ID del usuario"}), 400
    new_favorite_character = FavoriteCharacters(
        user_id = body["user_id"],
        character_id = id
    )
    db.session.add(new_favorite_character)
    db.session.commit()
    return jsonify({"message": "Personaje favorito añadido correctamente"}), 200

@app.route('/planets/favorite/<int:id>', methods=['DELETE'])
def delete_favorite_planet(id):
    favorite_planet = FavoritePlanets.query.get(id)
    if not favorite_planet:
        return jsonify({"message": "Planeta favorito no encontrado"}), 404
    db.session.delete(favorite_planet)
    db.session.commit()
    return jsonify({"message": "Planeta favorito eliminado correctamente"}), 200

@app.route('/people/favorite/<int:id>', methods=['DELETE'])
def delete_favorite_character(id):
    favorite_character = FavoriteCharacters.query.get(id)
    if not favorite_character:
        return jsonify({"message": "Personaje favorito no encontrado"}), 404
    db.session.delete(favorite_character)
    db.session.commit()
    return jsonify({"message": "Personaje favorito eliminado correctamente"}), 200

@app.route('/starships/favorite/<int:id>', methods=['DELETE'])
def delete_favorite_starship(id):
    favorite_starship = FavoriteStarships.query.get(id)
    if not favorite_starship:
        return jsonify({"message": "Nave favorita no encontrada"}), 404
    db.session.delete(favorite_starship)
    db.session.commit()
    return jsonify({"message": "Nave favorita eliminada correctamente"}), 200

@app.route('/planets/<int:id>', methods=['PUT'])
def update_planet(id):
    planet = Planets.query.get(id)
    if not planet:
        return jsonify({"message": "Planeta no encontrado"}), 404
    body = request.get_json()
    if "name" in body:
        planet.name = body["name"]
    if "population" in body:
        planet.population = body["population"]
    db.session.commit()
    return jsonify({"message": "Planeta actualizado correctamente"}), 200

@app.route('/planets/<int:id>', methods=['DELETE'])
def delete_planet(id):
    planet = Planets.query.get(id)
    if not planet:
        return jsonify({"message": "Planeta no encontrado"}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planeta eliminado correctamente"}), 200

@app.route('/starships/<int:id>', methods=['PUT'])
def update_starship(id):
    starship = Starships.query.get(id)
    if not starship:
        return jsonify({"message": "Nave espacial no encontrada"}), 404
    body = request.get_json()
    if "name" in body:
        starship.name = body["name"]
    if "model" in body:
        starship.model = body["model"]
    db.session.commit()
    return jsonify({"message": "Nave espacial actualizada correctamente"}), 200

@app.route('/starships/<int:id>', methods=['DELETE'])
def delete_starship(id):
    starship = Starships.query.get(id)
    if not starship:
        return jsonify({"message": "Nave espacial no encontrada"}), 404
    db.session.delete(starship)
    db.session.commit()
    return jsonify({"message": "Nave espacial eliminada correctamente"}), 200

@app.route('/people/<int:id>', methods=['PUT'])
def update_person(id):
    person = People.query.get(id)
    if not person:
        return jsonify({"message": "Persona no encontrada"}), 404
    body = request.get_json()
    if "name" in body:
        person.name = body["name"]
    if "height" in body:
        person.height = body["height"]
    if "mass" in body:
        person.mass = body["mass"]
    db.session.commit()
    return jsonify({"message": "Persona actualizada correctamente"}), 200

@app.route('/people/<int:id>', methods=['DELETE'])
def delete_person(id):
    person = People.query.get(id)
    if not person:
        return jsonify({"message": "Persona no encontrada"}), 404
    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Persona eliminada correctamente"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
