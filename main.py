import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page to use the full screen width
st.set_page_config(layout="wide")

def load_data():
    data_file_path = 'Data/Pisa mean perfromance scores 2013 - 2015 Data.csv'
    definition_file_path = 'Data/Pisa mean performance scores 2013 - 2015 Definition and Source.csv'

    pisa_data = pd.read_csv(data_file_path)
    definitions = pd.read_csv(definition_file_path)

    # Replace '..' with NaN in specific columns only
    columns_to_clean = ['2015 [YR2015]']  # Update this list based on your data
    for col in columns_to_clean:
        pisa_data[col] = pisa_data[col].replace('..', pd.NA)

    # Convert score to numeric and dropna for these columns only
    pisa_data['2015 [YR2015]'] = pd.to_numeric(pisa_data['2015 [YR2015]'], errors='coerce')
    pisa_data.dropna(subset=columns_to_clean, inplace=True)

    return pisa_data, definitions

pisa_data, definitions = load_data()


def page_indicator_definitions(definitions):
    definitions = pd.read_csv('Data/Pisa mean performance scores 2013 - 2015 Definition and Source.csv')
    st.subheader("PISA Indicator Definitions")
    for index, row in definitions.iterrows():
        with st.expander(f"{row['Indicator Name']} ({row['Code']})"):
            st.write(row['Long definition'])

def page_country_performance(pisa_data):
    st.subheader("Country Performance Analysis")

    # Subject selection
    subjects = {
        'Mathematics': 'PISA: Mean performance on the mathematics scale',
        'Reading': 'PISA: Mean performance on the reading scale',
        'Science': 'PISA: Mean performance on the science scale'
    }
    subject = st.selectbox("Select Subject", list(subjects.keys()))

    # Initialize session state for selected countries
    if 'selected_countries' not in st.session_state:
        st.session_state['selected_countries'] = pisa_data['Country Name'].unique().tolist()

    # Filter data for the year 2015, overall gender, and selected countries
    filtered_data = pisa_data[(pisa_data['Series Name'] == subjects[subject]) &
                              (pisa_data['Country Name'].isin(st.session_state['selected_countries']))]

    # Plotting
    fig = px.bar(filtered_data, x='Country Name', y='2015 [YR2015]', color='Country Name',
                 title=f'PISA Scores for {subject} in 2015')
    fig.update_layout(
        width=800,  # Adjust width as needed
        height=600  # Adjust height as needed
    )
    # Centering the chart
    with st.container():
        st.plotly_chart(fig, use_container_width=True)

    # Container for country checkboxes arranged in columns
    all_countries = pisa_data['Country Name'].unique()
    num_cols = 8  # Adjust the number of columns as needed
    cols = st.columns(num_cols)
    for index, country in enumerate(all_countries):
        col = cols[index % num_cols]
        is_selected = col.checkbox(country, value=(country in st.session_state['selected_countries']), key=country)
        if is_selected and country not in st.session_state['selected_countries']:
            st.session_state['selected_countries'].append(country)
        elif not is_selected and country in st.session_state['selected_countries']:
            st.session_state['selected_countries'].remove(country)

def page_gender_gap_analysis(pisa_data):
    st.subheader("Gender Gap Analysis")

    # Country and Subject selection
    country = st.sidebar.selectbox("Select Country", pisa_data['Country Name'].unique())
    subjects = {
        'Mathematics': 'mathematics scale',
        'Reading': 'reading scale',
        'Science': 'science scale'
    }
    subject = st.sidebar.selectbox("Select Subject", list(subjects.keys()))

    # Filter data based on country and subject
    gender_data = pisa_data[pisa_data['Country Name'] == country]
    general_data = gender_data[gender_data['Series Name'].str.contains(subjects[subject], case=False)]
    female_data = gender_data[gender_data['Series Name'].str.contains(subjects[subject]) & gender_data['Series Name'].str.contains('Female')]
    male_data = gender_data[gender_data['Series Name'].str.contains(subjects[subject]) & gender_data['Series Name'].str.contains('Male')]

    # Plotting a horizontal bar chart
    fig = px.bar(general_data, y='Series Name', x='2015 [YR2015]', color='Series Name', orientation='h',
                 title=f'Gender Gap in {country} for {subject} in 2015')
    fig.update_layout(width=800, height=600)  # Adjust the width and height as needed

    # Add data values on the chart
    fig.update_traces(texttemplate='%{x}', textposition='outside')

    # Centering the chart
    with st.container():
        st.plotly_chart(fig, use_container_width=True)

    # Displaying data number
    mean_general = general_data['2015 [YR2015]'].mean()
    mean_female = female_data['2015 [YR2015]'].mean()
    mean_male = male_data['2015 [YR2015]'].mean()

    st.write(
        f"The mean performance score for {subject} in {country} in 2015 is {mean_general:.2f} (Overall), {mean_female:.2f} (Female), and {mean_male:.2f} (Male).")

def page_top_bottom_countries(pisa_data):
    st.subheader("Top and Bottom Performing Countries")

    # Subject selection
    subjects = {
        'Mathematics': 'PISA: Mean performance on the mathematics scale',
        'Reading': 'PISA: Mean performance on the reading scale',
        'Science': 'PISA: Mean performance on the science scale'
    }
    subject = st.selectbox("Select Subject", list(subjects.keys()))

    # Number of countries
    num_countries = st.slider("Number of Countries", 1, 15, 5)

    # Filter and sort data
    subject_data = pisa_data[pisa_data['Series Name'] == subjects[subject]]
    top_countries = subject_data.nlargest(num_countries, '2015 [YR2015]')
    bottom_countries = subject_data.nsmallest(num_countries, '2015 [YR2015]')

    # Plotting top and bottom countries
    fig_top = px.bar(top_countries, x='2015 [YR2015]', y='Country Name', orientation='h',
                     title=f'Top {num_countries} Countries in {subject} 2015')
    # Add data values on the chart
    fig_top.update_traces(texttemplate='%{x}', textposition='outside')
    fig_bottom = px.bar(bottom_countries, x='2015 [YR2015]', y='Country Name', orientation='h',
                        title=f'Bottom {num_countries} Countries in {subject} 2015')
    fig_bottom.update_traces(texttemplate='%{x}', textposition='outside')

    st.plotly_chart(fig_top)
    st.plotly_chart(fig_bottom)

def main():
    # Custom CSS for styling with red header background
    st.markdown("""
    <style>
    .main .block-container { padding-top: 5rem; }
    .reportview-container .main header { background-color: #8B0000; }
    h1 { color: white; margin-bottom: 1rem; }
    .css-145kmo2 { background-color: #8B0000; }
    .css-145kmo2 button { border: 1px solid white; color: white; }
    .css-145kmo2 button:hover { background-color: #a30000; }
    </style>
    """, unsafe_allow_html=True)

    # Red header with title
    st.markdown("<div style='background-color: #8B0000;'><h1 style='color: white; padding: 1rem;'>PISA Data Analysis in 2015</h1></div>", unsafe_allow_html=True)

    # Creating a top navigation menu using columns and buttons
    menu_options = {
        "PISA Data Analysis in 2015": page_indicator_definitions,
        "Country Performance Analysis": page_country_performance,
        "Gender Gap Analysis": page_gender_gap_analysis,
        "Top and Bottom Countries": page_top_bottom_countries
    }

    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = page_indicator_definitions

    cols = st.columns(len(menu_options))

    for i, (title, func) in enumerate(menu_options.items()):
        if cols[i].button(title):
            st.session_state['current_page'] = func

    st.session_state['current_page'](pisa_data)

if __name__ == "__main__":
    main()




