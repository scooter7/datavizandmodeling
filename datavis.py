import pandas as pd
import streamlit as st
import plotly.express as px
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

def create_choropleth_map(data, zip_column, value_column, geojson):
    fig = px.choropleth_mapbox(data, geojson=geojson, locations=zip_column, color=value_column,
                               featureidkey="properties.ZIP",  # Adjust the featureidkey based on your GeoJSON
                               mapbox_style="carto-positron", zoom=3, center={"lat": 37.0902, "lon": -95.7129})
    st.plotly_chart(fig)

def create_pivot_table(data, rows, columns, values):
    agg_func = st.selectbox("Select Aggregation Function", ['sum', 'count', 'mean'], index=0)
    pivot_table = pd.pivot_table(data, values=values, index=rows, columns=columns, aggfunc=agg_func)
    st.write(pivot_table)

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

        selected_pivot_rows = st.multiselect("Select Rows for Pivot Table", data.columns.tolist(), default=None)
        selected_pivot_columns = st.multiselect("Select Columns for Pivot Table", data.columns.tolist(), default=None)
        selected_pivot_values = st.selectbox("Select Values for Pivot Table", data.columns.tolist(), index=0)
        
        if selected_pivot_rows:
            data[selected_pivot_rows] = data[selected_pivot_rows].astype(str)
        if selected_pivot_columns:
            data[selected_pivot_columns] = data[selected_pivot_columns].astype(str)

        selected_map_zip_column = st.selectbox("Select Zip Column for Choropleth Map", data.columns.tolist(), index=0)
        selected_map_value_column = st.selectbox("Select Value Column for Choropleth Map", data.columns.tolist(), index=1)
        zip_code_database = load_zip_code_database()
        
        data[selected_map_zip_column] = data[selected_map_zip_column].astype(str)
        zip_code_database['zip'] = zip_code_database['zip'].astype(str)

        x_column = st.selectbox("Select X-axis Column for Chart", data.columns.tolist(), index=0)

        if st.button("Create Column Chart"):
            create_column_chart(data, x_column)

        if st.button("Create Pie Chart"):
            create_pie_chart(data, x_column)

        if st.button("Create Choropleth Map"):
            create_choropleth_map(data, selected_map_zip_column, selected_map_value_column, zip_code_database)

        if st.button("Create Pivot Table"):
            create_pivot_table(data, selected_pivot_rows, selected_pivot_columns, selected_pivot_values)

if __name__ == "__main__":
    main()


