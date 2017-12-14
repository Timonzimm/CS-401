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
def all_countries():
    cur = get_db().execute('SELECT ShortName, CountryCode FROM Country')
    countries_infos = cur.fetchall()
    cur.close()
    return jsonify(countries_infos)

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

@app.route('/attacks/types/<string:country>')
def attack_types_by_country(country):
    """Returns the types list with the corresponding number of attacks in descending order of the given country."""
    cur = get_db().execute('SELECT attacktype1_txt, num_attacks FROM (SELECT attacktype1_txt, COUNT(attacktype1_txt) num_attacks FROM Attacks WHERE iso_code="{}" GROUP BY attacktype1_txt) ORDER BY num_attacks DESC'.format(country))
    attack_types = cur.fetchall()
    cur.close()
    return jsonify(attack_types)

@app.route('/attacks/targets/<string:country>')
def attack_targets_by_country(country):
    """Returns the targets list with the corresponding number of attacks in descending order of the given country."""
    cur = get_db().execute('SELECT targtype1_txt, num_attacks FROM (SELECT targtype1_txt, COUNT(targtype1_txt) num_attacks FROM Attacks WHERE iso_code="{}" GROUP BY targtype1_txt) ORDER BY num_attacks DESC'.format(country))
    attack_targets = cur.fetchall()
    cur.close()
    return jsonify(attack_targets)

@app.route('/attacks/perpetrators/<string:country>')
def attack_perpetrators_by_country(country):
    """Returns the perpetrators list with the number of attacks corresponding to their attacks in descending order of the given country."""
    cur = get_db().execute('SELECT gname, num_attacks FROM (SELECT gname, COUNT(gname) num_attacks FROM Attacks WHERE iso_code="{}" GROUP BY gname) ORDER BY num_attacks DESC'.format(country))
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

@app.route('/score/<string:country>')
def score_per_year_by_country(country):
    """Returns the Global Terrorism Index (GTI) per year of the given country."""
    cur = get_db().execute('''SELECT iyear, (
    1*COUNT(*)
    + 3*SUM(nkill)
    + 0.5*SUM(nwound)
    + 2*SUM(case propextent when 1.0 then 1 else 0 end)
    + 2*SUM(case propextent when 2.0 then 1 else 0 end)
    + 2*SUM(case propextent when 3.0 then 1 else 0 end)
    + 2*SUM(case propextent when 4.0 then 1 else 0 end)) FROM Attacks WHERE iso_code="{}" GROUP BY iyear''' .format(country))
    score = cur.fetchall()
    cur.close()
    return jsonify(score)

# Economic development indicators

@app.route('/development/economy/electric_consumption/<string:country>')
def electric_consumption_per_year_by_country(country):
    """Returns the electric consumption (kWh per capita) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="EG.USE.ELEC.KH.PC"'.format(country))
    electric_consumption = cur.fetchall()
    cur.close()
    return jsonify(electric_consumption)

@app.route('/development/economy/co2_emissions/<string:country>')
def co2_emissions_per_year_by_country(country):
    """Returns the CO2 emissions (in kt) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="EN.ATM.CO2E.KT"'.format(country))
    co2_emissions = cur.fetchall()
    cur.close()
    return jsonify(co2_emissions)

@app.route('/development/economy/total_reserves/<string:country>')
def total_reserves_per_year_by_country(country):
    """Returns the total reserves (minus gold) in US$ per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="FI.RES.XGLD.CD"'.format(country))
    total_reserves = cur.fetchall()
    cur.close()
    return jsonify(total_reserves)

@app.route('/development/economy/arm_imports/<string:country>')
def arm_imports_per_year_by_country(country):
    """Returns the arm imports (SIPRI) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="MS.MIL.MPRT.KD"'.format(country))
    arm_imports = cur.fetchall()
    cur.close()
    return jsonify(arm_imports)

@app.route('/development/economy/arm_exports/<string:country>')
def arm_exports_per_year_by_country(country):
    """Returns the arm exports (SIPRI) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="MS.MIL.XPRT.KD"'.format(country))
    arm_exports = cur.fetchall()
    cur.close()
    return jsonify(arm_exports)

@app.route('/development/economy/gs_imports/<string:country>')
def gs_imports_per_year_by_country(country):
    """Returns the good and service imports (annual % growth) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="NE.IMP.GNFS.KD.ZG"'.format(country))
    gs_imports = cur.fetchall()
    cur.close()
    return jsonify(gs_imports)

@app.route('/development/economy/gs_exports/<string:country>')
def gs_exports_per_year_by_country(country):
    """Returns the good and service exports (annual % growth) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="NE.EXP.GNFS.KD.ZG"'.format(country))
    gs_exports = cur.fetchall()
    cur.close()
    return jsonify(gs_exports)

@app.route('/development/economy/gdp/<string:country>')
def gdp_per_year_by_country(country):
    """Returns the GDP (annual % growth) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="NY.GDP.MKTP.KD.ZG"'.format(country))
    gdp = cur.fetchall()
    cur.close()
    return jsonify(gdp)

