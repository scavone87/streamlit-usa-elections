import streamlit as st
import elections
import demography
import pro_capite
import correlazioni

PAGES = {
    "Elezioni": elections,
    "Demografia": demography,
    "Pro-Capite": pro_capite,
    "Correlazioni": correlazioni
}
st.sidebar.title('Navigazione')
selection = st.sidebar.radio("vai", list(PAGES.keys()))
page = PAGES[selection]
page.app()
