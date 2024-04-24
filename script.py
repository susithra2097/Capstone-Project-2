from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import requests
import json

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="guvicapstone"
)

# Function to execute SELECT query and return DataFrame
def query_to_df(query):
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    return df

# SELECT queries for each table
queries = [
    "SELECT * FROM Aggregated_Transaction",
    "SELECT * FROM Aggregated_Users",
    "SELECT * FROM Map_Transaction",
    "SELECT * FROM Map_User",
    "SELECT * FROM Top_Transaction",
    "SELECT * FROM Top_User"
]

# List to store DataFrames
dfs = []

# Execute queries and transform results into DataFrames
for query in queries:
    df = query_to_df(query)
    dfs.append(df)

# Close connection to MySQL database
conn.close()

# Access DataFrames
aggregated_transaction_df = dfs[0]
aggregated_users_df = dfs[1]
map_transaction_df = dfs[2]
map_user_df = dfs[3]
top_transaction_df = dfs[4]
top_user_df = dfs[5]

# Helper function to generate unique selectbox key
def generate_selectbox_key(year, quarters, method):
    return f"{year}_{quarters}_state_select_{method}"

#####################################################Functions##########################################################################

def TransactionAmount_count(df, year, quarters, selected_states):
    df["Years"] = df["Years"].astype(int)
    
    if quarters == "All Quarters":
        selected_data = df[df["Years"] == year]
        quarter_title = f"{year}"
        map_title = f"{year}"
    else:
        selected_data = df[(df["Years"] == year) & (df["Quarter"] == quarters)]
        quarter_title = f"{year} {quarters}Q"
        map_title = f"{year} {quarters}Q"

    if not selected_states or "All States" in selected_states:
        selected_data = df
    else:
        selected_data = selected_data[selected_data["States"].isin(selected_states)]
        
    selected_data.reset_index(drop=True, inplace=True)

    selected_data_n = selected_data.groupby("States")[["TransactionCount", "TransactionAmount"]].sum()
    selected_data_n.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        Amount_chart = px.bar(selected_data_n, x="States", y="TransactionAmount", title=f"{quarter_title} TRANSACTION AMOUNT", width=600, height=600)
        st.plotly_chart(Amount_chart)

    with col2:
        Count_Chart = px.bar(selected_data_n, x="States", y="TransactionCount", title=f"{quarter_title} TRANSACTION COUNT",
                             color_discrete_sequence=px.colors.sequential.Bluered_r, width=600, height=600)
        st.plotly_chart(Count_Chart)

    col1, col2 = st.columns(2)

    with col1:
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)
        states_name = []
        for feature in data1["features"]:
            states_name.append(feature["properties"]["ST_NM"])
        states_name.sort()

        fig = px.choropleth(selected_data_n, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                            color="TransactionAmount", color_continuous_scale="Rainbow",
                            range_color=(selected_data_n["TransactionAmount"].min(), selected_data_n["TransactionAmount"].max()),
                            hover_name="States", title=f"{map_title} TRANSACTION AMOUNT", fitbounds="locations",
                            height=600, width=600)

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig)

    with col2:
        fig1 = px.choropleth(selected_data_n, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                             color="TransactionCount", color_continuous_scale="Rainbow",
                             range_color=(selected_data_n["TransactionCount"].min(), selected_data_n["TransactionCount"].max()),
                             hover_name="States", title=f"{map_title} TRANSACTION COUNT", fitbounds="locations",
                             height=600, width=600)

        fig1.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig1)