@app.route('/development/economy/gni/<string:country>')
def gni_per_year_by_country(country):
    """Returns the GNI (annual % growth) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="NY.GNP.MKTP.KD.ZG"'.format(country))
    gni = cur.fetchall()
    cur.close()
    return jsonify(gni)

@app.route('/development/economy/tourism/<string:country>')
def tourism_per_year_by_country(country):
    """Returns the number of arrivals (tourism) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="ST.INT.ARVL"'.format(country))
    tourism = cur.fetchall()
    cur.close()
    return jsonify(tourism)

@app.route('/development/economy/foreign_inv/<string:country>')
def foreign_inv_per_year_by_country(country):
    """Returns the foreign direct investment (net inflows % of GDP) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="BX.KLT.DINV.WD.GD.ZS"'.format(country))
    foreign_inv = cur.fetchall()
    cur.close()
    return jsonify(foreign_inv)

# Social health development indicators

@app.route('/development/social_health/mortality_rate_under_5/<string:country>')
def mortality_rate_under_5_per_year_by_country(country):
    """Returns the mortality rate under 5 (per 1,000 people) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="SH.DYN.MORT"'.format(country))
    mortality_rate_under_5 = cur.fetchall()
    cur.close()
    return jsonify(mortality_rate_under_5)

@app.route('/development/social_health/hospital_beds/<string:country>')
def hospital_beds_per_year_by_country(country):
    """Returns the number of hospital beds (per 1,000 people) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="SH.MED.BEDS.ZS"'.format(country))
    hospital_beds = cur.fetchall()
    cur.close()
    return jsonify(hospital_beds)

@app.route('/development/social_health/birth_rate/<string:country>')
def birth_rate_per_year_by_country(country):
    """Returns the birth rate (per 1,000 people) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="SP.DYN.CBRT.IN"'.format(country))
    birth_rate = cur.fetchall()
    cur.close()
    return jsonify(birth_rate)

@app.route('/development/social_health/death_rate/<string:country>')
def death_rate_per_year_by_country(country):
    """Returns the death rate (per 1,000 people) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="SP.DYN.CDRT.IN"'.format(country))
    death_rate = cur.fetchall()
    cur.close()
    return jsonify(death_rate)

@app.route('/development/social_health/population_dens/<string:country>')
def population_dens_per_year_by_country(country):
    """Returns the population density (people per square km of land area) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="EN.POP.DNST"'.format(country))
    population_dens = cur.fetchall()
    cur.close()
    return jsonify(population_dens)

@app.route('/development/social_health/armed_forces/<string:country>')
def armed_forces_per_year_by_country(country):
    """Returns the armed forces personnel (total) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="MS.MIL.TOTL.P1"'.format(country))
    armed_forces = cur.fetchall()
    cur.close()
    return jsonify(armed_forces)

# Population development indicators

@app.route('/development/social_health/population_0_14/<string:country>')
def population_0_14_per_year_by_country(country):
    """Returns the population aged between 0-14 (in %) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="SP.POP.0014.TO.ZS"'.format(country))
    population_0_14 = cur.fetchall()
    cur.close()
    return jsonify(population_0_14)

@app.route('/development/social_health/population_15_64/<string:country>')
def population_15_64_per_year_by_country(country):
    """Returns the population aged between 15-64 (in %) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="SP.POP.1564.TO.ZS"'.format(country))
    population_15_64 = cur.fetchall()
    cur.close()
    return jsonify(population_15_64)

@app.route('/development/social_health/population_65_up/<string:country>')
def population_65_up_per_year_by_country(country):
    """Returns the population aged between 65 and above (in %) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="SP.POP.65UP.TO.ZS"'.format(country))
    population_65_up = cur.fetchall()
    cur.close()
    return jsonify(population_65_up)

@app.route('/development/social_health/population_growth/<string:country>')
def population_growth_per_year_by_country(country):
    """Returns the population annual % growth per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="SP.POP.GROW"'.format(country))
    population_growth = cur.fetchall()
    cur.close()
    return jsonify(population_growth)

# Wealth development indicators

@app.route('/development/wealth/renewable_energy_cons/<string:country>')
def renewable_energy_cons_per_year_by_country(country):
    """Returns the renewable energy consumption (% of total final energy consumption) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="EG.FEC.RNEW.ZS"'.format(country))
    renewable_energy_cons = cur.fetchall()
    cur.close()
    return jsonify(renewable_energy_cons)

@app.route('/development/wealth/air_transport/<string:country>')
def air_transport_per_year_by_country(country):
    """Returns the number of passenger carried per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="IS.AIR.PSGR"'.format(country))
    air_transport = cur.fetchall()
    cur.close()
    return jsonify(air_transport)

@app.route('/development/wealth/internet_users/<string:country>')
def internet_users_per_year_by_country(country):
    """Returns the internet users (per 1,000 people) per year of the given country."""
    cur = get_db().execute('SELECT Year, Value FROM Indicators WHERE CountryCode="{}" AND IndicatorCode="IT.NET.USER.P2"'.format(country))
    internet_users = cur.fetchall()
    cur.close()
    return jsonify(internet_users)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)