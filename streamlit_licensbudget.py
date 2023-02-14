import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
#import streamlit.components.v1 as components

st.set_page_config(page_title='Dyvekes UNGLI app', page_icon="appikon.jpg", layout='centered', initial_sidebar_state="expanded")



file = filename = 'Regnskabsdata.XLS'
st.sidebar.subheader('Indlæs din regnskabsdata fil')
uploaded_file = st.sidebar.file_uploader("Skal være excel fil")#, type = 'xlsx')
st.sidebar.subheader('Indtast UNGLI information')
UNGLI_belob = st.sidebar.number_input('Indtast det beløb institutionen bruger på UNGLI licenser (findes i ConsortiaManager)')

if uploaded_file is not None:
    file = uploaded_file
    filename = uploaded_file.name

def load_data(file):
    st.write("Ny fil indlæst")
    return pd.read_excel(file, skiprows = 4, usecols = [1,4])

st.header('Analyserer fil "' + filename + '"')

df = load_data(file)
#transponér så rækker fra excel passer med kolonner i pandas
df = df.T
#definér rækken som kolonnenavne, og fjern dernæst rækken som "datarække"
df.columns = df.iloc[0]
df = df.drop(df.index[0])

### data manipulering, hent info vi skal bruge ###
#institutionsnummer og navn
inst_num = df.iloc[0]['Institutions nummer:']
inst_navn = df.iloc[0][1]

#Taxameter
taxameter = df.iloc[0]['Undervisningstaxameter']

#undervisningsgennemførelse, budgettet licenser kommer fra?
gennemforelse = df.iloc[0]['Undervisningens gennemførelse , Øvrige omkostninger']

### Vi vil gerne have tre metrikker: 
## 1) udgift til UNGLI divideret med "Undervisningens gennemførelse..."
## 2) udgift til UNGLI divideret med undervisningstaxameter
## 3) Undervisningens gennemførelse divideret med taxameter

metrik1 = UNGLI_belob/gennemforelse*100

metrik2 = UNGLI_belob/taxameter*100

metrik3 = gennemforelse/taxameter*100

col1, col2, col3 = st.columns(3)
col1.metric('Andel af "Undervisningens gennemførelse, øvrige omkostninger" der består af UNGLI licenser', value = str(metrik1)+ "%")
col2.metric('Andel af undervisningstaxameter der består af UNGLI licenser', value = str(metrik2) + "%")
col3.metric('Andel af undervisningstaxameter der består af "Undervisningens gennemførelse, øvrige omkostninger"', value = str(metrik3) + "%")

st.ballons()
