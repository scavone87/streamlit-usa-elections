import streamlit as st
import pandas as pd
import numpy as np
import base64


year_census_map = {
	'4/1/2010 Census population' : 1,
	'4/1/2010 population estimates base' : 2 ,
	'7/1/2010 population estimate': 3, 
	'7/1/2011 population estimate': 4, 
	'7/1/2012 population estimate': 5, 
	'7/1/2013 population estimate': 6, 
	'7/1/2014 population estimate': 7, 
	'7/1/2015 population estimate' : 8, 
	'7/1/2016 population estimate' : 9, 
	'7/1/2017 population estimate' : 10,
	'7/1/2018 population estimate' : 11,
	'7/1/2019 population estimate': 12
}   


race_map = {
  'Two or More Races' : "TOM",
  'Hispanic, White alone or in combination' : "HWA",
  'Hispanic, Asian alone or in combination' : "HAAC",
  'Not Hispanic, Native Hawaiian and Other Pacific Islander alone or in combination' : "NHNAC",
  'Hispanic, American Indian and Alaska Native alone or in combination' : "HIAC",
  'Not Hispanic, White alone' : "NHWA",
  'Not Hispanic, Asian alone or in combination' : "NHAAC",
  'Not Hispanic' : "NH",
  'Hispanic' : "H",
  'Hispanic, White alone or in combination' : "HWAC",
  'Hispanic, Asian alone' : "HAA",
  'American Indian and Alaska Native alone or in combination' : "IAC",
  'Hispanic, Native Hawaiian and Other Pacific Islander alone or in combination' : "HNAC",
  'Hispanic, Black or African American alone or in combination' : "HBAC",
  'Black or African American alone or in combination' : "BAC",
  'Hispanic, Two or More Races' : "HTOM",
  'White alone or in combination' : "WAC",
  'White alone' : "WA",
  'Not Hispanic, Black or African American alone' : "NHBA",
  'Hispanic, Black or African American alone' : "HBA",
  'Asian alone or in combination' : "AAC",
  'Not Hispanic, White alone or in combination' : "NHWAC",
  'Black or African American alone' : "BA",
  'Native Hawaiian and Other Pacific Islander alone' : "NA",
  'Not Hispanic, Black or African American alone or in combination' : "NHBAC",
  'Hispanic, American Indian and Alaska Native alone' : "HIA",
  'Native Hawaiian and Other Pacific Islander alone or in combination' : "NAC",
  'Not Hispanic, Native Hawaiian and Other Pacific Islander alone' : "NHNA",
  'Not Hispanic, American Indian and Alaska Native alone' : "NHIA",
  'Asian alone' : "AA",
  'American Indian and Alaska Native alone' : "IA",
  'Not Hispanic, American Indian and Alaska Native alone or in combination' : "NHIAC",
  'Not Hispanic, Asian alone or in combination' : "NHAA",
  'Not Hispanic, Two or More Races' : "NHTOM",
  'Hispanic, Native Hawaiian and Other Pacific Islander alone' : "HNA"
}

agegrp_map = {
    'Total' : 0,
    'Age 0 to 4 years' : 1,
    'Age 5 to 9 years' : 2,
    'Age 10 to 14 years' : 3,
    'Age 15 to 19 years' : 4,
    'Age 20 to 24 years' : 5,
    'Age 25 to 29 years' : 6,
    'Age 30 to 34 years' : 7,
    'Age 35 to 39 years' : 8,
    'Age 40 to 44 years' : 9,
    'Age 45 to 49 years' : 10,
    'Age 50 to 54 years' : 11, 
    'Age 55 to 59 years' : 12,
    'Age 60 to 64 years' : 13, 
    'Age 65 to 69 years' : 14,
    'Age 70 to 74 years' : 15,
    'Age 75 to 79 years' : 16,
    'Age 80 to 84 years' : 17,
    'Age 85 years or older' : 18
}


@st.cache(allow_output_mutation=True)
def load_dataset(path, na_values=""):
    f = open(path)
    if not na_values:
        dataset = pd.read_csv(f)
    else:
        dataset = pd.read_csv(f, na_values=na_values)
    return dataset


