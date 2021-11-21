from flask import Flask, jsonify, render_template, request, json
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        #Method1
        # dictionary = {}
        # # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     # Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     dictionary[column.name] = getattr(self, column.name)

        #Method2 - Using dictionary comprehenshion
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary

@app.route("/")
def home():
    print(Cafe.query.count())
    return render_template("index.html")

## HTTP GET - Read Record

# Get a random cafe
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    # })
    return jsonify(cafe=random_cafe.to_dict())

# Get all the cafes
@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    cafe_list = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=cafe_list)

# Search for cafes at a particular location
@app.route("/search")
def get_all_cafes_at_a_particular_location():

    # Get the location parmaeter
    query_location = request.args.get("loc")

    #Get the corresponding cafes at a particular location
    cafes = db.session.query(Cafe).all()
    cafe_list = [cafe.to_dict() for cafe in cafes if cafe.location == str(query_location)]

    # If cafe list is empty, return the error message
    if not cafe_list:
        error_msg = {"Not Found": "Sorry, we don't have a cafe at that location."}
        return jsonify(errors=error_msg)
    else:
        return jsonify(cafes=cafe_list)

## HTTP POST - Create Record
# Add a new cafe
@app.route("/add", methods=['POST'])
def add_new_cafe():
    # Add a new movie into the database
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        has_sockets=bool(request.form.get("has_sockets")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    # If response is post,then print out a success message
    if request.method == 'POST':
        success_msg = {"success": "Successfully added the new cafe."}
        return jsonify(reponse=success_msg)

## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def patch_cafe(cafe_id):
    # Select a specific cafe with the cafe_id
    new_price = request.args.get("new_price")
    cafe_selected = Cafe.query.get(cafe_id)
    # Edit the database
    if cafe_selected:
        cafe_selected.coffee_price = new_price
        db.session.commit()
        success_msg = {"success": "Successfully updated the price."}
        return jsonify(response=success_msg)
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404

## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=['DELETE'])
def delete_cafe(cafe_id):
    cafe_selected = Cafe.query.get(cafe_id)
    if request.args.get("api-key") == "TopSecreteAPIKey":
        # If the api-key is correct but there's no cafe to select
        if not cafe_selected:
            return jsonify(response={"error": "Sorry, a cafe with that id was not found in the database"}), 404
        else:
            db.session.delete(cafe_selected)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe"})
    else:
        return jsonify(response={"error": "Sorry, that's not allowed. Make sure you have the correct api_key"}), 403

if __name__ == '__main__':
    app.run(debug=True)
