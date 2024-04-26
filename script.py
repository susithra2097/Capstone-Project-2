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


#####################################################Functions##########################################################################

def TransactionAmount_count(df, year, quarters):
    df["Years"] = df["Years"].astype(int)
    
    if quarters == "All Quarters":
        selected_data = df[df["Years"] == year]
        quarter_title = f"{year}"
        map_title = f"{year}"
    else:
        selected_data = df[(df["Years"] == year) & (df["Quarter"] == quarters)]
        quarter_title = f"{year} {quarters}Q"
        map_title = f"{year} {quarters}Q"

    #if not selected_states or "All States" in selected_states:
        #selected_data = df
    #else:
        #selected_data = selected_data[selected_data["States"].isin(selected_states)]
        
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
    if "Districts" in selected_data.columns:
        selected_data_n = selected_data.groupby(["States", "Districts"])[["TransactionCount", "TransactionAmount"]].sum().reset_index()
    elif "Pincodes" in selected_data.columns:
        selected_data_n = selected_data.groupby(["States", "Pincodes"])[["TransactionCount", "TransactionAmount"]].sum().reset_index()
    else:
        selected_data_n = selected_data.groupby(["States"])[["TransactionCount", "TransactionAmount"]].sum().reset_index()
    return selected_data_n
    

def add_state_selectbox(selected_data_n, selected_states, df):
    selected_data_n = selected_data_n[selected_data_n["States"].isin(selected_states)]
    
    # Plot pie chart for TransactionType
    transaction_type_data = df[df["States"].isin(selected_states)].groupby("TransactionType").sum().reset_index()
    fig_pie = px.pie(transaction_type_data, values="TransactionAmount", names="TransactionType",
                     title="Transaction Type Distribution")
    st.plotly_chart(fig_pie)



def add_brand_selectbox(selected_data_n, selected_states, df):
    selected_data_n = selected_data_n[selected_data_n["States"].isin(selected_states)]
    
    # Plot pie chart for Brands
    brand_data = df[df["States"].isin(selected_states)].groupby("Brands").sum().reset_index()
    fig_pie = px.pie(brand_data, values="TransactionCount", names="Brands",
                     title="Brands by State")
    st.plotly_chart(fig_pie)

def TransactionCount_count(df, year, quarters):
    df["Years"] = df["Years"].astype(int)
    
    if quarters == "All Quarters":
        selected_data = df[df["Years"] == year]
        quarter_title = f"{year}"
        map_title = f"{year}"
    else:
        selected_data = df[(df["Years"] == year) & (df["Quarter"] == quarters)]
        quarter_title = f"{year} {quarters}Q"
        map_title = f"{year} {quarters}Q"

    selected_data.reset_index(drop=True, inplace=True)

    selected_data_n = selected_data.groupby("States")[["TransactionCount"]].sum()
    selected_data_n.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        Count_chart = px.bar(selected_data_n, x="States", y="TransactionCount", title=f"{quarter_title} TRANSACTION COUNT",
                             color_discrete_sequence=px.colors.sequential.Bluered_r, width=600, height=600)
        st.plotly_chart(Count_chart)

    with col2:
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)  # Define data1 here
        fig1 = px.choropleth(selected_data_n, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                             color="TransactionCount", color_continuous_scale="Rainbow",
                             range_color=(selected_data_n["TransactionCount"].min(), selected_data_n["TransactionCount"].max()),
                             hover_name="States", title=f"{map_title} TRANSACTION COUNT", fitbounds="locations",
                             height=600, width=600)

        fig1.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig1)

    selected_data_n1 = selected_data.groupby(["States", "Brands"])["TransactionCount"].sum().reset_index()
    
    return selected_data_n1