@st.cache(suppress_st_warning=True)
def calculate_percentage_votes_by_county(df_elections, candidate = 0):
    """
    Calculates the percentage of votes for the input candidate by county.
    If the candidate is in, it returns the percentage of votes, otherwise the full dataframe with the percentages of votes
    
    It is possible to specify a key for:
    - candidate: 0 for total
        
    Input parameters:
    df_elections (pandas.core.frame.DataFrame): elections dataframe
    candidate (str): candidate  
    
    Output:
    pandas.core.frame.DataFrame: dataframe containing the percentage of votes for the input candidate by each county 
    
    """
    sum_votes_county = df_elections.groupby(['state', 'county'], as_index=False).sum().drop(columns = ['STATEFP', 'COUNTYFP'])
    sum_votes_county = sum_votes_county.rename(columns = {'votes' : 'sum_votes'})
    elections_and_sum_votes = pd.merge(df_elections, sum_votes_county, how="inner", left_on=['state', 'county'], right_on=['state', 'county'])
    elections_and_sum_votes['percentage_votes'] = (elections_and_sum_votes['votes']/elections_and_sum_votes['sum_votes'])*100
    if candidate == 0:
        return elections_and_sum_votes[['STATENAME', 'county', 'COUNTYFP' ,'candidate' ,'votes' ,'percentage_votes']].reset_index(drop=True)
    return elections_and_sum_votes[elections_and_sum_votes.candidate == candidate][['STATENAME', 'county', 'votes', 'percentage_votes']].sort_values('percentage_votes', ascending= False).reset_index(drop=True)

@st.cache(suppress_st_warning=True)
def calculate_percentage_votes_by_state(df_elections, candidate = 0):
    """
    Calculates the percentage of votes for the input candidate by state.
    If the candidate is in, it returns the percentage of votes, otherwise the full dataframe with the percentages of votes
    
    It is possible to specify a key for:
    - candidate: 0 for total
        
    Input parameters:
    df_elections (pandas.core.frame.DataFrame): elections dataframe
    candidate (str): candidate  
    
    Output:
    pandas.core.frame.DataFrame: dataframe containing the percentage of votes for the input candidate by each state 
    
    """
    votes_candidate_by_state = df_elections.groupby(['STATENAME', 'candidate'], as_index=False).sum()
    tot_votes_by_state = df_elections.groupby(['STATENAME'], as_index=False).sum()
    tot_votes_by_state = tot_votes_by_state.rename(columns = {'votes' : 'total_votes'})
    elections_plus_tot_votes = pd.merge(votes_candidate_by_state, tot_votes_by_state, how="inner", left_on=["STATENAME"], right_on=["STATENAME"])
    elections_plus_tot_votes["percentage_votes"] = (elections_plus_tot_votes["votes"]/elections_plus_tot_votes["total_votes"]) * 100
    if candidate == 0:
        return elections_plus_tot_votes[["STATENAME", "candidate", "percentage_votes"]]
    return elections_plus_tot_votes[elections_plus_tot_votes.candidate == candidate].sort_values('STATENAME')['percentage_votes']


@st.cache(suppress_st_warning=True)
def calculate_percentage_race_by_county(df_demography, race, agegrp = 0, year = 9):
    """
    Calculates the percentage of input race (male + female) for each county
    It is possible to specify a key for:
    - age group (0-18): 0 for total, other for age group from 0 years to over 85 years
    - year (1-12): from 4/1/2010 to 7/1/2019, default 9: 7/1/2016
        
    Input parameters:
    df_demography (pandas.core.frame.DataFrame): demography dataframe
    race (str): race 
    agegrp (int): age group
    year (int): year 
    
    Output:
    pandas.core.frame.DataFrame: dataframe containing percentage of citizens for the input race, grouped by state and county
    
    """
    df_race_m = df_demography[(df_demography.AGEGRP == agegrp) & (df_demography.YEAR == year)].groupby(['STNAME', 'CTYNAME', 'COUNTY']).sum()[race + "_MALE"].to_frame(race).reset_index()
    df_race_f = df_demography[(df_demography.AGEGRP == agegrp) & (df_demography.YEAR == year)].groupby(['STNAME', 'CTYNAME', 'COUNTY']).sum()[race + "_FEMALE"].to_frame(race).reset_index()
    df_race_tot = (df_race_m[race] + df_race_f[race]).to_frame()
    df_total = df_demography[(df_demography.AGEGRP == agegrp) & (df_demography.YEAR == year)].groupby(['STNAME', 'CTYNAME', 'COUNTY']).sum()["TOT_POP"].to_frame().reset_index()
    percentage_race = ((df_race_tot[race] / df_total["TOT_POP"]) * 100).round(decimals = 2)
    df_total[race] = percentage_race
    return df_total.sort_values(by=race, ascending = False)


