import streamlit as st
from PIL import Image
import os



# Ottenere il percorso del file relativo allo script corrente
current_dir = os.path.dirname(os.path.abspath(__file__))

# Costruire il percorso del file immagine utilizzando os.path.join
image_path = os.path.join(current_dir, 'imgs', 'united-states.png')

# Aprire l'immagine utilizzando il percorso corretto
im = Image.open(image_path)
st.set_page_config(page_title='Election USA 2016', page_icon=im, layout='centered', initial_sidebar_state='auto')

st.write("## Benvenuto nella mia app di analisi dati sulle elezioni USA 2016! 👋")

st.sidebar.success("Navigazione")
