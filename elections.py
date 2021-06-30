from google.protobuf.descriptor import DescriptorMetaclass
import streamlit as st
import pandas as pd
import numpy as np

import services as srv

def app():
    elections = srv.load_dataset('datasets/election_group4_mod.csv')
    elections = elections[['state', 'STATENAME', 'STATEFP', 'COUNTYFP', "county", 'NEIGHBORS', "party", "office", 'candidate', 'votes']]
    st.title("Elezioni USA 2016 ")
    st.header("Anteprima dataset")
    state_list = elections['STATENAME'].unique()
    state_list = np.append(state_list, ["Tutti"])
    option = st.selectbox(
        'Quale stato vuoi vedere?',
        state_list, 
        index=10
    )
    
    df_download = pd.DataFrame() # Dataframe scaricabile
    if option == 'Tutti':
        df_download = elections
        st.dataframe(df_download)
    else:
        df_download = elections[elections.STATENAME == option]
        st.dataframe(df_download.reset_index(drop = True))
    linko =srv.get_table_download_link(df_download)
    st.markdown(linko, unsafe_allow_html=True)

    st.header("Le contee con la maggior percentuale a favore")
    option = st.selectbox(
        'Di quale candidato vuoi vedere le percentuali?',
        elections['candidate'].unique()
    )
    st.subheader("Percentuali di " + option)
    df_percentage_download = srv.calculate_percentage_votes_by_county(elections,option)
    row_number = st.slider("Quante contee vuoi visualizzare?", min_value=1 ,max_value=len(df_percentage_download), step=1)
    st.dataframe(df_percentage_download[:row_number])
    linko =srv.get_table_download_link(df_percentage_download)
    st.markdown(linko, unsafe_allow_html=True)

    st.header("Le contee con il maggior numero di voti a favore dei candidati non facenti parte del Partito Democratico e Partito Repubblicano")

    democratics_and_republicans = ['Democratic Party', 'Republican Party']
    not_dem_and_rep = elections.loc[~elections.party.isin(democratics_and_republicans), ['STATENAME', 'county', 'votes']].groupby(['STATENAME', 'county'], as_index = False).sum()
    tot = elections.groupby(['STATENAME', 'county'], as_index = False).sum()
    not_dem_and_rep['tot_votes'] = tot['votes']
    not_dem_and_rep['percentage_votes'] = (not_dem_and_rep['votes']/tot['votes'])*100
    sorted_by_percentage = st.checkbox('Ordina per percentuale', key=1)
    if sorted_by_percentage:
        df_county_download = not_dem_and_rep.sort_values('percentage_votes', ascending = False).reset_index(drop = True)
    else:
        df_county_download = not_dem_and_rep.sort_values('votes', ascending = False).reset_index(drop = True)
    number_counties = st.slider('Numero di contee', min_value=1, max_value=len(df_county_download), value = 100 ,step=1)
    st.dataframe(df_county_download[:number_counties])
    linko =srv.get_table_download_link(df_county_download[:number_counties])
    st.markdown(linko, unsafe_allow_html=True)

    st.header("Gli Stati con il maggior numero di contee a favore di Donald J. Trump")
    counties_by_states = elections[elections.candidate == 'Donald J. Trump'].groupby('STATENAME').size().reset_index(name='tot_county')
    max_votes_by_county = elections.groupby(['STATENAME', 'county'])['votes'].transform(max) == elections['votes']
    counties_in_favor = elections[max_votes_by_county][elections[max_votes_by_county].candidate == 'Donald J. Trump'].groupby('STATENAME').size().reset_index(name='in_favor')
    counties_in_favor = pd.merge(counties_by_states, counties_in_favor, how = 'inner')
    counties_in_favor['percentage_in_favor'] = round((counties_in_favor['in_favor'] / counties_in_favor['tot_county'])*100, 1)
    sorted_by_percentage = st.checkbox('Ordina per percentuale', key=2)
    if sorted_by_percentage:
        counties_in_favor = counties_in_favor.sort_values('percentage_in_favor', ascending = False)
    else:
        counties_in_favor = counties_in_favor.sort_values('in_favor', ascending = False)
    states_trump = st.slider('Quanti stati vuoi vedere?', min_value=1, max_value= len(counties_in_favor), value= 3 ,step=1, key=2)
    st.dataframe(counties_in_favor[:states_trump].reset_index(drop = True))
    linko =srv.get_table_download_link(counties_in_favor[:states_trump])
    st.markdown(linko, unsafe_allow_html=True)
    
    st.header("Gli Stati con il maggior numero di contee a favore di Hillary Clinton")
    max_votes_by_county = elections.groupby(['STATENAME', 'county'])['votes'].transform(max) == elections['votes']
    counties_in_favor = elections[max_votes_by_county][elections[max_votes_by_county].candidate == 'Hillary Clinton'].groupby('STATENAME').size().reset_index(name='in_favor')
    counties_in_favor = pd.merge(counties_by_states, counties_in_favor, how = 'inner')
    counties_in_favor['percentage_in_favor'] = round((counties_in_favor['in_favor'] / counties_in_favor['tot_county'])*100,1)
    counties_in_favor = counties_in_favor.sort_values('percentage_in_favor', ascending = False)
    sorted_by_percentage = st.checkbox('Ordina per percentuale', key=3)
    if sorted_by_percentage:
        counties_in_favor = counties_in_favor.sort_values('percentage_in_favor', ascending = False)
    else:
        counties_in_favor = counties_in_favor.sort_values('in_favor', ascending = False)
    states_clinton = st.slider('Quanti stati vuoi vedere?', min_value=1, max_value= len(counties_in_favor), value= 3, step=1, key=3)
    st.dataframe(counties_in_favor[:states_clinton].reset_index(drop = True))
    linko =srv.get_table_download_link(counties_in_favor[:states_clinton])
    st.markdown(linko, unsafe_allow_html=True)
