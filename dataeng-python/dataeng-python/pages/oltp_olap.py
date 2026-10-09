import psycopg2
from pymongo import MongoClient
import streamlit as st
from datetime import datetime,timedelta
import pandas as pd
# six_month_ago = datetime.now() - timedelta(days=180)
# ============================================================
# 1. PostgreSQL Connection
# ============================================================

pg_conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="",
    user="postgres",
    password=""
)

pg_cursor = pg_conn.cursor()


# ============================================================
# 2. MongoDB Connection
# ============================================================

client = MongoClient("mongodb://localhost:27017/")

db = client["crm"]

users_collection = db["users"]
posts_collection = db["posts"]


# ============================================================
# 3. Extract - PostgreSQL
# ============================================================

pg_cursor.execute("""
    SELECT
        id,
        username,
        email,
        created_at,
        updated_at
    FROM users
""")

sql_users = pg_cursor.fetchall()


# ============================================================
# 4. Extract - MongoDB Users
# ============================================================

mongo_users = list(
    users_collection.find(
        {},
        {
            "_id": 1,
            "name": 1,
            "email": 1,
            "age": 1,
            "created_at": 1,
            "updated_at": 1
        }
    )
)


# ============================================================
# 5. Extract - MongoDB Posts
# ============================================================

mongo_posts = list(
    posts_collection.find(
        {},
        {
            "_id": 1,
            "user_id": 1,
            "title": 1,
            "content": 1,
            "created_at": 1,
            "updated_at": 1
        }
    )
)



# هنستخدم Set عشان نعرف عدد الـ unique emails
all_emails = set()

for user in sql_users:

    user_id = user[0]

    username = user[1].strip().lower()

    email = user[2].strip().lower()

    all_emails.add(email)


 # --------------------------------------------------------
 # Posts From the LAst 8 months
# --------------------------------------------------------
six_month_ago = datetime.now() - timedelta(days=182)

print(six_month_ago)
top_users = list(posts_collection.aggregate([
    {
        #1. Filter Posts From the last 6 months
        "$match" : {
            "created_at" : {
                "$gte" : six_month_ago
            }
        }
    },
    # 2. Group posts by user
    {
        "$group" :{
            "_id" : "$user_id" ,
            "posts_count" : {
                "$sum" : 1
            }
        }
    },
    #3 Sort from The Highest to Lowest
    {
        "$sort" : {
            "posts_count" : -1
        }
    },
    #4 Get top 10 users
    {
        "$limit" : 10
    },
    # 5. Join with users collection
    {
        "$lookup":{
            "from": "users",
            "localField":"_id",
            "foreignField": "_id",
            "as" : "user"
        }
    },
    #6. convert user array to object
    {
        "$unwind": "$user"
    },
    #7. SELECT FIELDS
    {
        "$project" : {
            "_id" : 0,
            "name" : "$user.name",
            "email": "$user.email",
            "posts_count": 1
        }
    }
]))


 # --------------------------------------------------------
# Statstics
# --------------------------------------------------------

sql_users_count = len(sql_users)
mongo_users_count = len(mongo_users)
total_users = sql_users_count + mongo_users_count
total_unique_users = len(all_emails)


st.title("Users Integration Dashboard")
col1 , col2 , col3 ,col4,col5 = st.columns(5)
with col1 :
    st.metric("SQL Users" , sql_users_count)
with col2 :
    st.metric("NoSQL Users" , mongo_users_count)
with col3 :
        st.metric("total Users" ,total_users)
with col4 :
        st.metric("total unique Users" ,total_unique_users)
with col5 :
        st.metric("total Posts" ,len(mongo_posts))

st.divider()


st.subheader("Top Users - Most post in the last 6 Months")
df = pd.DataFrame(top_users)
st.bar_chart(df,x="name", y="posts_count")
st.dataframe(df,use_container_width=True)
