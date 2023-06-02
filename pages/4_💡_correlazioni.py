import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from PIL import Image

import os

import services as srv


# Ottenere il percorso del file relativo allo script corrente
current_dir = os.path.dirname(os.path.abspath(__file__))

# Costruire il percorso del file immagine utilizzando os.path.join
image_path = os.path.join(current_dir, 'imgs', 'united-states.png')

# Aprire l'immagine utilizzando il percorso corretto
im = Image.open(image_path)
st.set_page_config(page_title='Election USA 2016', page_icon=im, layout='centered', initial_sidebar_state='auto')

st.title("Correlazioni")

elections = srv.load_dataset('datasets/election_group4_mod.csv')
pro_capite = srv.load_dataset('datasets/CAINC1__1969_2019-Percapitapersonalincome(dollars)2.csv', "(NA)")
demography = srv.load_dataset('datasets/cc-est2019-alldata-gruppo-4.csv')
demography['CTYNAME'] = demography['CTYNAME'].str.replace(" County", "")
demography['CTYNAME'] = demography['CTYNAME'].str.replace(" city", "City")

st.subheader("Esiste una correlazione tra il reddito procapite di una contea e il voto a un determinato candidato?")

votes_and_procapite = srv.get_votes_and_procapite_dataset(pro_capite, elections)


selected_candidate = st.selectbox(
    'Di quale candidato vuoi vedere le percentuali?',
    votes_and_procapite['candidate'].unique()
)

votes_and_procapite_by_candidate = votes_and_procapite[votes_and_procapite.candidate == selected_candidate].reset_index(drop = True)
st.dataframe(votes_and_procapite_by_candidate)

if selected_candidate is not None:
    title = selected_candidate + " percentage votes"
else:
    title = "Selected Candidate percentage votes"

c = alt.Chart(votes_and_procapite_by_candidate).mark_circle().encode(
    alt.X(
        '2016',
        title="Pro Capite 2016", 
        scale=alt.Scale(zero=False)
    ), 
    alt.Y(
        'percentage_votes', 
        title=title, 
        scale=alt.Scale(zero=False)
    ), 
    tooltip=['state','county'], 
    color=alt.Color('state')
).interactive()


st.altair_chart(c, use_container_width=True)
st.write("Coefficiente di correlazione: ", srv.get_corr_coef_for_candidate(selected_candidate, votes_and_procapite, '2016', 'percentage_votes'))

st.subheader("Esiste una correlazione tra il reddito procapite di uno stato e la vittoria di un determinato candidato?")

votes_and_procapite_winners = srv.get_votes_and_procapite_by_winner(elections, pro_capite)
st.dataframe(votes_and_procapite_winners)

points = alt.Chart(votes_and_procapite_winners).mark_point().encode(
    alt.X(
        'mean_pro_capite',
        title="Pro Capite 2016",
        scale=alt.Scale(zero=False)
    ),
    alt.Y(
        'percentage_votes',
        title= "Percentage votes of winners",
        scale=alt.Scale(zero=False)
    ),
    color=alt.Color('candidate', sort='descending', scale=alt.Scale(range=['#1f77b4', '#ff7f0e'])), # Qui puoi specificare la gamma di colori.
    tooltip = ['state']
).configure_point(
    size=100
)
st.altair_chart(points, use_container_width=True)

for candidate in votes_and_procapite_winners.candidate.unique():
        st.write("Coefficiente di correlazione per ", candidate + " :" ,srv.get_corr_coef_for_candidate(candidate, votes_and_procapite_winners, 'mean_pro_capite', 'percentage_votes'))


st.subheader("Esiste una correlazione tra la percentuale di cittadini di una determinata razza di una contea e il voto a un determinato candidato?")

race_map = srv.race_map
race_selected = st.selectbox(
    'Scegli la razza',
    list(race_map.keys()),
    key=bytes('race1', 'utf-8')
)

year_map = srv.year_census_map
year = st.selectbox(
    'Scegli un anno',
    list(year_map.keys()),
    index=8,
    key = bytes('year1', 'utf-8')
)

agegrp_map = srv.agegrp_map
agegrp = st.selectbox(
    "Scegli una fascia d'età",
    list(agegrp_map.keys()),
    key = bytes('agegrp1', 'utf-8')
)

