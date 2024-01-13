import pandas as pd
import streamlit as st
import plotly.express as px
import json
import requests

def format_zip_codes(data, zip_column):
    if zip_column in data.columns:
        data[zip_column] = data[zip_column].apply(lambda x: str(x).zfill(5) if pd.notnull(x) else x)
    return data

def handle_missing_data(data, col_types):
    for col, col_type in col_types.items():
        if col_type == 'str':
            data[col] = data[col].fillna('blank')
        elif col_type in ['numeric', 'float']:
            if data[col].isnull().any():
                mean_value = data[col].mean()
                data[col] = data[col].fillna(mean_value)
    return data

def create_column_chart(data, x_column, y_column):
    fig = px.bar(data, x=x_column, y=y_column)
    st.plotly_chart(fig)

def create_pie_chart(data, column):
    fig = px.pie(data, names=column, values=data.columns[0])
    st.plotly_chart(fig)

def create_choropleth_map(data, zip_column, value_column):
    url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/tx_texas_zip_codes_geo.min.json'
    geojson = json.loads(requests.get(url).text)
    fig = px.choropleth(data, geojson=geojson, locations=zip_column, featureidkey="properties.ZCTA5CE10", color=value_column)
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

def create_pivot_table(data, rows, columns, values):
    pivot_table = pd.pivot_table(data, values=values, index=rows, columns=columns, aggfunc='sum')
    st.write(pivot_table)

def detect_mixed_type_columns(df):
    mixed_type_columns = []
    for col in df.columns:
        if df[col].apply(type).nunique() > 1:
            mixed_type_columns.append(col)
    return mixed_type_columns

def load_and_merge_zip_data(uploaded_data, zip_column_name):
    zip_code_database_url = "https://github.com/scooter7/datavizandmodeling/raw/main/zip_code_database.xlsx"
    zip_code_data = pd.read_excel(zip_code_database_url)
    merged_data = uploaded_data.merge(zip_code_data, left_on=zip_column_name, right_on='zip', how='left')
    return merged_data

def main():
    st.title("Data Visualization App")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file, low_memory=False)
        except pd.errors.EmptyDataError:
            st.error("No columns to parse from file. Please check the file format and contents.")
            return

        zip_column = st.text_input("Enter the name of the zip code column (if applicable):")
        if zip_column:
            data = format_zip_codes(data, zip_column)

        mixed_type_cols = detect_mixed_type_columns(data)
        if mixed_type_cols:
            st.warning("Some columns have mixed types and may need data type specification:")
            col_types = {}
            for col in mixed_type_cols:
                col_type = st.selectbox(f"Select data type for '{col}'", ['str', 'numeric', 'float', 'date/time'], key=col, index=0)
                col_types[col] = col_type
            if st.button("Reload Data with Specified Types"):
                try:
                    data = pd.read_csv(uploaded_file, dtype=col_types, low_memory=False)
                    data = handle_missing_data(data, col_types)
                    st.success("Data reloaded with specified data types and missing data handled.")
                except Exception as e:
                    st.error(f"Error reloading data: {e}")

        chart_type = st.selectbox("Select Chart Type", ["Column Chart", "Pie Chart", "Choropleth Map"])
        if chart_type == "Column Chart":
            create_column_chart(data)
        elif chart_type == "Pie Chart":
            selected_column = st.selectbox("Select a column for the Pie Chart", data.columns.tolist(), index=0)
            create_pie_chart(data, selected_column)
        elif chart_type == "Choropleth Map":
            value_column = st.selectbox("Select Value Column for Choropleth Map", data.columns.tolist(), index=0)
            create_choropleth_map(data, zip_column, value_column)

if __name__ == "__main__":
    main()

