import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import streamlit.components.v1 as components

st.set_page_config(page_title='UNGLI institutionsøkonomi analyse', page_icon="appikon.jpg", layout='centered', initial_sidebar_state="expanded")



file = filename = 'Regnskabsdata.XLS'
st.sidebar.subheader('Indlæs din regnskabsdata fil')
uploaded_file = st.sidebar.file_uploader("Downloades fra https://regnskabsportal.uvm.dk/Accounts/Search.aspx?sm=4.1")#, type = 'xlsx')
st.sidebar.subheader('Indtast UNGLI information')
UNGLI_belob = st.sidebar.number_input('Indtast det beløb institutionen bruger på UNGLI licenser (findes i ConsortiaManager)')

if uploaded_file is not None:
    file = uploaded_file
    filename = uploaded_file.name

def load_data(file):
    #st.write("Ny fil indlæst")
    return pd.read_excel(file, skiprows = 4, usecols = [1,4,5])

st.title('UNGLI institutionsøkonomi analyse')
st.write('Formålet med denne lille app er at give et hurtigt overblik over hvor meget UNGLI licenser fylder i budgettet for en given institution.')
st.write('For at bruge appen skal du have en fil trukket fra Regnskabsportalen i .XLS format samt et estimat af hvor mange penge institutionen bruger på UNGLI licenser (dette kan formentlig aflæses i ConsortiaManager)')
st.write('Upload og indtast informationen til venstre.')

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

metrik1 = np.round(UNGLI_belob/gennemforelse*100,3)

metrik2 = np.round(UNGLI_belob/taxameter*100,3)

metrik3 = np.round(gennemforelse/taxameter*100,3)

st.subheader('Analyse af ' + inst_navn + ', institutionsnummer: ' + str(inst_num))

st.metric('Andel af "Undervisningens gennemførelse, øvrige omkostninger" der består af UNGLI licenser:', value = str(metrik1)+ "%")
st.metric('Andel af undervisningstaxameter der består af UNGLI licenser:', value = str(metrik2) + "%")
st.metric('Andel af undervisningstaxameter der består af "Undervisningens gennemførelse, øvrige omkostninger":', value = str(metrik3) + "%")

#st.balloons()
