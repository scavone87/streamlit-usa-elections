import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import services as srv

def app():
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

    votes_and_procapite_by_candidate = votes_and_procapite[votes_and_procapite.candidate == selected_candidate]
    st.dataframe(votes_and_procapite_by_candidate)
    value = st.checkbox("Rendi interattivo il grafico")
    if value == True:
        c = alt.Chart(votes_and_procapite_by_candidate).mark_circle().encode(alt.X(
            '2016', title="Reddito Pro Capite 2016",scale=alt.Scale(zero=False)), alt.Y('percentage_votes', title=selected_candidate + " votes"),scale=alt.Scale(zero=False)).interactive()
    else:
        c = alt.Chart(votes_and_procapite_by_candidate).mark_circle().encode(alt.X(
            '2016', title="Reddito Pro Capite 2016",scale=alt.Scale(zero=False)), alt.Y('percentage_votes', title=selected_candidate + " votes",scale=alt.Scale(zero=False)))
    st.altair_chart(c, use_container_width=True)
    st.write("Coefficiente di correlazione: ", srv.get_corr_coef_for_candidate(selected_candidate, votes_and_procapite, '2016', 'percentage_votes'))

    st.subheader("Esiste una correlazione tra il reddito procapite di uno stato e la vittoria di un determinato candidato?")

    votes_and_procapite_winners = srv.get_votes_and_procapite_by_winner(elections, pro_capite)
    st.dataframe(votes_and_procapite_winners)

    points = alt.Chart(votes_and_procapite_winners).mark_point().encode(
        alt.X(
            '2016',
            title="Reddito Pro Capite 2016",
            scale=alt.Scale(zero=False)
        ),
        alt.Y(
            'percentage_votes',
            title= "Percentuale voti dei vincitori",
            scale=alt.Scale(zero=False)
        ),
        color=alt.Color('candidate', sort='descending')
    ).configure_point(
        size=100
    )

    st.altair_chart(points, use_container_width=True)

    for candidate in votes_and_procapite_winners.candidate.unique():
            st.write(
                "Coefficiente di correlazione per ", 
                candidate + " :" ,
                srv.get_corr_coef_for_candidate(candidate, votes_and_procapite_winners, '2016', 'percentage_votes')
            )

    st.subheader("Esiste una correlazione tra la percentuale di cittadini di una determinata razza di una contea e il voto a un determinato candidato?")

    race_map = srv.race_map
    race_selected = st.selectbox(
        'Scegli la razza',
        list(race_map.keys()),
        key=1
    )

    year_map = srv.year_census_map
    year = st.selectbox(
        'Scegli un anno',
        list(year_map.keys()),
        index=8,
        key = 1
    )

    agegrp_map = srv.agegrp_map
    agegrp = st.selectbox(
        "Scegli una fascia d'età",
        list(agegrp_map.keys()),
        key = 1
    )

    race_and_votes = srv.get_elections_and_race_by_county(elections, demography, race_map[race_selected], agegrp= agegrp_map[agegrp], year= year_map[year])
    race_and_votes.drop(columns=['STNAME','CTYNAME', 'COUNTY'], inplace = True)
    candidate = st.selectbox(
        'Scegli un candidato di cui vuoi verificare la correlazione',
        elections['candidate'].unique()
    )
    race_and_votes = race_and_votes[race_and_votes.candidate == candidate]
    race_and_votes = race_and_votes.rename(columns={ race_map[race_selected] : race_selected})

    st.dataframe(race_and_votes)
    interactive = st.checkbox("Rendi interattivo il grafico", key= bool)
    if interactive == True:
        percentage_race_graphics = alt.Chart(race_and_votes).mark_circle().encode(alt.X(
            race_selected, title="Percentage of " + race_selected, scale=alt.Scale(zero=False)), alt.Y('percentage_votes', title=candidate + "percentage votes", scale=alt.Scale(zero=False))).interactive()
    else:
        percentage_race_graphics = alt.Chart(race_and_votes).mark_circle().encode(alt.X(
            race_selected, title="Percentage of " + race_selected, scale=alt.Scale(zero=False)), alt.Y('percentage_votes', title=candidate + "percentage votes", scale=alt.Scale(zero=False)))
    st.altair_chart(percentage_race_graphics, use_container_width=True)
    st.write("Coefficiente di correlazione: ", srv.get_corr_coef_for_candidate(
        candidate, race_and_votes, race_selected, 'percentage_votes'))

    st.subheader("Esiste una correlazione tra la percentuale di cittadini di una determinata razza di uno stato e il voto a un determinato candidato?")

    race_selected = st.selectbox(
        'Scegli la razza ',
        list(race_map.keys()),
        key = 2
    )

    year_map = srv.year_census_map
    year = st.selectbox(
        'Scegli un anno',
        list(year_map.keys()),
        index=8,
        key = 2
    )

    agegrp_map = srv.agegrp_map
    agegrp = st.selectbox(
        "Scegli una fascia d'età",
        list(agegrp_map.keys()),
        key = 2
    )    

    candidate = st.selectbox(
        'Scegli un candidato di cui vuoi verificare la correlazione ',
        elections['candidate'].unique()
    )
    race_and_votes_state = srv.get_elections_and_race_by_state(elections, demography, race_map[race_selected], agegrp= agegrp_map[agegrp], year= year_map[year])
    race_and_votes_state = race_and_votes_state.loc[race_and_votes_state.candidate == candidate, ['STATENAME', 'candidate', 'percentage_votes', 'TOT_POP', race_map[race_selected]]]
    race_and_votes_state = race_and_votes_state.rename(columns={race_map[race_selected] : race_selected})
    st.dataframe(race_and_votes_state)
    interactive = st.checkbox("Rendi il grafico interattivo")
    if interactive == True:
        percentage_race_state_graphics = alt.Chart(race_and_votes_state).mark_circle().encode(alt.X(
            race_selected, title="Percentage of " + race_selected, scale=alt.Scale(zero=False)), alt.Y('percentage_votes', title=candidate + " votes", scale=alt.Scale(zero=False))).interactive()
    else:
        percentage_race_state_graphics = alt.Chart(race_and_votes_state).mark_circle().encode(alt.X(
            race_selected, title="Percentage of " + race_selected, scale=alt.Scale(zero=False)), alt.Y('percentage_votes', title=candidate + " votes", scale=alt.Scale(zero=False)))
    st.altair_chart(percentage_race_state_graphics, use_container_width=True)
    st.write("Coefficiente di correlazione: ", srv.get_corr_coef_for_candidate(
        candidate, race_and_votes_state, race_selected, 'percentage_votes'))

    st.subheader('Correlazione tra i voti di un candidato in una contea e i voti ottenuti nelle contee confinanti')
    demography_filtered = demography[(demography.AGEGRP == 0) & (demography.YEAR == 9)]
    demography_filtered = demography_filtered[['STNAME', 'COUNTY','TOT_POP']]
    df_elections = pd.merge(elections, demography_filtered, how = "inner", left_on = ['STATENAME','COUNTYFP'], right_on = ['STNAME','COUNTY'])
    df_elections.drop(columns = ['COUNTY', 'STNAME'], inplace = True)
    df_elections = df_elections.dropna(subset=['NEIGHBORS'])
    df_elections['weighted votes'] = 0
    df_elections = srv.calculate_weighted_votes(df_elections)
    candidate = st.selectbox(
        'Scegli un candidato di cui vuoi verificare la correlazione ',
        df_elections['candidate'].unique(),
        key=2
    )
    df_elections = df_elections[df_elections.candidate == candidate]
    st.dataframe(df_elections)
    interactive = st.checkbox("Rendi il grafico interattivo", key = 2)
    if interactive == True:
        df_elections_graphics = alt.Chart(df_elections).mark_circle().encode(alt.X(
            'votes', title="votes", scale=alt.Scale(zero=False)), alt.Y('weighted votes', title="weighted votes counties", scale=alt.Scale(zero=False))).interactive()
    else:
        df_elections_graphics = alt.Chart(df_elections).mark_circle().encode(alt.X(
            'votes', title="votes", scale=alt.Scale(zero=False)), alt.Y('weighted votes', title="weighted votes counties", scale=alt.Scale(zero=False)))
    st.altair_chart(df_elections_graphics, use_container_width=True)
    st.write("Coefficiente di correlazione: ", srv.get_corr_coef_for_candidate(candidate, df_elections, 'votes', 'weighted votes'))
    
    st.subheader('Correlazione tra la percentuale di donne stimate nel 2016 di uno stato e i voti ottenuti dai Vincitori')

    winner = st.selectbox(
        'Scegli un vincitore',
        ['Donald J. Trump', 'Hillary Clinton']
    )

    percentage_female,y = srv.calculate_percentage_woman(demography, elections, winner)
    df_elections_graphics = pd.DataFrame({'percentage_female': percentage_female.to_list(), 'votes': y.to_list()})
    interactive = st.checkbox("Rendi il grafico interattivo", key = 3)
    if interactive == True:
        df_elections_graphics = alt.Chart(df_elections_graphics).mark_circle().encode(alt.X(
            'percentage_female', title="percentage_female", scale=alt.Scale(zero=False)), alt.Y('votes', title="votes"), scale=alt.Scale(zero=False)).interactive()
    else:
        df_elections_graphics = alt.Chart(df_elections_graphics).mark_circle().encode(alt.X(
            'percentage_female', title="percentage_female", scale=alt.Scale(zero=False)), alt.Y('votes', title="votes", scale=alt.Scale(zero=False)))
    st.altair_chart(df_elections_graphics, use_container_width=True)
    st.write('Coefficiente di correlazione: ', np.corrcoef(percentage_female,y)[1,0])






    st.subheader('Correlazione tra la percentuale di donne afroamericane stimate nel 2016 di uno stato e i voti ottenuti dai Vincitori')

    winner = st.selectbox(
        'Scegli un vincitore',
        ['Donald J. Trump', 'Hillary Clinton'],
        key=2
    )

    percentage_female,y = srv.calculate_percentage_woman(demography, elections, winner, race='BA_FEMALE')
    df_elections_graphics = pd.DataFrame({'percentage_female': percentage_female.to_list(), 'votes': y.to_list()})
    interactive = st.checkbox("Rendi il grafico interattivo", key = 4)
    if interactive == True:
        df_elections_graphics = alt.Chart(df_elections_graphics).mark_circle().encode(alt.X(
            'percentage_female', title="percentage afroamerican female", scale=alt.Scale(zero=False)), alt.Y('votes', title="votes"), scale=alt.Scale(zero=False)).interactive()
    else:
        df_elections_graphics = alt.Chart(df_elections_graphics).mark_circle().encode(alt.X(
            'percentage_female', title="percentage afroamerican female", scale=alt.Scale(zero=False)), alt.Y('votes', title="votes", scale=alt.Scale(zero=False)))
    st.altair_chart(df_elections_graphics, use_container_width=True)
    st.write('Coefficiente di correlazione: ', np.corrcoef(percentage_female,y)[1,0])