import streamlit as st
from PIL import Image
import services as srv


st.set_page_config(page_title='Election USA 2016', page_icon=srv.getIconPage(), layout='centered', initial_sidebar_state='auto')



demography = srv.load_dataset('datasets/cc-est2019-alldata-gruppo-4.csv')
st.write(" # Demografia USA Elezioni 2016")
st.header("Vedi le contee con la maggior percentuale di cittadini dell'etnia scelta")
race_map = srv.race_map
race_selected = st.selectbox(
    'Scegli la razza',
    list(race_map.keys())
)
year_map = srv.year_census_map
year = st.selectbox(
    'Scegli un anno',
    list(year_map.keys()),
    index=8
)

agegrp_map = srv.agegrp_map
agegrp = st.selectbox(
    "Scegli una fascia d'età",
    list(agegrp_map.keys())
)

data = srv.calculate_percentage_race_by_county(demography, race_map[race_selected], agegrp=agegrp_map[agegrp], year=year_map[year]).reset_index(drop = True)
data = data.rename(columns={race_map[race_selected]: race_selected + ' percentage'})

row_number = st.slider(
    "Quante contee vuoi visualizzare?",
    min_value=1,
    max_value=len(data), 
    value=50, 
    step=1
)

st.dataframe(data[:row_number])
linko = srv.get_table_download_link(data[:row_number])
st.markdown(linko, unsafe_allow_html=True)
