import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import openpyxl

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

    aggregated_data = data.groupby([zip_column, value_column]).size().reset_index(name='count')
    aggregated_data = aggregated_data.pivot(index=zip_column, columns=value_column, values='count').fillna(0)
    aggregated_data = aggregated_data.reset_index()

    merged_data = aggregated_data.merge(zip_code_database, how='left', left_on=zip_column, right_on='zip')

    fig = px.density_mapbox(merged_data, lat='latitude', lon='longitude', z='Yes', radius=10,
                            center=dict(lat=37.0902, lon=-95.7129), zoom=3, mapbox_style="open-street-map")
    st.plotly_chart(fig)

def create_pivot_table(data, rows, value_column):
    # Convert columns to string to ensure they are 1-dimensional
    data[rows] = data[rows].astype(str) if rows else data[rows]
    data[value_column] = data[value_column].astype(str) if value_column else data[value_column]

    agg_func = st.selectbox("Select Aggregation Function", ['sum', 'count', 'mean'], index=0)
    
    try:
        pivot_table = pd.pivot_table(data, values=value_column, index=rows, aggfunc=agg_func)
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
        data = pd.read_csv(uploaded_file, low_memory=False)
        st.subheader("Uploaded CSV Data")
        st.dataframe(data)

        mixed_type_cols = detect_mixed_type_columns(data)
        if mixed_type_cols:
            if st.button("Reload Data with Specified Types"):
                data = handle_missing_data(data, mixed_type_cols)
                st.success("Data reloaded with specified data types.")

        x_column = st.selectbox("Select X-axis Column for Chart", data.columns.tolist(), index=0)
        selected_pivot_rows = st.multiselect("Select Rows for Pivot Table", data.columns.tolist(), default=None)
        selected_value_column = st.selectbox("Select Column for Pivot Table Values", data.columns.tolist(), index=0)

        if st.button("Create Column Chart"):
            create_column_chart(data, x_column)

        if st.button("Create Pie Chart"):
            create_pie_chart(data, x_column)

        if st.button("Create Density Map"):
            create_density_map(data, selected_map_zip_column, selected_map_value_column, zip_code_database)

        if st.button("Create Pivot Table"):
            create_pivot_table(data, selected_pivot_rows, selected_value_column)

if __name__ == "__main__":
    main()