def map_transaction_analysis(selected_data, year, quarter, selected_states):
    selected_data = selected_data[selected_data["States"].isin(selected_states)]
    
    # Group data by districts and sum transaction amount and count
    district_data = selected_data.groupby("Districts").agg({"TransactionAmount": "sum", "TransactionCount": "sum"}).reset_index()
    
    # Create separate column charts for transaction amount and count
    fig_amount = px.bar(district_data, y="Districts", x="TransactionAmount", 
                        title=f"Districts Transaction Amount - {year} {quarter}",
                        color_discrete_sequence=px.colors.qualitative.Plotly,
                        orientation="h",height=500,width=500)
    
    fig_count = px.bar(district_data, y="Districts", x="TransactionCount", 
                       title=f"Districts Transaction Count - {year} {quarter}",
                       color_discrete_sequence=px.colors.qualitative.Plotly,
                       orientation="h",height=500,width=500)
    col1, col2 = st.columns(2)
    with col1:
    # Display the charts
        st.plotly_chart(fig_amount)
    with col2:
        st.plotly_chart(fig_count)


def RegisteredUsers_count(df, year, quarters):
    df["Years"] = df["Years"].astype(int)
    
    if quarters == "All Quarters":
        selected_data = df[df["Years"] == year]
        quarter_title = f"{year}"
        map_title = f"{year}"
    else:
        selected_data = df[(df["Years"] == year) & (df["Quarter"] == quarters)]
        quarter_title = f"{year} {quarters}Q"
        map_title = f"{year} {quarters}Q"

    selected_data.reset_index(drop=True, inplace=True)

    selected_data_n = selected_data.groupby("States")[["RegisteredUsers"]].sum()
    selected_data_n.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        Users_chart = px.bar(selected_data_n, x="States", y="RegisteredUsers", title=f"{quarter_title} REGISTERED USERS COUNT",
                             color_discrete_sequence=px.colors.sequential.Bluered_r, width=600, height=600)
        st.plotly_chart(Users_chart)

    with col2:
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)  # Define data1 here
        fig1 = px.choropleth(selected_data_n, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                             color="RegisteredUsers", color_continuous_scale="Rainbow",
                             range_color=(selected_data_n["RegisteredUsers"].min(), selected_data_n["RegisteredUsers"].max()),
                             hover_name="States", title=f"{map_title} REGISTERED USERS COUNT", fitbounds="locations",
                             height=600, width=600)

        fig1.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig1)
    if "Districts" in selected_data.columns:
        selected_data_n1 = selected_data.groupby(["States", "Districts"])["RegisteredUsers"].sum().reset_index()
    else:
        selected_data_n1 = selected_data.groupby(["States"])["RegisteredUsers"].sum().reset_index()
    return selected_data_n1


def map_registered_users_analysis(selected_data, year, quarter, selected_states):
    selected_data = selected_data[selected_data["States"].isin(selected_states)]

    # Group data by districts and sum registered users count
    district_data = selected_data.groupby("Districts").agg({"RegisteredUsers": "sum"}).reset_index()

    # Create column chart for registered users count
    fig_registered_users = px.bar(district_data, y="Districts", x="RegisteredUsers", 
                                  title=f"Districts Registered Users Count - {year} {quarter}",
                                  color_discrete_sequence=px.colors.qualitative.Plotly,
                                  orientation="h", height=500, width=500)

    # Display the chart
    st.plotly_chart(fig_registered_users)

   
def top_transaction_analysis(selected_data, selected_states):
    tiy= selected_data[selected_data["States"].isin(selected_states)]
    tiy.reset_index(drop= True, inplace= True)
    col1,col2= st.columns(2)
    with col1:
        fig_top_insur_bar_1= px.bar(tiy, x= "States", y= "TransactionAmount", hover_data= "Pincodes",
                                title= "TRANSACTION AMOUNT", height= 600,width= 400, color_discrete_sequence= px.colors.sequential.GnBu_r)
        st.plotly_chart(fig_top_insur_bar_1)

    with col2:

        fig_top_insur_bar_2= px.bar(tiy, x= "States", y= "TransactionCount", hover_data= "Pincodes",
                                title= "TRANSACTION COUNT", height= 600,width= 400, color_discrete_sequence= px.colors.sequential.Agsunset_r)
        st.plotly_chart(fig_top_insur_bar_2)