race_and_votes = srv.get_elections_and_race_by_county(elections, demography, race_map[race_selected], agegrp= agegrp_map[agegrp], year= year_map[year])
race_and_votes.drop(columns=['STNAME','CTYNAME', 'COUNTY'], inplace = True)
candidate = st.selectbox(
    'Scegli un candidato di cui vuoi verificare la correlazione',
    elections['candidate'].unique()
)
race_and_votes = race_and_votes[race_and_votes.candidate == candidate]
race_and_votes = race_and_votes.rename(columns={ race_map[race_selected] : race_selected}).reset_index(drop = True)

st.dataframe(race_and_votes)
percentage_race_graphics = alt.Chart(race_and_votes).mark_circle().encode(
    alt.X(
        race_selected, 
        title="Percentage of " + race_selected, 
        scale=alt.Scale(zero=False)
    ), 
    alt.Y(
        'percentage_votes', 
        title=candidate + " percentage votes", 
        scale=alt.Scale(zero=False)
    ),  
    color = alt.Color('STATENAME'), 
    tooltip = ['STATENAME','county']
).interactive()

st.altair_chart(percentage_race_graphics, use_container_width=True)

st.write("Coefficiente di correlazione: ", srv.get_corr_coef_for_candidate(candidate, race_and_votes, race_selected, 'percentage_votes'))
st.write("Coef. di correlazione di Spearman:", srv.spearman_correlation(race_and_votes, race_selected, 'percentage_votes'))


chart = alt.Chart(race_and_votes).mark_bar().encode(
    x=alt.X('percentage_votes:Q', title='Percentuale Voti'),
    y=alt.Y(race_selected, title='Popolazione Razza'),
    color=alt.Color('candidate:N', legend=None)
    ).interactive().properties(
        width=600,
        height=400
    )

st.altair_chart(chart, use_container_width=True)
st.write("Coef. di correlazione di Kendall: ", srv.kendall_correlation(race_and_votes, race_selected, 'percentage_votes'))


st.subheader("Esiste una correlazione tra la percentuale di cittadini di una determinata razza di uno stato e il voto a un determinato candidato?")

race_selected = st.selectbox(
    'Scegli la razza ',
    list(race_map.keys()),
    key = bytes('race2', 'utf-8')
)

year_map = srv.year_census_map
year = st.selectbox(
    'Scegli un anno',
    list(year_map.keys()),
    index=8,
    key = bytes('year2', 'utf-8')
)

agegrp_map = srv.agegrp_map
agegrp = st.selectbox(
    "Scegli una fascia d'età",
    list(agegrp_map.keys()),
    key = bytes('agegrp2', 'utf-8')
)    

candidate = st.selectbox(
    'Scegli un candidato di cui vuoi verificare la correlazione ',
    elections['candidate'].unique()
)
race_and_votes_state = srv.get_elections_and_race_by_state(elections, demography, race_map[race_selected], agegrp= agegrp_map[agegrp], year= year_map[year])

race_and_votes_state = race_and_votes_state.loc[race_and_votes_state.candidate == candidate, ['STATENAME', 'candidate', 'percentage_votes', 'TOT_POP', race_map[race_selected]]]
race_and_votes_state = race_and_votes_state.rename(columns={race_map[race_selected] : race_selected}).reset_index(drop = True)
st.dataframe(race_and_votes_state)
percentage_race_state_graphics = alt.Chart(race_and_votes_state).mark_circle().encode(
    alt.X(
        race_selected, 
        title="Percentage of " + race_selected, 
        scale=alt.Scale(zero=False)
    ), 
    alt.Y(
        'percentage_votes', 
        title=candidate + " percentage votes", 
        scale=alt.Scale(zero=False)
    ),   
    color = alt.Color("STATENAME") ,
    tooltip = ['STATENAME']
).interactive()

st.altair_chart(percentage_race_state_graphics, use_container_width=True)
st.write("Coefficiente di correlazione: ", srv.get_corr_coef_for_candidate(candidate, race_and_votes_state, race_selected, 'percentage_votes'))
st.write("Coef. di correlazione di Spearman:", srv.spearman_correlation(race_and_votes_state, race_selected, 'percentage_votes'))

chart = alt.Chart(race_and_votes_state).mark_bar().encode(
x=alt.X('percentage_votes:Q', title='Percentuale Voti'),
y=alt.Y(race_selected, title='Popolazione Razza'),
color=alt.Color('candidate:N', legend=None)
).interactive().properties(
    width=600,
    height=400
)

st.altair_chart(chart, use_container_width=True)
st.write("Coef. di correlazione di Kendall: ", srv.kendall_correlation(race_and_votes_state, race_selected, 'percentage_votes'))


