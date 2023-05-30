import streamlit as st
import services as srv


pro_capite = srv.load_dataset('datasets/CAINC1__1969_2019-Percapitapersonalincome(dollars)2.csv', "(NA)")
st.write(" # Reddito Pro Capite delle Contee")

sorting = st.selectbox(
    'Calcolare il minimo o il massimo reddito pro capite?',
    ['Massimo', 'Minimo']
)

year_list = [i for i in range(1969,2020)]
year_list.append("Average")

anno = st.selectbox(
    'Anno di interesse',
    year_list,
    index=len(year_list)-1
)

if sorting == 'Massimo':
    sorting = False
else:
    sorting = True
anno = str(anno)
data = srv.calculate_pro_capite(pro_capite,sorting,year=anno)
value = st.slider('Numero di contee', min_value=1, max_value = len(data), value = 50 ,step=1)
st.dataframe(data[:value])
linko =srv.get_table_download_link(data[:value])
st.markdown(linko, unsafe_allow_html=True)
