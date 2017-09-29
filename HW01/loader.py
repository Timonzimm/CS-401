import glob, os, re
import pandas as pd

DATA_FOLDER = 'Data'
os.chdir('./{}/ebola'.format(DATA_FOLDER))
DIRS_COUNTRIES = [d for d in os.listdir('.') if os.path.isdir(os.path.join('.', d))]
DATE_PATTERN = re.compile(r'([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])')

dfs = []
for dir in DIRS_COUNTRIES:
    table_files = glob.glob("./{}/*.csv".format(dir))
    print('Country: {}'.format(dir))
    df = pd.DataFrame()
    for f in table_files:
        year, month, day = DATE_PATTERN.search(f).groups()
        print(year, month, day)
        df = pd.read_csv(f)
        print(df.columns)
    print('*'*50)
    exit()