######################################################################### Streamlit Part#################################################
st.set_page_config(layout="wide")
##st.title("PHONEPE DATA VISUALIZATION AND EXPLORATION")

with st.sidebar:
    opt = option_menu("MENU", ["HOME", "DATA EXPLORATION", "TOP CHARTS & QUESTIONS"])

if opt == "HOME":
    st.image("C:\\Users\\91936\\OneDrive\\Desktop\\Guvi\\Capstone Project 2 -Phonepe\\img.png")
    st.markdown("# :violet[Data Visualization and Exploration]")
    st.markdown("## :violet[A User-Friendly Tool Using Streamlit and Plotly]")
    col1,col2 = st.columns([3,2],gap="medium")
    with col1:
        st.write(" ")
        st.write(" ")
        st.markdown("### :violet[Technologies used :]  Python, Pandas, MySQL, mysql-connector-python, Streamlit, and Plotly.")
        st.markdown("### :violet[Overview :] In this streamlit web app you can visualize the phonepe pulse data and gain lot of insights on transactions, number of users, top 10 state, district, pincode and which brand has most number of users and so on. Bar charts, Pie charts and Geo map visualization are used to get some insights.")
    with col2:
        st.image("C:\\Users\\91936\\OneDrive\\Desktop\\Guvi\\Capstone Project 2 -Phonepe\\home.png")

elif opt == "DATA EXPLORATION":
    st.markdown("# :violet[DATA EXPLORATION]")
    tab1, tab2, tab3 = st.tabs(["Aggregated Analysis", "Map Analysis", "Top Analysis"])

    with tab1:
        method = st.radio("Select The Method",["Transaction Analysis","User Analysis"])

        if method == "Transaction Analysis":
            years_key = "transaction_years"  # Unique key for transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(aggregated_transaction_df["Years"].min()), max_value=int(aggregated_transaction_df["Years"].max()), value=(int(aggregated_transaction_df["Years"].min())))
            quarters_key = "transaction_quarters"  # Unique key for transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(aggregated_transaction_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            selected_data_n =TransactionAmount_count(aggregated_transaction_df, years, quarters)

            states = selected_data_n["States"].unique().tolist()
            selected_states = st.multiselect("Select States", states, default=["Tamil Nadu"])

            add_state_selectbox(selected_data_n,selected_states,aggregated_transaction_df)

        elif method =="User Analysis":
            years_key = "transaction_years"  # Unique key for transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(aggregated_users_df["Years"].min()), max_value=int(aggregated_users_df["Years"].max()), value=(int(aggregated_users_df["Years"].min())))
            quarters_key = "transaction_quarters"  # Unique key for transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(aggregated_users_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            selected_data_n1 = TransactionCount_count(aggregated_users_df, years, quarters)
            
            states = selected_data_n1["States"].unique().tolist()
            selected_states = st.multiselect("Select States", states, default=["Tamil Nadu"])
            add_brand_selectbox(selected_data_n1, selected_states, aggregated_users_df)

    with tab2:
        method = st.radio("Select The Method",["Map Transaction Analysis","Map User Analysis"])

        if method == "Map Transaction Analysis":
            years_key = "Map_transaction_years"  # Unique key for transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(map_transaction_df["Years"].min()), max_value=int(map_transaction_df["Years"].max()), value=(int(map_transaction_df["Years"].min())))
            quarters_key = "Map_transaction_quarters"  # Unique key for transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(map_transaction_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            selected_data_n =TransactionAmount_count(map_transaction_df, years, quarters)
            states = selected_data_n["States"].unique().tolist()
            selected_states = st.multiselect("Select States Map Transaction", states, default=["Tamil Nadu"])
            map_transaction_analysis(selected_data_n, years, quarters, selected_states)

        elif method =="Map User Analysis":
            years_key = "Map_transaction_years"  # Unique key for transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(map_user_df["Years"].min()), max_value=int(map_user_df["Years"].max()), value=(int(map_user_df["Years"].min())))
            quarters_key = "Map_transaction_quarters"  # Unique key for transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(map_user_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            selected_data_n =RegisteredUsers_count(map_user_df, years, quarters)
            states = selected_data_n["States"].unique().tolist()
            selected_states = st.multiselect("Select States Map Transaction", states, default=["Tamil Nadu"])
            map_registered_users_analysis(selected_data_n, years, quarters, selected_states)


    with tab3:
        method = st.radio("Select The Method",["Top Transaction Analysis","Top User Analysis"])

        if method == "Top Transaction Analysis":
            years_key = "top_transaction_years"  # Unique key for transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(top_transaction_df["Years"].min()), max_value=int(top_transaction_df["Years"].max()), value=(int(top_transaction_df["Years"].min())))
            quarters_key = "top_transaction_quarters"  # Unique key for transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(top_transaction_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            selected_data_n2 =TransactionAmount_count(top_transaction_df, years, quarters)
            states = selected_data_n2["States"].unique().tolist()
            selected_states = st.multiselect("Select States Top Transaction", states, default=["Tamil Nadu"])
            top_transaction_analysis(selected_data_n2,selected_states)
        elif method =="Top User Analysis":
            years_key = "Top_transaction_years"  # Unique key for transaction years slider
            years = st.slider("Select The Year", key=years_key, min_value=int(top_user_df["Years"].min()), max_value=int(top_user_df["Years"].max()), value=(int(top_user_df["Years"].min())))
            quarters_key = "Top_transaction_quarters"  # Unique key for transaction quarters dropdown
            quarters_options = ["All Quarters"] + sorted(top_user_df["Quarter"].unique())  # Include "All Quarters" option
            quarters = st.selectbox("Select The Quarter", key=quarters_key, options=quarters_options)
            selected_data_n =RegisteredUsers_count(top_user_df, years, quarters)

