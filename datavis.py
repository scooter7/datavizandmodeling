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
    st.subheader("Create Column Chart")
    if x_column and y_column:
        fig = px.bar(data, x=x_column, y=y_column)
        st.plotly_chart(fig)

def create_pie_chart(data, column):
    fig = px.pie(data, names=column, values=data.columns[0])
    st.plotly_chart(fig)

def create_choropleth_map(data, zip_column, value_column):
    fig = px.choropleth(data, locations=zip_column, color=value_column, geojson='https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/us_geo.min.json')
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

def create_pivot_table(data, rows, columns, values):
    st.subheader("Create Pivot Table")
    if rows and columns and values:
        try:
            if pd.api.types.is_numeric_dtype(data[values]):
                agg_func = 'sum'
            else:
                agg_func = 'count'
            pivot_table = pd.pivot_table(data, values=values, index=rows, columns=columns, aggfunc=agg_func)
            st.write(pivot_table)
        except Exception as e:
            st.error(f"Error creating pivot table: {e}")

def detect_mixed_type_columns(df):
    mixed_type_columns = {}
    for col in df.columns:
        col_type = st.selectbox(f"Select data type for '{col}'", ['str', 'numeric', 'float', 'date/time'], key=f'{col}_selectbox', index=0)
        mixed_type_columns[col] = col_type
    return mixed_type_columns

def main():
    st.title("Data Visualization App")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file, low_memory=False)
        except pd.errors.EmptyDataError:
            st.error("No columns to parse from file. Please check the file format and contents.")
            return

        st.subheader("Uploaded CSV Data")
        st.dataframe(data)

        st.subheader("Column Selections for Visualizations")
        x_column = st.selectbox("Select X-axis Column for Chart", data.columns.tolist(), index=0)
        y_column = st.selectbox("Select Y-axis Column for Chart", data.columns.tolist(), index=1)
        selected_pivot_rows = st.multiselect("Select Rows for Pivot Table", data.columns.tolist(), default=None)
        selected_pivot_columns = st.multiselect("Select Columns for Pivot Table", data.columns.tolist(), default=None)
        selected_pivot_values = st.selectbox("Select Values for Pivot Table", data.columns.tolist(), index=0)
        selected_map_value_column = st.selectbox("Select Value Column for Choropleth Map", data.columns.tolist(), index=0)

        mixed_type_cols = detect_mixed_type_columns(data)
        if mixed_type_cols:
            st.warning("Some columns have mixed types and may need data type specification:")
            col_types = handle_missing_data(data, mixed_type_cols)
            if st.button("Reload Data with Specified Types"):
                try:
                    data = pd.read_csv(uploaded_file, dtype=col_types, low_memory=False)
                    st.success("Data reloaded with specified data types.")
                except Exception as e:
                    st.error(f"Error reloading data: {e}")

        if st.button("Create Column Chart"):
            create_column_chart(data, x_column, y_column)

        if st.button("Create Pie Chart"):
            create_pie_chart(data, x_column)

        if st.button("Create Choropleth Map"):
            create_choropleth_map(data, selected_map_value_column, selected_map_value_column)

        if st.button("Create Pivot Table"):
            create_pivot_table(data, selected_pivot_rows, selected_pivot_columns, selected_pivot_values)

if __name__ == "__main__":
    main()
