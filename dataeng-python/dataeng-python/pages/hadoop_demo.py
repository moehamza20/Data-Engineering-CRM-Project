# Spark => Mongo (JSON)
# Batch and Stream Processing
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import (col , count , desc)
import streamlit as st
import os


# =========================
# Connect to MongoDB
# =========================
client = MongoClient("mongodb://localhost:27017/")
db = client["crm"]
 
users_collection = db["users"]
posts_collection = db["posts"]
 
 
# =========================
#  Extract mongo DB Data
# =========================
 
mongo_users = list(users_collection.find({} , {
    "_id" : 1 ,
    "name" : 1
}))
 
 # how to make your data batched? (make data at list |collection)
 
 
mongo_posts = list(posts_collection.find({} , {
     "_id" : 1 ,
     "user_id" : 1 ,
     "title" : 1 ,
     "content" : 1 ,
     "created_at" : 1 ,
     "updated_at" : 1
}))
 
# ========================================
#  Convert the MongoDB to Json(Serialized)
# =========================================
import json
 
clean_posts = []
 
for post in mongo_posts:
    clean_posts.append({
        "id" : str(post["_id"]) ,
        "user_id" : str(post["user_id"]),
        "title" : post.get("title" , "") ,
        "content" : post.get("content" , "") ,
        "created_at" : str(post.get("created_at" , "") ),
        "updated_at" : str(post.get("updated_at" , "") ),
       
    })
   
   
# ========================================
#   Save Raw Data
# ========================================
 
with open("posts.json" , "w") as file:
    json.dump(clean_posts , file , ensure_ascii=False , indent=2)
print("posts.json created successfully")
 
# ========================================
# Create Spark Session
# ========================================
spark = (
    SparkSession.builder
    .appName("Raiseup Hadoop Demo")
    .master("local[4]")
    .config("spark.sql.shuffle.partitions" , "4")
    .getOrCreate()
)
 
# ========================================
# Read Data (Posts & users) Batch Processing
# ========================================
posts_df = (
    spark.read
    .option("multiLine", True)
    .json("posts.json")
)
 
posts_df = posts_df.repartition(4)

#Demo FOr Load post df partitions
def show_partition(index,iterator):
    rows = list(iterator)
    print(f"Partition: {index}, Rows: {len(rows)} sec")
    return iter(rows)
 
posts_df.rdd.mapPartitionsWithIndex(show_partition).count()

 
users_df = spark.createDataFrame([
    {
        "user_id" : str(user["_id"]) ,
        "name" : user.get("name" , "")
    }
    for user in mongo_users
])


# ========================================
# Check Data
# ========================================
posts_df.printSchema()
posts_df.show(truncate=False)
 
# ========================================
# Join Posts , users
# ========================================
 
posts_with_user = posts_df.join(users_df , posts_df.user_id == users_df.user_id , "left")
users_without_posts =(
    users_df.join(
        posts_with_user.select("id").distinct(),users_df.user_id == col("user_id"),"left_anti"
    )
)

# ========================================
# Total Posts, users
# ========================================
total_posts = posts_df.count()
total_users = users_df.count()
 
# ========================================
# Posts Per User
# ========================================
posts_per_user = (
    posts_with_user
    .groupBy("name")
    .agg(
        count("*").alias("posts_count")
    )
    .orderBy(
        desc("posts_count")
    )
)

# Distributed processing
posts_per_user.explain()


# Parallel Processing
filtered_posts = posts_df.filter(
    col("title").isNotNull()
)

long_posts = posts_df.filter(
    col("content").isNotNull()
)

print("Filter Created")
filtered_posts.show() #Action (.show() )

print("Long Posts Check created")
long_posts.show()

# ========================================
# Top 10 Users
# ========================================
top_users = posts_per_user.limit(10)
 
top_users.show()
 
# ========================================
# Display Data
# ========================================

st.header("Distributed Processing")
col1,col2 = st.columns(2)
with col1:
    st.metric("Spark Master","local[*]")
with col2:
    st.metric("Partitions", posts_df.rdd.getNumPartitions())


 
 
col1, col2 = st.columns(2)
 
st.divider()
st.header("Mongo Data")
with col1:
    st.metric("Total Posts" , total_posts)
with col2:
    st.metric("Total Users" , total_users)
# ========================================
# Posts Data
# ========================================
st.subheader("All Posts")
posts_table = (
    posts_with_user.select("name" , "title" , "content" , "created_at" , "updated_at").toPandas()
    )
 
st.dataframe (posts_table , use_container_width=True)
 
# ========================================
# Posts Per User Data
# ========================================
st.header("Posts per User")
posts_per_user_table = (posts_per_user.toPandas())
 
st.dataframe(posts_per_user_table , use_container_width=True)
 
# ========================================
# User without posts
# ========================================
st.subheader("User without posts")
st.dataframe(users_without_posts.select("name").toPandas() , use_container_width=True)

# ========================================
# Top 10 users
# ========================================
st.divider()
st.header("Top 10 Users")
top_users_table = (top_users.toPandas())
 
st.dataframe(top_users_table , use_container_width=True)
 
# ========================================
# Bar Chart
# ========================================
st.subheader("Top Users - Number of posts")
 
st.bar_chart(top_users_table , x="name" , y="posts_count")
 

# ========================================
# Stop Spark
# ========================================
spark.stop()
client.close()