elif opt == "TOP CHARTS & QUESTIONS":

   
# Assuming you have loaded your dataframes: aggregated_users_df, aggregated_transaction_df, map_transaction_df, map_user_df

    questions = [
        'Top Brands Of Mobile Used',
        'States With Lowest Trasaction Amount',
        'Districts With Highest Transaction Amount',
        'Top 10 Districts With Lowest Transaction Amount',
        'Top 10 States With AppOpens',
        'Least 10 States With AppOpens',
        'States With Lowest Trasaction Count',
        'States With Highest Trasaction Count',
        'States With Highest Trasaction Amount',
        'Top 50 Districts With Lowest Transaction Amount'
    ]

    ques = st.selectbox("Select the question", questions)

    if ques == "Top Brands Of Mobile Used":
        brand = aggregated_users_df[["Brands", "TransactionCount"]]
        brand1 = brand.groupby("Brands")["TransactionCount"].sum().sort_values(ascending=False)
        brand2 = pd.DataFrame(brand1).reset_index()

        fig_brands = px.pie(brand2, values="TransactionCount", names="Brands", color_discrete_sequence=px.colors.sequential.dense_r,
                            title="Top Mobile Brands of Transaction_count")
        st.plotly_chart(fig_brands)

    elif ques == "States With Lowest Trasaction Amount":
        lt = aggregated_transaction_df[["States", "TransactionAmount"]]
        lt1 = lt.groupby("States")["TransactionAmount"].sum().sort_values(ascending=True)
        lt2 = pd.DataFrame(lt1).reset_index().head(10)

        fig_lts = px.bar(lt2, x="States", y="TransactionAmount", title="LOWEST TRANSACTION AMOUNT and STATES",
                        color_discrete_sequence=px.colors.sequential.Oranges_r)
        st.plotly_chart(fig_lts)

    elif ques == "Districts With Highest Transaction Amount":
        htd = map_transaction_df[["Districts", "TransactionAmount"]]
        htd1 = htd.groupby("Districts")["TransactionAmount"].sum().sort_values(ascending=False)
        htd2 = pd.DataFrame(htd1).head(10).reset_index()

        fig_htd = px.pie(htd2, values="TransactionAmount", names="Districts",
                        title="TOP 10 DISTRICTS OF HIGHEST TRANSACTION AMOUNT",
                        color_discrete_sequence=px.colors.sequential.Emrld_r)
        st.plotly_chart(fig_htd)

    elif ques == "Top 10 Districts With Lowest Transaction Amount":
        htd = map_transaction_df[["Districts", "TransactionAmount"]]
        htd1 = htd.groupby("Districts")["TransactionAmount"].sum().sort_values(ascending=True)
        htd2 = pd.DataFrame(htd1).head(10).reset_index()

        fig_htd = px.pie(htd2, values="TransactionAmount", names="Districts",
                        title="TOP 10 DISTRICTS OF LOWEST TRANSACTION AMOUNT",
                        color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_htd)

    elif ques == "Top 10 States With AppOpens":
        sa = map_user_df[["States", "AppOpens"]]
        sa1 = sa.groupby("States")["AppOpens"].sum().sort_values(ascending=False)
        sa2 = pd.DataFrame(sa1).reset_index().head(10)

        fig_sa = px.line(sa2, x="States", y="AppOpens", title="Top 10 States with AppOpens",
                        color_discrete_sequence=px.colors.sequential.deep_r)
        st.plotly_chart(fig_sa)

    elif ques == "Least 10 States With AppOpens":
        sa = map_user_df[["States", "AppOpens"]]
        sa1 = sa.groupby("States")["AppOpens"].sum().sort_values(ascending=True)
        sa2 = pd.DataFrame(sa1).reset_index().head(10)

        fig_sa = px.line(sa2, x="States", y="AppOpens", title="Least 10 States with AppOpens",
                        color_discrete_sequence=px.colors.sequential.dense_r)
        st.plotly_chart(fig_sa)

    elif ques == "States With Lowest Trasaction Count":
        stc = aggregated_transaction_df[["States", "TransactionCount"]]
        stc1 = stc.groupby("States")["TransactionCount"].sum().sort_values(ascending=True)
        stc2 = pd.DataFrame(stc1).reset_index()

        fig_stc = px.bar(stc2, x="States", y="TransactionCount", title="STATES WITH LOWEST TRANSACTION COUNT",
                        color_discrete_sequence=px.colors.sequential.Jet_r)
        st.plotly_chart(fig_stc)

    elif ques == "States With Highest Trasaction Count":
        stc = aggregated_transaction_df[["States", "TransactionCount"]]
        stc1 = stc.groupby("States")["TransactionCount"].sum().sort_values(ascending=False)
        stc2 = pd.DataFrame(stc1).reset_index()

        fig_stc = px.bar(stc2, x="States", y="TransactionCount", title="STATES WITH HIGHEST TRANSACTION COUNT",
                        color_discrete_sequence=px.colors.sequential.Magenta_r)
        st.plotly_chart(fig_stc)

    elif ques == "States With Highest Trasaction Amount":
        ht = aggregated_transaction_df[["States", "TransactionAmount"]]
        ht1 = ht.groupby("States")["TransactionAmount"].sum().sort_values(ascending=False)
        ht2 = pd.DataFrame(ht1).reset_index().head(10)

        fig_ht = px.line(ht2, x="States", y="TransactionAmount",
                        title="STATES WITH HIGHEST TRANSACTION AMOUNT and STATES",
                        color_discrete_sequence=px.colors.sequential.Oranges_r)
        st.plotly_chart(fig_ht)

    elif ques == "Top 50 Districts With Lowest Transaction Amount":
        dt = map_transaction_df[["Districts", "TransactionAmount"]]
        dt1 = dt.groupby("Districts")["TransactionAmount"].sum().sort_values(ascending=True)
        dt2 = pd.DataFrame(dt1).reset_index().head(50)

        fig_dt = px.bar(dt2, x="Districts", y="TransactionAmount", title="DISTRICTS WITH LOWEST TRANSACTION AMOUNT",
                        color_discrete_sequence=px.colors.sequential.Mint_r)
        st.plotly_chart(fig_dt)