st.subheader('Correlazione tra i voti di un candidato in una contea e i voti ottenuti nelle contee confinanti')
demography_filtered = demography[(demography.AGEGRP == 0) & (demography.YEAR == 9)]
demography_filtered = demography_filtered[['STNAME', 'COUNTY','TOT_POP']]
df_elections = pd.merge(elections, demography_filtered, how = "inner", left_on = ['STATENAME','COUNTYFP'], right_on = ['STNAME','COUNTY'])
df_elections.drop(columns = ['COUNTY', 'STNAME'], inplace = True)
df_elections = df_elections.dropna(subset=['NEIGHBORS'])
df_elections = srv.calculate_weighted_votes(df_elections)

candidate = st.selectbox(
    'Scegli un candidato di cui vuoi verificare la correlazione ',
    df_elections['candidate'].unique(),
    key=bytes('candidiate2', 'utf-8')
)

df_elections = df_elections[df_elections.candidate == candidate]
st.dataframe(df_elections.reset_index(drop = True))
df_elections_graphics = alt.Chart(df_elections).mark_circle().encode(
    alt.X(
        'votes', 
        title="counties votes", 
        scale=alt.Scale(zero=False)
    ), 
    alt.Y(
        'weighted_votes', 
        title="weighted votes from neighboring counties", 
        scale=alt.Scale(zero=False)
    ), 
    color = alt.Color('STATENAME'),
    tooltip = ['STATENAME','county']
).interactive()

st.altair_chart(df_elections_graphics, use_container_width=True)
st.write("Coefficiente di correlazione: ", srv.get_corr_coef_for_candidate(candidate, df_elections, 'votes', 'weighted_votes'))
st.write("Coef. di correlazione di Spearman:", srv.spearman_correlation(df_elections, 'votes', 'weighted_votes'))

chart = alt.Chart(df_elections).mark_bar().encode(
x=alt.X('votes:Q', title='counties votes'),
y=alt.Y('weighted_votes', title='Weighted votes from neighboring counties'),
color=alt.Color('candidate:N', legend=None)
).interactive().properties(
    width=600,
    height=400
)

st.altair_chart(chart, use_container_width=True)

st.write("Coef. di correlazione di Kendall: ", srv.kendall_correlation(df_elections, 'votes', 'weighted_votes'))


st.subheader('Correlazione tra la percentuale di donne stimate nel 2016 di uno stato e i voti ottenuti dai Vincitori')

winner = st.selectbox(
    'Scegli un vincitore',
    ['Donald J. Trump', 'Hillary Clinton']
)

percentage_female,y = srv.calculate_percentage_woman(demography, elections, winner)
df_elections_graphics = pd.DataFrame({'percentage_female': percentage_female.to_list(), 'votes': y.to_list()})    
df_elections_graphics = alt.Chart(df_elections_graphics).mark_circle().encode(
    alt.X(
        'percentage_female', 
        title="percentage_female", 
        scale=alt.Scale(zero=False)
    ), 
    alt.Y(
        'votes', 
        title="percentage votes", 
        scale=alt.Scale(zero=False)
    )
).interactive()

st.altair_chart(df_elections_graphics, use_container_width=True)
st.write('Coefficiente di correlazione: ', np.corrcoef(percentage_female,y)[1,0])

st.subheader('Correlazione tra la percentuale di donne afroamericane stimate nel 2016 di uno stato e i voti ottenuti dai Vincitori')

winner = st.selectbox(
    'Scegli un vincitore',
    ['Donald J. Trump', 'Hillary Clinton'],
    key=bytes('winner2', 'utf-8')
)

percentage_female,y = srv.calculate_percentage_woman(demography, elections, winner, race='BA_FEMALE')
df_elections_graphics = pd.DataFrame({'percentage_female': percentage_female.to_list(), 'votes': y.to_list()})
df_elections_graphics = alt.Chart(df_elections_graphics).mark_circle().encode(
    alt.X(
        'percentage_female', 
        title="percentage afroamerican female", 
        scale=alt.Scale(zero=False)
    ), 
    alt.Y(
        'votes', 
        title="percentage votes", 
        scale=alt.Scale(zero=False)
    )
).interactive()

st.altair_chart(df_elections_graphics, use_container_width=True)
st.write('Coefficiente di correlazione: ', np.corrcoef(percentage_female,y)[1,0])