@st.cache(suppress_st_warning=True)
def calculate_percentage_race_by_state(df_demography,race, agegrp = 0, year = 9):
    """
    Calculates the percentage of input race (male + female) for each state
    It is possible to specify a key for:
    - age group (0-18): 0 for total, other for age group from 0 years to over 85 years
    - year (1-12): from 4/1/2010 to 7/1/2019, default 9: 7/1/2016
        
    Input parameters:
    df_demography (pandas.core.frame.DataFrame): demography dataframe
    race (str): race 
    agegrp (int): age group
    year (int): year 
    
    Output:
    pandas.core.frame.DataFrame: dataframe containing percentage of citizens for the input race, grouped by state
    
    """
    df_race_m = df_demography[(df_demography.AGEGRP == agegrp) & (df_demography.YEAR == year)].groupby(['STNAME']).sum()[race + "_MALE"].to_frame(race).reset_index()
    df_race_f = df_demography[(df_demography.AGEGRP == agegrp) & (df_demography.YEAR == year)].groupby(['STNAME']).sum()[race + "_FEMALE"].to_frame(race).reset_index()
    df_race_tot = (df_race_m[race] + df_race_f[race]).to_frame()
    df_total = df_demography[(df_demography.AGEGRP == agegrp) & (df_demography.YEAR == year)].groupby(['STNAME']).sum()["TOT_POP"].to_frame().reset_index()
    percentage_race = ((df_race_tot[race] / df_total["TOT_POP"]) * 100).round(decimals = 2)
    df_total[race] = percentage_race
    return df_total

@st.cache(suppress_st_warning=True)
def calculate_pro_capite(pro_capite_set, sort, year='Average'):
    if year != 'Average':
        return pro_capite_set[['State', 'County', year]].round(2).sort_values(year, ascending=sort).reset_index(drop = True)
    df = pd.DataFrame({
        'State': pro_capite_set['State'],
        'County': pro_capite_set['County'],
        'Average': pro_capite_set[pro_capite_set.columns[6:]].mean(axis=1, numeric_only=True).round(2)
    })
    return df.sort_values('Average', ascending=sort).reset_index(drop = True)

