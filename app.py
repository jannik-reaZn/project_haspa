import pandas as pd
import re
import streamlit as st
import plotly.express as px
from keys import keys
#from keys import grocery

def filter_columns_in_dataframe(df):
    """
    Filter specific columns in dataframe.
    """
    try:
        df = df.filter(['Verwendungszweck', 'Betrag', 'Beguenstigter/Zahlungspflichtiger'])
        return df
    except:
        print('Error occured while filtering columns in dataframe')

if __name__ == '__main__':
    st.title('Haushaltsbuch')

    # input field for the user
    uploaded_file = st.file_uploader(label='Lade eine Datei hoch', type='csv', help='Drücke auf "Browse files" und lade eine Datei mit der Endung ".csv" hoch oder ziehe eine Datei in das Feld')

    # start displaying if a file is given
    if uploaded_file:
        # read in file
        df = pd.read_csv(uploaded_file, sep = ';', encoding = 'ISO-8859-1')

        # replace character ',' with '.' and convert to float
        df['Betrag'] = df['Betrag'].str.replace(',', '.')
        df['Betrag'] = df['Betrag'].astype(float)

        # keep specific columns
        df = filter_columns_in_dataframe(df)
        # TODO make this work
        df['Betrag'].round(2)
        df['Betrag'] = df['Betrag'].apply(lambda x: float('{:.2f}'.format(x)))

        # count number of occurences
        counter = 0

        # store spending for all keys
        list_key_spendings = []

        # sort alphabetically 
        sorted_keys = {key: value for key, value in sorted(keys.items())}

        for key in sorted_keys:
            # store spending for every key
            spendings_for_key = 0
            for company in keys[key]:
                # create dataframe with True/False if substring is contained/not contained
                df_booleans = df.apply(lambda col: col.str.contains(company, na=False, flags=re.IGNORECASE), axis=1)

                # dataframe with one column that contains true if true was detected in a row in df_booleans, otherwise false
                df_result = df_booleans.any(axis=1)

                # list of all row indices with true
                true_rows = df.index[df_result].tolist()

                # count the number of occurences
                counter += len(true_rows)

                # select amounts in column
                spendings = [df.at[item, 'Betrag'] for item in true_rows]

                # sum the spendings
                spendings_for_key += sum(spendings)

            list_key_spendings.append(round(spendings_for_key, 2))

        # convert negative values to positive
        list_key_spendings_positive = list(map(abs, list_key_spendings))

        # write all results in dataframe
        df_results = pd.DataFrame({'Key': sorted_keys.keys(),'Betrag': list_key_spendings_positive})

        st.header('Tabelle')
        st.dataframe(df)
        st.write(f'Es konnten {counter}/{df.shape[0]} Zeilen verarbeitet werden!')

        # plot bar chart
        st.header('Balkendiagramm')
        fig = px.bar(df_results, x='Key', y='Betrag', text=list_key_spendings_positive)
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig)