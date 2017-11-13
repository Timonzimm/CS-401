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

@app.route('/coords/<string:country>')
def attack_coordinates_by_country(country):
    """Returns the coordinates of all attacks of the given country."""
    cur = get_db().execute('SELECT longitude, latitude FROM Attacks WHERE iso_code="{}"'.format(country))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/coords/year/<int:year>')
def attack_coordinates_by_year(year):
    """Returns the coordinates of all attacks of the given year."""
    cur = get_db().execute('SELECT longitude, latitude FROM Attacks WHERE iyear={}'.format(year))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/attacks/countries')
def all_attacks():
    """Returns the total number of attacks for each country."""
    cur = get_db().execute('SELECT iso_code, COUNT(*) as num_attacks FROM Attacks GROUP BY iso_code')
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/attacks/types/<string:country>')
def attack_types_by_country(country):
    """Returns the types list with the corresponding number of attacks in descending order of the given country."""
    cur = get_db().execute('SELECT attacktype1_txt, num_attacks FROM (SELECT attacktype1_txt, COUNT(attacktype1_txt) num_attacks FROM Attacks WHERE iso_code="{}" GROUP BY attacktype1_txt) ORDER BY num_attacks DESC'.format(country))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/attacks/targets/<string:country>')
def attack_targets_by_country(country):
    """Returns the targets list with the corresponding number of attacks in descending order of the given country."""
    cur = get_db().execute('SELECT targtype1_txt, num_attacks FROM (SELECT targtype1_txt, COUNT(targtype1_txt) num_attacks FROM Attacks WHERE iso_code="{}" GROUP BY targtype1_txt) ORDER BY num_attacks DESC'.format(country))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/attacks/perpetrators/<string:country>')
def attack_perpetrators_by_country(country):
    """Returns the perpetrators list with the number of victims corresponding to their attacks in descending order of the given country."""
    cur = get_db().execute('SELECT gname, num_victims FROM (SELECT gname, SUM(nkill) num_victims FROM Attacks WHERE iso_code="{}" GROUP BY gname) ORDER BY num_victims DESC LIMIT 20'.format(country))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/attacks/num_victims/<string:country>')
def num_victims_per_year_by_country(country):
    """Returns the number of victims per year of the given country."""
    cur = get_db().execute('SELECT iyear, SUM(nkill) FROM Attacks WHERE iso_code="{}" GROUP BY iyear'.format(country))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/attacks/num_attacks/<string:country>')
def num_attacks_per_year_by_country(country):
    """Returns the number of attacks per year of the given country."""
    cur = get_db().execute('SELECT iyear, COUNT(*) FROM Attacks WHERE iso_code="{}" GROUP BY iyear'.format(country))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)