@st.cache(suppress_st_warning=True)
def get_table_download_link(df):
    """Generates a link allowing the data in a given pandas dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'
    return href


def get_elections_and_race_by_county(df_elections, df_demography, race, agegrp = 0, year = 9):
    """
    Calculates the percentage of citizens belonging the input race and the percentage of votes to a candidate from each county
    
    It is possible to specify a key for:
    - age group (0-18): 0 for total, other for age group from 0 years to over 85 years
    - year (1-12): from 4/1/2010 to 7/1/2019, default 9: 7/1/2016
        
    Input parameters:
    df_elections (pandas.core.frame.DataFrame): elections dataframe
    df_demography (pandas.core.frame.DataFrame): demography dataframe
    race (str): race
    agegrp (int): age group
    year (int): year 
    
    Output:
    pandas.core.frame.DataFrame: dataframe containing the percentage of citizens belonging to the input race with the percentage of votes to a candidate from each county
    
    """
    elections_with_percentage_by_county = calculate_percentage_votes_by_county(df_elections)
    percentage_race = calculate_percentage_race_by_county(df_demography, race, agegrp = agegrp, year = year)
    return pd.merge(elections_with_percentage_by_county, percentage_race, how="inner", left_on=["STATENAME","COUNTYFP"], right_on=["STNAME","COUNTY"])

def get_elections_and_race_by_state(df_elections, df_demography, race, agegrp = 0, year = 9):
    """
    Calculates the percentage of citizens belonging the input race and the percentage of votes to a candidate from each state
    
    It is possible to specify a key for:
    - age group (0-18): 0 for total, other for age group from 0 years to over 85 years
    - year (1-12): from 4/1/2010 to 7/1/2019, default 9: 7/1/2016
        
    Input parameters:
    df_elections (pandas.core.frame.DataFrame): elections dataframe
    df_demography (pandas.core.frame.DataFrame): demography dataframe
    race (str): race
    agegrp (int): age group
    year (int): year 
    
    Output:
    pandas.core.frame.DataFrame: dataframe containing the percentage of citizens belonging to the input race with the percentage of votes to a candidate from each state
    
    """
    elections_with_percentage_by_state = calculate_percentage_votes_by_state(df_elections)
    percentage_race = calculate_percentage_race_by_state(df_demography, race, agegrp= agegrp, year = year)
    return pd.merge(elections_with_percentage_by_state, percentage_race, how="inner", left_on=["STATENAME"], right_on=["STNAME"])

@st.cache
def get_votes_and_procapite_dataset(procapite_dataset, elections_dataset):
    procapite_filtered = procapite_dataset[['State', 'County', '2016']]
    elections_filtered = elections_dataset[['state', 'county', 'candidate', 'votes']]
    sum_votes = elections_filtered.groupby(["state", "county"], as_index=False).sum()
    sum_votes = sum_votes.rename(columns = {"votes" : "sum_votes"})
    elections_filtered = pd.merge(elections_filtered, sum_votes, how="inner")
    elections_filtered["percentage_votes"] = (elections_filtered["votes"]/elections_filtered["sum_votes"]) * 100
    df = pd.DataFrame()
    df['State'] = procapite_filtered['State']
    df[['County', 'City']] = procapite_filtered.County.str.split("+", expand = True)
    plus_counties = df[df["City"].notnull()]

    for index,county_va in enumerate(plus_counties.County):
        county_va = county_va.strip()
        independent_city = plus_counties.iloc[index].City.strip()
        state = plus_counties.iloc[index].State
        list_candidate = elections_filtered[(elections_filtered.state == state) & ((elections_filtered.county == county_va) | (elections_filtered.county == independent_city))]['candidate'].unique()
        for candidate in list_candidate:
            first_county_votes = elections_filtered[(elections_filtered.state == state) & (elections_filtered.county == county_va) & (elections_filtered.candidate == candidate)]['votes'].item()
            first_county_tot_votes = elections_filtered[(elections_filtered.state == state) & (elections_filtered.county == county_va) & (elections_filtered.candidate == candidate)]['sum_votes'].item()
            second_county_votes = elections_filtered[(elections_filtered.state == state) & (elections_filtered.county == (independent_city + " City")) & (elections_filtered.candidate == candidate)]['votes'].item() 
            second_county_tot_votes = elections_filtered[(elections_filtered.state == state) & (elections_filtered.county == (independent_city + " City")) & (elections_filtered.candidate == candidate)]['sum_votes'].item() 
            sum_votes_candidate = first_county_votes + second_county_votes
            sum_tot_votes = first_county_tot_votes + second_county_tot_votes
            percentage_double_cities = (sum_votes_candidate/sum_tot_votes) * 100
            elections_filtered.loc[(elections_filtered.state == state) & (elections_filtered.county == county_va) & (elections_filtered.candidate == candidate), ['percentage_votes']] = percentage_double_cities
            elections_filtered.loc[(elections_filtered.state == state) & (elections_filtered.county == county_va) & (elections_filtered.candidate == candidate), ['county']] = elections_filtered[(elections_filtered.state == state) & (elections_filtered.county == county_va) & (elections_filtered.candidate == candidate)]["county"] + " + " + independent_city
    votes_and_procapite = pd.merge(elections_filtered, procapite_filtered,  how='inner', left_on=['state','county'], right_on = ['State','County']).drop(columns=['State', 'County'])
    return votes_and_procapite

@st.cache(suppress_st_warning=True)
def get_votes_and_procapite_by_winner(elections_dataset, procapite_dataset):
    sum_votes_by_candidate = elections_dataset.groupby(['state', 'candidate'], as_index=False).sum().sort_values(by='state')
    winners = sum_votes_by_candidate.groupby(['state'],as_index=False).max('votes')
    votes_by_state = pd.merge(sum_votes_by_candidate, winners, how="inner")
    votes_by_state = votes_by_state[['state', 'candidate', 'votes']]
    sum_votes_state = elections_dataset.groupby(['state'], as_index=False).sum().sort_values(by='state')
    votes_by_state['percentage_votes'] = votes_by_state['votes'] / sum_votes_state['votes'] * 100
    mean_pro_capite = procapite_dataset.groupby('State').mean()['2016'].round(2).to_frame()
    votes_and_pro_capite = pd.merge(votes_by_state, mean_pro_capite, how="inner", left_on=['state'], right_on=["State"])
    return votes_and_pro_capite

@st.cache(suppress_st_warning=True)
def get_corr_coef_for_candidate(candidate, df, x, y, plot = True): 
        
    """
    Calculates the correlation coefficient between two variables filtering the dataframe by candidate
    It is possible to specify a key for:
    - plot: To graphically display the result (True, by default) 
        
    Input parameters:
    candidate (str):                    candidate name
    df (pandas.core.frame.DataFrame):   dataframe to analyze 
    x (str):                            column name to be interpreted as x-axis
    y (str):                            column name to be interpreted as y-axis
    plot (bool):                         display
    
    Output:
    numpy.float64: value of the correlation coefficient between the variables x and y
    
    """  
    df_candidate = df[df.candidate == candidate]
    cc = np.corrcoef(df_candidate[x], df_candidate[y])[1,0] 
    if not np.isnan(cc):
        return cc
    st.write('Non ?? stato possibile calcolare il coefficiente di correlazione')


@st.cache
def calculate_weighted_votes(df_elections):
    for candidate in df_elections.candidate.unique():
        df_candidate = df_elections[df_elections.candidate == candidate]
        for state in df_elections.state.unique():
            for county in df_candidate[(df_candidate.state == state)]['county']:
                neighbors = df_candidate[(df_candidate.county == county) & (df_candidate.state == state)]['NEIGHBORS'].item().split(", ")
                neighbor_votes = []
                population = []
                for neighbor in neighbors:
                    if not df_candidate[(df_candidate.county == neighbor) & (df_candidate.NEIGHBORS.str.contains(county))].empty:
                        neighbor_votes.append(df_candidate[(df_candidate.county == neighbor) & (df_candidate.NEIGHBORS.str.contains(county))]['votes'].iat[0])
                        population.append(df_candidate[(df_candidate.county == neighbor) & (df_candidate.NEIGHBORS.str.contains(county))]['TOT_POP'].iat[0])
                if population:
                    df_elections.loc[(df_elections.candidate == candidate) & (df_elections.state == state) & (df_elections.county == county), ['weighted votes']] = round(np.average(neighbor_votes, weights = population), 2)
    return df_elections
    
    
def calculate_percentage_woman(df_demography, df_elections, candidate, race = 'TOT_FEMALE'):
    a = df_demography[(df_demography.YEAR == 9) & (df_demography.AGEGRP == 0)].sort_values('state').groupby('state').sum()[race].reset_index(drop = True)
    b = df_demography[(df_demography.YEAR == 9) & (df_demography.AGEGRP == 0)].sort_values('state').groupby('state').sum()['TOT_POP'].reset_index(drop = True)
    percentage_female = (a/b)*100
    y = calculate_percentage_votes_by_state(df_elections, candidate)
    return percentage_female,y