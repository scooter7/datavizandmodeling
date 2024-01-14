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

    # Filter data for 'Yes' values in the Applicant Enrollment column
    filtered_data = data[data[value_column] == 'Yes']

    # Count occurrences of 'Yes' by ZIP Code
    aggregated_data = filtered_data.groupby(zip_column).size().reset_index(name='count')
    
    # Merge the aggregated data with the ZIP code database
    merged_data = aggregated_data.merge(zip_code_database, how='left', left_on=zip_column, right_on='zip')

    # Create the density map using the count of 'Yes' values
    fig = px.density_mapbox(merged_data, lat='latitude', lon='longitude', z='count', radius=10,
                            center=dict(lat=37.0902, lon=-95.7129), zoom=3, mapbox_style="open-street-map")
    st.plotly_chart(fig)

def create_pivot_table(data, index_column, pivot_column, values_column, agg_func):
    # Convert columns to string to ensure they are 1-dimensional
    data[index_column] = data[index_column].astype(str)
    data[pivot_column] = data[pivot_column].astype(str)

    # Determine the aggregation function
    if pd.api.types.is_numeric_dtype(data[values_column]):
        agg_func = 'sum'
    else:
        agg_func = 'count'

    try:
        pivot_table = pd.pivot_table(data, values=values_column, index=index_column, columns=pivot_column, aggfunc=agg_func, fill_value=0)
        st.write(pivot_table)
    except Exception as e:
        st.error(f"Error creating pivot table: {e}")

def detect_mixed_type_columns(df):
    mixed_type_columns = {}
    for col in df.columns:
        col_type = st.selectbox(f"Select data type for '{col}'", ['str', 'numeric', 'float', 'date/time'], key=f'{col}_selectbox', index=0)
        mixed_type_columns[col] = col_type
    return mixed_type_columns
    
def standardize_column(data, column_name):
    # Ensure the column exists in the DataFrame
    if column_name in data.columns:
        # Convert any complex or mixed types to string
        data[column_name] = data[column_name].apply(lambda x: ','.join(map(str, x)) if isinstance(x, (list, tuple)) else str(x))
    return data
    
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
                for col in mixed_type_cols:
                    data = standardize_column(data, col)
                st.success("Data reloaded with specified data types.")

        x_column = st.selectbox("Select X-axis Column for Chart", data.columns.tolist(), index=0)
        selected_map_zip_column = st.selectbox("Select Zip Column for Density Map", data.columns.tolist(), index=0)
        selected_map_value_column = st.selectbox("Select Value Column for Density Map", data.columns.tolist(), index=1)
        zip_code_database = load_zip_code_database()

        selected_pivot_index = st.selectbox("Select Index Column for Pivot Table", data.columns.tolist(), index=0)
        selected_pivot_column = st.selectbox("Select Column for Pivot Table Columns", data.columns.tolist(), index=1)
        selected_value_column = st.selectbox("Select Values Column for Pivot Table", data.columns.tolist(), index=2)
        agg_func = st.selectbox("Select Aggregation Function for Pivot Table", ['sum', 'count', 'mean'], index=0)

        if st.button("Create Column Chart"):
            create_column_chart(data, x_column)

        if st.button("Create Pie Chart"):
            create_pie_chart(data, x_column)

        if st.button("Create Density Map"):
            create_density_map(data, selected_map_zip_column, selected_map_value_column, zip_code_database)

        if st.button("Create Pivot Table"):
            create_pivot_table(data, selected_pivot_index, selected_pivot_column, selected_value_column, agg_func)

if __name__ == "__main__":
    main()
