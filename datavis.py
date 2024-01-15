import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import openpyxl

data = pd.DataFrame()  # Initialize data as an empty DataFrame

def format_zip_codes(data, zip_column):
    if zip_column in data.columns:
        data[zip_column] = data[zip_column].apply(lambda x: str(x).zfill(5) if pd.notnull(x) else x)
    return data

def handle_missing_data(data, col_types):
    for col, col_type in col_types.items():
        if col_type == 'str':
            data[col] = data[col].fillna('blank')
        elif col_type in ['number', 'float']:
            if data[col].isnull().any():
                mean_value = data[col].mean()
                data[col] = data[col].fillna(mean_value)
    return data

def clean_data_for_pivot(data):
    for col in data.columns:
        data[col] = data[col].astype(str)
    return data

def load_zip_code_database():
    url = 'https://github.com/scooter7/datavizandmodeling/blob/main/zip_code_database.xlsx?raw=true'
    return pd.read_excel(url)

def create_column_chart(data, x_column):
    chart_type = st.selectbox("Choose Chart Type", ["Value", "Count"], index=0)
    if chart_type == "Value":
        y_column = st.selectbox("Select Y-axis Column for Chart", data.columns.tolist(), index=1)
        fig = px.bar(data, x=x_column, y=y_column)
    else:
        fig = px.bar(data, x=x_column, text=x_column)
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fig)

def create_pie_chart(data, x_column):
    fig = px.pie(data, names=x_column, values=x_column)
    st.plotly_chart(fig)

def create_density_map(data, zip_column, value_column, zip_code_database):
    data[zip_column] = data[zip_column].astype(str)
    zip_code_database['zip'] = zip_code_database['zip'].astype(str)

    filtered_data = data[data[value_column] == 'Yes']

    aggregated_data = filtered_data.groupby(zip_column).size().reset_index(name='count')
    
    merged_data = aggregated_data.merge(zip_code_database, how='left', left_on=zip_column, right_on='zip')

    fig = px.density_mapbox(merged_data, lat='latitude', lon='longitude', z='count', radius=10,
                            center=dict(lat=37.0902, lon=-95.7129), zoom=3, mapbox_style="open-street-map")
    st.plotly_chart(fig)

def create_pivot_table(data, index_column, values_column):
    data[index_column] = data[index_column].astype(str)
    data[values_column] = data[values_column].astype(str)

    pivot_table = pd.pivot_table(data, index=index_column, values=values_column, aggfunc='count', fill_value=0)
    pivot_table.columns.name = None
    pivot_table.reset_index(inplace=True)

    st.dataframe(pivot_table)

def detect_mixed_type_columns(df):
    mixed_type_columns = {}
    for col in df.columns:
        col_type = st.selectbox(f"Select data type for '{col}'", ['str', 'number', 'float', 'date/time'], key=f'{col}_selectbox', index=0)
        mixed_type_columns[col] = col_type
    return mixed_type_columns
    
def standardize_column(data, column_name):
    if column_name in data.columns:
        data[column_name] = data[column_name].apply(lambda x: ','.join(map(str, x)) if isinstance(x, (list, tuple)) else str(x))
    return data
    
def main():
    global data

    st.title("Data Visualization App")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file, low_memory=False)
        st.subheader("Original CSV Data")
        st.dataframe(data)

        mixed_type_cols = detect_mixed_type_columns(data)
        if mixed_type_cols:
            if st.button("Reload Data with Specified Types"):
                data = handle_missing_data(data, mixed_type_cols)
                for col, col_type in mixed_type_cols.items():
                    data[col] = data[col].astype(col_type)
                st.success("Data reloaded with specified data types.")
                st.subheader("Processed CSV Data")
                st.dataframe(data)

    if not data.empty:  # Check if data is not empty before proceeding
        x_column = st.selectbox("Select X-axis Column for Chart", data.columns.tolist(), index=0)
        selected_map_zip_column = st.selectbox("Select Zip Column for Density Map", data.columns.tolist(), index=0)
        selected_map_value_column = st.selectbox("Select Value Column for Density Map", data.columns.tolist(), index=1)
        zip_code_database = load_zip_code_database()

        selected_index_column = st.selectbox("Select Index Column for Pivot Table (Rows)", data.columns.tolist(), index=0)
        selected_values_column = st.selectbox("Select Values Column for Pivot Table (Columns)", data.columns.tolist(), index=1)

        if st.button("Create Column Chart"):
            create_column_chart(data, x_column)

        if st.button("Create Pie Chart"):
            create_pie_chart(data, x_column)

        if st.button("Create Density Map"):
            create_density_map(data, selected_map_zip_column, selected_map_value_column, zip_code_database)

        if st.button("Create Pivot Table"):
            create_pivot_table(data, selected_index_column, selected_values_column)

if __name__ == "__main__":
    main()
