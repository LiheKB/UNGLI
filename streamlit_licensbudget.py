import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import streamlit.components.v1 as components

st.set_page_config(page_title='UNGLI institutionsøkonomi analyse', page_icon="appikon.jpg", layout='centered', initial_sidebar_state="expanded")

file = filename = 'Regnskabsdata.XLS'
st.sidebar.subheader('Indlæs din regnskabsdata fil')
uploaded_files = st.sidebar.file_uploader("Downloades fra https://regnskabsportal.uvm.dk/Accounts/Search.aspx?sm=4.1", accept_multiple_files=True)#, type = 'xlsx')
antal_inst = int(st.sidebar.number_input('Indtast antal institutioner i filen', min_value = 1))
st.sidebar.subheader('Indtast UNGLI information')
UNGLI_belob = st.sidebar.number_input('Indtast det beløb institutionen bruger på UNGLI licenser (findes i ConsortiaManager)')

#if uploaded_file is not None:
#    file = uploaded_file
#    filename = uploaded_file.name

def load_multiple(file, num_inst = antal_inst):
    start_cols = [1]
    mult_cols = np.arange(start = 4, stop = 4 + num_inst)
    mult_cols = np.append(start_cols, mult_cols)
    return pd.read_excel(file, skiprows=4, usecols = mult_cols)

def load_data(file):
    return pd.read_excel(file, skiprows = 4, usecols = [1,4])

st.title('UNGLI institutionsøkonomi analyse')
st.write('Formålet med denne lille app er at give et hurtigt overblik over hvor meget UNGLI licenser fylder i budgettet for en given institution.')
st.write('For at bruge appen skal du have en fil trukket fra Regnskabsportalen i .XLS format samt et estimat af hvor mange penge institutionen bruger på UNGLI licenser (dette kan formentlig aflæses i ConsortiaManager)')
st.write('Upload og indtast informationen til venstre.')

if uploaded_files is not None:
    st.write("Ny fil uploadet.")
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        file = uploaded_file
        st.header('Analyserer fil "' + filename + '"')
        ##her går den i ståå??
        df = load_multiple(file)
        #transponér så rækker fra excel passer med kolonner i pandas
        df = df.T
        #definér rækken som kolonnenavne, og fjern dernæst rækken som "datarække"
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        CM_info = pd.DataFrame([
            {"institutionsnummer" : (df['Institutions nummer:']).to_numpy(), 
            "institutionsnavn" : (df.iloc[:,1]).to_numpy(),
            'CM beløb' : np.ones(antal_inst)}
        ])

        edited_CM = st.data_editor(CM_info, column_config={
        "institutionsnummer": "Institutions nummer",
        "institutionsnavn": "Institutions navn",
        "CM beløb": st.column_config.NumberColumn(
            "UNGLI beløb",
            help="Indtast antal kroner brugt på UNGLI licenser.",
            min_value=1,
        ),
        }, hide_index = True,
    )
        ### data manipulering, hent info vi skal bruge ###
        #institutionsnummer og navn
        inst_num = df['Institutions nummer:']
        inst_navn = df.iloc[:,1]
        #Taxameter
        taxameter = (df['Undervisningstaxameter']).to_numpy()

        #undervisningsgennemførelse, budgettet licenser kommer fra?
        gennemforelse = (df['Undervisningens gennemførelse , Øvrige omkostninger']).to_numpy()
        alle_CM = (edited_CM['CM beløb']).to_numpy()


        metrik1 = np.round(alle_CM/gennemforelse*100,3)

        metrik2 = np.round(alle_CM/taxameter*100,3)

        metrik3 = np.round(gennemforelse/taxameter*100,3)

        endelig_df = pd.DataFrame([
            {"institutionsnummer" : df['Institutions nummer:']}, 
            {"institutionsnavn" : df.iloc[:,1]},
            {"Andel af 'Undervisningens gennemførelse, øvrige omkostninger' der består af UNGLI licenser:" : metrik1},
            {"Andel af undervisningstaxameter der består af UNGLI licenser:" : metrik2},
            {"Andel af undervisningstaxameter der består af 'Undervisningens gennemførelse, øvrige omkostninger':" : metrik3}
        ])
        #st.subheader('Analyse af ' + inst_navn + ', institutionsnummer: ' + str(inst_num))
        st.write(endelig_df)
        #st.metric('Andel af "Undervisningens gennemførelse, øvrige omkostninger" der består af UNGLI licenser:', value = str(metrik1)+ "%")
        #st.metric('Andel af undervisningstaxameter der består af UNGLI licenser:', value = str(metrik2) + "%")
        #st.metric('Andel af undervisningstaxameter der består af "Undervisningens gennemførelse, øvrige omkostninger":', value = str(metrik3) + "%")

    else:
        st.header('Analyserer fil "' + filename + '"')

        df = load_multiple(file)
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

