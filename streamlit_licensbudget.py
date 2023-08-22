import streamlit as st
import pandas as pd
import numpy as np

#layout sat til wide så app bruger hele bredden af browseren
st.set_page_config(page_title='UNGLI institutionsøkonomi analyse', page_icon="appikon.jpg", layout='wide', initial_sidebar_state="expanded")

#filnavn på fil der bliver brugt som stand-in, indtil en ny fil uploades. 
#er måske forældet, da der ikke bruges sådan en længere?? 
#piller ikke ved det nu
file = filename = 'Regnskabsdata.XLS'
# .sidebar indikerer at det der henvises til bliver skrevet i en pop-ud bar til venstre i browseren
st.sidebar.subheader('Indlæs din regnskabsdata fil')
st.sidebar.write('Ønsker du at analysere flere filer samtidig (eksempelvis for at sammenligne på tværs af årstal) skal du være opmærksom på at have det samme antal institutioner i hver fil.')
st.sidebar.write('Er der færre institutioner i filen end angivet i nedenstående felt vil du opleve fejl på siden.')

#file uploader, så bruger kan uploade filer til analyse
# accept multiple files = True, så man kan uploade flere års rapporter i samme omgang
uploaded_files = st.sidebar.file_uploader("Downloades fra https://regnskabsportal.uvm.dk/Accounts/Search.aspx?sm=4.1", accept_multiple_files=True)#, type = 'xlsx')
antal_inst = int(st.sidebar.number_input('Indtast antal institutioner i filen', min_value = 1))


def load_multiple(file, num_inst = antal_inst):
    """
    input:
    file -> (str): kommer fra file_uploader
    num_inst = (int) antallet af institutioner der ønskes analyseres, 
    må ikke overstige antal af institutioner i fil

    output: 
    pd.DataFrame med indlæst regnskabsfil
    """
    #kolonnerne i regnskabsfilerne er sat op lidt specielt, så første institution svarer til anden kolonne
    #Vi indlæser kun den kolonne der indeholder information om institutionerne
    start_cols = [1]
    mult_cols = np.arange(start = 4, stop = 4 + num_inst)
    mult_cols = np.append(start_cols, mult_cols)
    return pd.read_excel(file, skiprows=4, usecols = mult_cols)

#hvis der kun skal uploades én fil med én inst
def load_data(file):
    return pd.read_excel(file, skiprows = 4, usecols = [1,4])

st.title('UNGLI institutionsøkonomi analyse')
st.write('Formålet med denne app er at give et hurtigt overblik over hvor meget UNGLI licenser fylder i budgettet for en given institution. Oplever du problemer med appen bedes du kontakte ALFs analysegruppe.')
st.write('For at bruge appen skal du have en fil trukket fra Regnskabsportalen i .XLS format samt et estimat af hvor mange penge institutionen bruger på UNGLI licenser (dette kan formentlig aflæses i ConsortiaManager).')
st.write('Det er muligt at analysere flere filer og institutioner samtidig. Vær opmærksom på at hvis der skal analyseres flere filer skal antallet af institutioner i hver fil være det samme, for at undgå fejl på denne side.')
st.write('Når dine filer er accepteret vil du se en tabel, hvor du skal indtaste beløbet der bruges på UNGLI licenser for den givne institution. Herefter udregnes de ønskede metrikker baseret på information der aflæses af regnskabsfilerne.')
st.write('*Det bliver forhåbentlig muligt at bruge et API kald til ConsortiManager i fremtiden, så CM data ikke skal tastes manuelt ind. Dog virker deres API ikke på nuværende tidspunkt med vores app. Bliver det muligt senere vil vi forsøge at implementere det :-).*')
st.write('Upload og indtast antal institutioner til venstre.')

if uploaded_files is not None:

    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        file = uploaded_file
        st.header('Analyserer fil "' + filename + '"')
        
        df = load_multiple(file)
        #transponér så rækker fra excel passer med kolonner i pandas
        df = df.T
        #definér rækken som kolonnenavne, og fjern dernæst rækken som "datarække"
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        CM_info = pd.DataFrame(
            np.array([(df['Institutions nummer:']).to_numpy(), (df.iloc[:,1]).to_numpy(), np.ones(antal_inst)]).T,
            columns = ["institutionsnummer", "institutionsnavn", "CM beløb"]
            )
        
        st.write('I nedenstående tabel bedes du indtaste beløbet der bruges på UNGLI licenser for hver af de ønskede institutioner for det givne år. Beløbet findes i ConsortiaManager.\nDu ændrer beløbet ved at klikke på den ønskede celle, indtaste tallet og trykke "Enter".')
        edited_CM = st.data_editor(CM_info, column_config={
        "institutionsnummer": "Institutionsnummer",
        "institutionsnavn": "Institutionsnavn",
        "CM beløb": st.column_config.NumberColumn(
            "UNGLI beløb",
            help="Indtast antal kroner brugt på UNGLI licenser.",
            min_value=1,
        ),
        }, hide_index = True, disabled = ["institutionsnummer", "institutionsnavn"]
        )


        ### data manipulering, hent info vi skal bruge ###
        #institutionsnummer og navn
        inst_num = df['Institutions nummer:']
        inst_navn = df.iloc[:,1]
        #Taxameter
        taxameter = (df['Undervisningstaxameter']).to_numpy(dtype = float)
        #undervisningsgennemførelse, budgettet licenser kommer fra
        gennemforelse = (df["Undervisningens gennemførelse, Øvrige omkostninger"]).to_numpy(dtype = float)

        alle_CM = (edited_CM['CM beløb']).to_numpy(dtype = float)

        #udregn alle metrikker i procent, med tre decimaler
        metrik1 = np.round(alle_CM/gennemforelse*100,3)

        metrik2 = np.round(alle_CM/taxameter*100,3)

        metrik3 = np.round(gennemforelse/taxameter*100,3)

        ende_data = np.array([df['Institutions nummer:'].to_numpy(), df.iloc[:,1].to_numpy(), metrik1, metrik2, metrik3])
        ende_kol = ["Institutionsnummer", "Institutionsnavn", "Andel af 'Undervisningens gennemførelse, øvrige omkostninger' der består af UNGLI licenser:", "Andel af undervisningstaxameter der består af UNGLI licenser:", "Andel af undervisningstaxameter der består af 'Undervisningens gennemførelse, øvrige omkostninger':"]
        endelig_df = pd.DataFrame(ende_data.T, columns = ende_kol)

        st.write("I nedenstående tabel ser du de beregnede metrikker. Formatering gør at det kan være nødvendigt at 'scrolle' igennem tabellen for at se det hele. Vær opmærksom på at værdier angivet som 'andele' er angivet i %.")
        
        st.dataframe(endelig_df, use_container_width=True, hide_index = True)

        st.caption('Ovenstående tabel viser institutionsnummer, institutionsnavn, Andel af "Undervisningens gennemførelse, øvrige omkostninger" der består af UNGLI licenser, Andel af undervisningstaxameter der består af UNGLI licenser og Andel af undervisningstaxameter der består af "Undervisningens gennemførelse, øvrige omkostninger". Andele angives i %.')
else:
    st.write("Ingen fil uploadet :-(")

st.write('*Dette er sidste linje kode i scriptet, hvis du ser denne tekst er appen kørt uden problemer :-) Appen er senest opdateret 25. juli 2023 af Linea Hedemark*')
