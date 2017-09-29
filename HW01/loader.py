import glob, os
import pandas as pd

DATA_FOLDER = 'Data'
os.chdir('./{}/ebola'.format(DATA_FOLDER))
DIRS_COUNTRIES = [d for d in os.listdir('.') if os.path.isdir(os.path.join('.', d))]

for dir in DIRS_COUNTRIES:
    table_files = glob.glob("./{}/*.csv".format(dir))

    for f in table_files:
        df = pd.read_csv(f)
        print(df.columns)