def Transaction_Analysis_Function(df, year, quarters, selected_states,selected_transaction_types):
    df["Years"] = df["Years"].astype(int)
    
    if quarters == "All Quarters":
        selected_data = df[df["Years"] == year]
        quarter_title = f"{year}"
        map_title = f"{year}"
    else:
        selected_data = df[(df["Years"] == year) & (df["Quarter"] == quarters)]
        quarter_title = f"{year} {quarters}Q"
        map_title = f"{year} {quarters}Q"

    if not selected_states or "All States" in selected_states:
        selected_data = df
    else:
        selected_data = selected_data[selected_data["States"].isin(selected_states)]

    if not selected_transaction_types or "All Transaction Types" in selected_transaction_types:
        selected_data = df
    else:
        selected_data = selected_data[selected_data["TransactionType"].isin(selected_transaction_types)]
         
    selected_data.reset_index(drop=True, inplace=True)

    selected_data_n = selected_data.groupby("States")[["TransactionCount", "TransactionAmount"]].sum()
    selected_data_n.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        Amount_chart = px.bar(selected_data_n, x="States", y="TransactionAmount", title=f"{quarter_title} TRANSACTION AMOUNT", width=600, height=600)
        st.plotly_chart(Amount_chart)

    with col2:
        Count_Chart = px.bar(selected_data_n, x="States", y="TransactionCount", title=f"{quarter_title} TRANSACTION COUNT",
                             color_discrete_sequence=px.colors.sequential.Bluered_r, width=600, height=600)
        st.plotly_chart(Count_Chart)

    col1, col2 = st.columns(2)

    with col1:
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)
        states_name = []
        for feature in data1["features"]:
            states_name.append(feature["properties"]["ST_NM"])
        states_name.sort()

        fig = px.choropleth(selected_data_n, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                            color="TransactionAmount", color_continuous_scale="Rainbow",
                            range_color=(selected_data_n["TransactionAmount"].min(), selected_data_n["TransactionAmount"].max()),
                            hover_name="States", title=f"{map_title} TRANSACTION AMOUNT", fitbounds="locations",
                            height=600, width=600)

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig)

    with col2:
        fig1 = px.choropleth(selected_data_n, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                             color="TransactionCount", color_continuous_scale="Rainbow",
                             range_color=(selected_data_n["TransactionCount"].min(), selected_data_n["TransactionCount"].max()),
                             hover_name="States", title=f"{map_title} TRANSACTION COUNT", fitbounds="locations",
                             height=600, width=600)

        fig1.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig1)

def Transaction_User_Function(df, year, quarters, selected_states,selected_brand_types):
    df["Years"] = df["Years"].astype(int)
    
    if quarters == "All Quarters":
        selected_data = df[df["Years"] == year]
        quarter_title = f"{year}"
        map_title = f"{year}"
    else:
        selected_data = df[(df["Years"] == year) & (df["Quarter"] == quarters)]
        quarter_title = f"{year} {quarters}Q"
        map_title = f"{year} {quarters}Q"

    if not selected_states or "All States" in selected_states:
        selected_data = df
    else:
        selected_data = selected_data[selected_data["States"].isin(selected_states)]

    if not selected_brand_types or "All Brands" in selected_brand_types:
        selected_data = df
    else:
        selected_data = selected_data[selected_data["Brands"].isin(selected_brand_types)]
         
    selected_data.reset_index(drop=True, inplace=True)

    selected_data_n = selected_data.groupby("States")[["TransactionCount"]].sum()
    selected_data_n.reset_index(inplace=True)


    Amount_chart = px.bar(selected_data_n, x="States", y="TransactionCount", title=f"{quarter_title} TRANSACTION COUNT", width=600, height=600)
    st.plotly_chart(Amount_chart)

    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(url)
    data1 = json.loads(response.content)
    states_name = []
    for feature in data1["features"]:
        states_name.append(feature["properties"]["ST_NM"])
    states_name.sort()

    fig = px.choropleth(selected_data_n, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                            color="TransactionCount", color_continuous_scale="Rainbow",
                            range_color=(selected_data_n["TransactionCount"].min(), selected_data_n["TransactionCount"].max()),
                            hover_name="States", title=f"{map_title} TRANSACTION COUNT", fitbounds="locations",
                            height=600, width=600)

    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

    

######################################################################### Streamlit Part#################################################
st.set_page_config(layout="wide")
st.title("PHONEPE DATA VISUALIZATION AND EXPLORATION")

with st.sidebar:
    opt = option_menu("MENU", ["HOME", "DATA EXPLORATION", "TOP CHARTS"])

if opt == "HOME":
    pass

