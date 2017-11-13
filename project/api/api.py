import sqlite3
from scipy.stats import gaussian_kde
from flask import Flask, g, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

DATABASE = 'data/database.sqlite'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/countries')
def all_attacks_by_country():
    cur = get_db().execute('SELECT iso_code, COUNT(*) as num_attacks FROM Attacks GROUP BY iso_code')
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/coords/<string:country>')
def all_attacks_by_coordinates_sample(country):
    cur = get_db().execute('SELECT longitude, latitude FROM Attacks WHERE iso_code="{}"'.format(country))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/coords/year/<int:year>')
def all_attacks_by_coordinates_and_year(year):
    cur = get_db().execute('SELECT longitude, latitude FROM Attacks WHERE iyear={}'.format(year))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)