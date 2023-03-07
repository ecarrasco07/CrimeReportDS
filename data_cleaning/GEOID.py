from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from censusgeocode import CensusGeocode
import censusgeocode as cg 

'''
GEOID function for adding col to large csv file.
Takes a csv file path as param

'''
def mass_geoid(path = "/Users/eduardo/Downloads/crimedata.csv"):

    def geocode_row(row):
        cg = CensusGeocode()
        census_tract = cg.coordinates(x=row.Longitude, y=row.Latitude)['Census Tracts'][0]['GEOID']
        return census_tract

    # READ THE FILE AS A DF
    df = pd.read_csv(path, usecols=['Latitude', 'Longitude'])
    print("SUCCESSFULLY READ DF")
    print(df.head())


    with ThreadPoolExecutor() as executor:
        results = list(executor.map(geocode_row, df.itertuples(index=False)))


    df = df.assign(census_tract = results)


    df.to_csv('/Users/eduardo/Downloads/crimedata_withtracts.csv', index=False)



'''
Function takes the path to a csv file and takes lat and long columns to
find which tract the coords belong to.

path: Path of the csv file 
'''
def geoid_csv(path, path_out):
    # READ THE FILE AS A DF
    df = pd.read_csv(path)

    #FUNCTION THAT ADDS GEOID ROW FOR EACH CALL
    df['GEOID'] = df.apply(lambda x : cg.coordinates(x=x['Longitude'], y=x['Latitude'])['Census Tracts'][0]['GEOID'], axis = 1)

    #EXPORT AS CSV
    df.to_csv(path_out, index=False)


'''
Function takes a pandas df and add GEOID column.
'''
def geo_id(df):

    result = df.apply(lambda x : cg.coordinates(x=x['Longitude'], y=x['Latitude'])['Census Tracts'][0]['GEOID'], axis = 1)
    df = df.assign(GEOID = result)
    return df

'''
TESTING CODE

path = "/Users/eduardo/Downloads/crimedata.csv"

df = pd.read_csv(path, usecols=['Latitude', 'Longitude'])
print("SUCCESSFULLY READ DF")
print(df.head())

tester = df.head(10)

tester = geo_id(tester)

print(tester.head())
'''


