import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests

# Function to create a column chart
def create_column_chart(data, column):
    fig = px.bar(data, x=column, y=data.columns[0])
    st.plotly_chart(fig)

# Function to create a pie chart
def create_pie_chart(data, column):
    fig = px.pie(data, names=column, values=data.columns[0])
    st.plotly_chart(fig)

# Function to create a choropleth map
def create_choropleth_map(data, zip_column, value_column):
    # Fetching USA Zip Code GeoJSON (this is a simplified example)
    url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/tx_texas_zip_codes_geo.min.json'
    geojson = json.loads(requests.get(url).text)

    fig = px.choropleth(data, geojson=geojson, locations=zip_column, featureidkey="properties.ZCTA5CE10", color=value_column)
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

# Function to create a pivot table
def create_pivot_table(data):
    st.subheader("Create Pivot Table")
    rows = st.multiselect("Select Rows", data.columns.tolist())
    columns = st.multiselect("Select Columns", data.columns.tolist())
    values = st.selectbox("Select Values", data.columns.tolist())

    if rows and columns and values:
        # Check if the selected 'values' column is numerical
        if pd.api.types.is_numeric_dtype(data[values]):
            agg_func = 'sum'
        else:
            # If categorical, use 'count' as aggregation function
            agg_func = 'count'

        pivot_table = pd.pivot_table(data, values=values, index=rows, columns=columns, aggfunc=agg_func)
        st.write(pivot_table)

def main():
    st.title("Data Visualization App")

    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        # Pivot Table
        create_pivot_table(data)

        # Variable selection for charts
        columns = data.columns.tolist()
        selected_column = st.selectbox("Select a column to visualize", columns)

        # Chart selection and creation
        chart_type = st.selectbox("Select Chart Type", ["Column Chart", "Pie Chart", "Choropleth Map"])
        if chart_type == "Column Chart":
            create_column_chart(data, selected_column)
        elif chart_type == "Pie Chart":
            create_pie_chart(data, selected_column)
        elif chart_type == "Choropleth Map":
            value_column = st.selectbox("Select Value Column for Choropleth Map", columns)
            create_choropleth_map(data, selected_column, value_column)

if __name__ == "__main__":
    main()
