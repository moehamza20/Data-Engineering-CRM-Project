import psycopg2
import streamlit as st
from datetime import datetime
import math
import pandas as pd

# =========================
# PostgreSQL Connection
# =========================

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="",
    user="postgres",
    password=""
)

cursor = conn.cursor()

# query = """ SELECT * FROM users_partitioned WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01'; """ #Partition pruning
query = """ SELECT tableoid::regclass AS partition_name, * FROM users_partitioned; """ #Partition tables

users_df = pd.read_sql(query,conn) 

partition_count = (users_df.groupby("partition_name").size().reset_index(name="users_count"))

selected_partition = st.selectbox("Select Partition", users_df['partition_name'].unique())
selected_users = users_df[users_df["partition_name"] == selected_partition]



st.title("PostgreSQL Partitioning")
st.subheader(f"Data From {selected_partition}")
st.dataframe(selected_users,use_container_width=True)

st.header("Users per Partition")
st.dataframe(partition_count,use_container_width=True)
st.dataframe(users_df,use_container_width=True)

#present the data in charts

st.bar_chart(partition_count,x="partition_name",y="users_count")
