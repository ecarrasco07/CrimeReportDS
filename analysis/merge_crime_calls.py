import pandas as pd

'''
Function that returns two dataframes one that is the merged product of Calls and Census data.
The second returned dataframe are the obersvations that do not have a GEOID from geocoding errors.

The function takes a two data frams as input
census: Census dataframe
calls: Calls dataframe
'''
def merge_census_calls(census, calls):
    ##making changes to Calls df by first naming columns appropriately
    ##before sorting the values via most recent date and changing 
    ##column types according to what is needed
    calls.columns = ['Call Number' , 'Date/Time' , 'Address' , 'District' , 'Nature of Call' , 'Status' , 'Latitude' , 'Longitude', "Tract"]
    calls[["Date/Time"]] = calls[["Date/Time"]].apply(pd.to_datetime)
    calls = calls.sort_values(by='Date/Time', ascending=False)
    calls[["Tract"]] = calls[["Tract"]].apply(pd.to_numeric)

    ##making changes to Census df by first naming columns appropriately
    ##before adding in and altering columns with issues 
    census.columns = ['GEOID' , 'Tract' , 'Geometry' , 'Estimated Population' , 'Male Population' , 'Female Population' , 'Median Age' , 'Median Income', 'White Population', 'Black Population', 'Native Population', 'Hispanic Population', 'Income Poverty Level']
    census[["Tract","Estimated Population", "Male Population" ,"Female Population", "Median Age", "Median Income","White Population", "Black Population", "Native Population", "Hispanic Population","Income Poverty Level"]] = census[["Tract","Estimated Population", "Male Population" ,"Female Population", "Median Age", "Median Income","White Population", "Black Population", "Native Population", "Hispanic Population","Income Poverty Level"]].apply(pd.to_numeric)
    census["Hispanic Population"] = census["Estimated Population"] - (census["White Population"]+census["Black Population"]+census["Native Population"])
    census["Percent White"] = round((census["White Population"] / census["Estimated Population"])*100,3)
    census["Percent Black"] = round((census["Black Population"] / census["Estimated Population"])*100,3)
    census["Percent Native"] = round((census["Native Population"] / census["Estimated Population"])*100,3)
    census["Percent Hispanic"] = round((census["Hispanic Population"] / census["Estimated Population"])*100,3)
    census["Predominant  Tract Population"] = census[['Percent White', 'Percent Black', 'Percent Native','Percent Hispanic']] \
        .idxmax(axis=1).str.replace('Percent ', '').tolist()

    ##making merged df that gives all of the census data for each call
    final=calls.merge(census,how="left",on="Tract")

    ##storing specific cases where merge didn't properly assign census data
    ##then dropping empty cases accordingly
    empty = final[final['GEOID'].isnull()]
    final = final.dropna(subset=['GEOID'])

    return(final, empty)