elif opt == "DATA EXPLORATION":
    tab1, tab2, tab3 = st.tabs(["Aggregated Analysis", "Map Analysis", "Top Analysis"])

    with tab1:
        method = st.radio("Select The Method",["Transaction Analysis","User Analysis"])

        if method == "Transaction Analysis":
            years_key = "transaction_years"  # Unique key for transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(aggregated_transaction_df["Years"].min()), max_value=int(aggregated_transaction_df["Years"].max()), value=(int(aggregated_transaction_df["Years"].min())))
            quarters_key = "transaction_quarters"  # Unique key for transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(aggregated_transaction_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            states_key = "transaction_for_states1"
            states_list = sorted(aggregated_transaction_df["States"].unique())
            if "All States" not in states_list:
                states_list.insert(0, "All States")
            selected_states = st.multiselect("Select States", key=states_key, options=states_list, default=["All States"])
            transaction_types_key = "transaction_types"
            transaction_types_list = sorted(aggregated_transaction_df["TransactionType"].unique())
            if "All Transaction Types" not in transaction_types_list:
                transaction_types_list.insert(0, "All Transaction Types")
            selected_transaction_types = st.multiselect("Select Transaction Types", key=transaction_types_key, options=transaction_types_list, default=["All Transaction Types"])

            Transaction_Analysis_Function(aggregated_transaction_df, years, quarters, selected_states,selected_transaction_types)

        elif method =="User Analysis":


            years_key = "transaction_User_years"  # Unique key for transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(aggregated_users_df["Years"].min()), max_value=int(aggregated_transaction_df["Years"].max()), value=(int(aggregated_transaction_df["Years"].min())))
            quarters_key = "transaction_User_quarters"  # Unique key for transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(aggregated_users_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            states_key = "transaction_for_User_states1"
            states_list = sorted(aggregated_users_df["States"].unique())
            if "All States" not in states_list:
                states_list.insert(0, "All States")
            selected_states = st.multiselect("Select States", key=states_key, options=states_list, default=["All States"])
            brand_types_key = "brands_types"
            brand_types_list = sorted(aggregated_users_df["Brands"].unique())
            if "All Brands" not in brand_types_key:
                brand_types_list.insert(0, "All Brands")
            selected_brand_types = st.multiselect("Select Brands", key=brand_types_key, options=brand_types_list, default=["All Brands"])

            Transaction_User_Function(aggregated_users_df, years, quarters, selected_states,selected_brand_types)

    with tab2:
        method = st.radio("Select The Method",["Map Transaction Analysis","Map User Analysis"])

        if method == "Map Transaction Analysis":
            years_key = "map_transaction_years"  # Unique key for map transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(map_transaction_df["Years"].min()), max_value=int(map_transaction_df["Years"].max()), value=(int(map_transaction_df["Years"].min())))
            quarters_key = "map_transaction_quarters"  # Unique key for map transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(map_transaction_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            states_key = "transaction_for_states2"
            states_list = sorted(map_transaction_df["States"].unique())
            if "All States" not in states_list:
                states_list.insert(0, "All States")
            selected_states = st.multiselect("Select States", key=states_key, options=states_list, default=["All States"])
            
            TransactionAmount_count(map_transaction_df, years, quarters, selected_states)

        elif method =="Map User Analysis":
            pass

    with tab3:
        method = st.radio("Select The Method",["Top Transaction Analysis","Top User Analysis"])

        if method == "Top Transaction Analysis":
            years_key = "top_transaction_years"  # Unique key for top transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(top_transaction_df["Years"].min()), max_value=int(top_transaction_df["Years"].max()), value=(int(top_transaction_df["Years"].min())))
            quarters_key = "top_transaction_quarters"  # Unique key for top transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(top_transaction_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            states_key = "transaction_for_states3"
            states_list = sorted(top_transaction_df["States"].unique())
            if "All States" not in states_list:
                states_list.insert(0, "All States")
            selected_states = st.multiselect("Select States", key=states_key, options=states_list, default=["All States"])

            TransactionAmount_count(top_transaction_df, years, quarters, selected_states)

        elif method =="Top User Analysis":
            pass
