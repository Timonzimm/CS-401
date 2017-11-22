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


@app.route('/country/<string:country>')
def informations_by_country(country):
    """Returns the coordinates of all attacks of the given country."""
    cur = get_db().execute('SELECT ShortName, Region, IncomeGroup FROM Country WHERE CountryCode="{}"'.format(country))
    country_infos = cur.fetchall()
    cur.close()
    return jsonify(country_infos[0])

@app.route('/coords/<string:country>')
def attack_coordinates_by_country(country):
    """Returns the coordinates of all attacks of the given country."""
    cur = get_db().execute('SELECT longitude, latitude FROM Attacks WHERE iso_code="{}"'.format(country))
    attack_coords = cur.fetchall()
    cur.close()
    return jsonify(attack_coords)

@app.route('/coords/year/<int:year>')
def attack_coordinates_by_year(year):
    """Returns the coordinates of all attacks of the given year."""
    cur = get_db().execute('SELECT longitude, latitude FROM Attacks WHERE iyear={}'.format(year))
    attack_coords = cur.fetchall()
    cur.close()
    return jsonify(attack_coords)

@app.route('/attacks/countries')
def all_attacks():
    """Returns the total number of attacks for each country."""
    cur = get_db().execute('SELECT iso_code, COUNT(*) as num_attacks FROM Attacks GROUP BY iso_code')
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/attacks/types/<string:country>/<int:num>')
def attack_types_by_country(country, num):
    """Returns the types list with the corresponding number of attacks in descending order of the given country."""
    cur = get_db().execute('SELECT attacktype1_txt, num_attacks FROM (SELECT attacktype1_txt, COUNT(attacktype1_txt) num_attacks FROM Attacks WHERE iso_code="{}" GROUP BY attacktype1_txt) ORDER BY num_attacks DESC LIMIT {}'.format(country, num))
    attack_types = cur.fetchall()
    cur.close()
    return jsonify(attack_types)

@app.route('/attacks/targets/<string:country>/<int:num>')
def attack_targets_by_country(country, num):
    """Returns the targets list with the corresponding number of attacks in descending order of the given country."""
    cur = get_db().execute('SELECT targtype1_txt, num_attacks FROM (SELECT targtype1_txt, COUNT(targtype1_txt) num_attacks FROM Attacks WHERE iso_code="{}" GROUP BY targtype1_txt) ORDER BY num_attacks DESC LIMIT {}'.format(country, num))
    attack_targets = cur.fetchall()
    cur.close()
    return jsonify(attack_targets)

@app.route('/attacks/perpetrators/<string:country>/<int:num>')
def attack_perpetrators_by_country(country, num):
    """Returns the perpetrators list with the number of attacks corresponding to their attacks in descending order of the given country."""
    cur = get_db().execute('SELECT gname, num_attacks FROM (SELECT gname, COUNT(gname) num_attacks FROM Attacks WHERE iso_code="{}" GROUP BY gname) ORDER BY num_attacks DESC LIMIT {}'.format(country, num))
    attack_perpetrators = cur.fetchall()
    cur.close()
    return jsonify(attack_perpetrators)

@app.route('/attacks/num_victims/<string:country>')
def num_victims_per_year_by_country(country):
    """Returns the number of victims per year of the given country."""
    cur = get_db().execute('SELECT iyear, SUM(nkill) FROM Attacks WHERE iso_code="{}" GROUP BY iyear'.format(country))
    num_victims = cur.fetchall()
    cur.close()
    return jsonify(num_victims)

@app.route('/attacks/num_attacks/<string:country>')
def num_attacks_per_year_by_country(country):
    """Returns the number of attacks per year of the given country."""
    cur = get_db().execute('SELECT iyear, COUNT(*) FROM Attacks WHERE iso_code="{}" GROUP BY iyear'.format(country))
    num_attacks = cur.fetchall()
    cur.close()
    return jsonify(num_attacks)

@app.route('/development/electric_consumption/<string:country>')
def electric_consumption_per_year_by_country(country):
    """Returns the electric consumption (kWh per capita) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="EG.USE.ELEC.KH.PC"'.format(country))
    electric_consumption = cur.fetchall()
    cur.close()
    return jsonify(electric_consumption)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)