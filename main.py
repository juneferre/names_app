import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from io import BytesIO
import streamlit as st

## LOAD DATA DIRECTLY FROM SS WEBSITE
@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

df = load_name_data()



df['total_births'] = df.groupby(['year', 'sex'])['count'].transform('sum')
df['prop'] = df['count'] / df['total_births']
st.title('My Name App')

tab1, tab2, tab3 = st.tabs(['Overall', 'By Name', 'By Year'])

with tab1: 
    st.write('Here is stuff about all the data')

with tab2: 
    st.write('Name')

    # pick a name
    noi = st.text_input('Enter a name')
    plot_female = st.checkbox('Plot female line')
    plot_male = st.checkbox('Plot male line')
    name_df = df[df['name']==noi]

    fig = plt.figure(figsize=(15, 8))

    if plot_female:
        sns.lineplot(data=name_df[name_df['sex'] == 'F'], x='year', y='prop', label='Female')

    if plot_male:
        sns.lineplot(data=name_df[name_df['sex'] == 'M'], x='year', y='prop', label='Male')

    plt.title(f'Popularity of {noi} over time')
    plt.xlim(1880, 2025)
    plt.xlabel('Year')
    plt.ylabel('Proportion')
    plt.xticks(rotation=90)
    plt.legend()
    plt.tight_layout()

    st.pyplot(fig)



with tab3:
    st.write('Year')

    year_of_interest = st.number_input('Enter a year', min_value=1880, max_value=2025, step=1, value=1990)
    top_names = df[df['year'] == year_of_interest]

    # st.write(top_names.shape)

    # ---- FEMALE NAMES ----
    top_female = top_names[top_names['sex'] == 'F'].nlargest(10, 'count')
    f_year_fig = plt.figure(figsize=(15, 8))
    sns.barplot(data=top_female, x='count', y='name')
    plt.title(f"Top 10 Female Names in {year_of_interest}")
    plt.xlabel('Count')
    plt.ylabel('Name')
    plt.tight_layout()
    st.pyplot(f_year_fig)

    # ---- MALE NAMES ----
    top_male = top_names[top_names['sex'] == 'M'].nlargest(10, 'count')
    m_year_fig = plt.figure(figsize=(15, 8))
    sns.barplot(data=top_male, x='count', y='name')
    plt.title(f"Top 10 Male Names in {year_of_interest}")
    plt.xlabel('Count')
    plt.ylabel('Name')
    plt.tight_layout()
    st.pyplot(m_year_fig)
