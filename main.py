import streamlit as st
from PIL import Image


im = Image.open("imgs\\united-states.png")
st.set_page_config(page_title='Election USA 2016', page_icon=im, layout='centered', initial_sidebar_state='auto')

st.write("## Benvenuto nella mia app di analisi dati sulle elezioni USA 2016! 👋")

st.sidebar.success("Navigazione")
