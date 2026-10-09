import psycopg2
from pymongo import MongoClient
import streamlit as st


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


# ============================================================
# 6. Transform - Normalize SQL Users
# ============================================================

# هنستخدم Set عشان نعرف عدد الـ unique emails
all_emails = set()

for user in sql_users:

    user_id = user[0]

    username = user[1].strip().lower()

    email = user[2].strip().lower()

    all_emails.add(email)


# ============================================================
# 7. Transform - Normalize MongoDB Users
# ============================================================

# Dictionary يحتوي Mongo Users
# key = MongoDB _id
# value = بيانات المستخدم

mongo_users_by_id = {}

for user in mongo_users:

    mongo_user_id = user["_id"]

    email = user.get("email", "").strip().lower()

    mongo_users_by_id[mongo_user_id] = {
        "id": mongo_user_id,
        "name": user.get("name", "").strip().lower(),
        "email": email,
        "age": user.get("age"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at")
    }

    # إضافة Mongo email للـ Set
    if email:
        all_emails.add(email)


# ============================================================
# 8. Group MongoDB Posts By User
# ============================================================

# الهدف:
#
# posts_by_user = {
#
#     user_id_1: [
#         post1,
#         post2
#     ],
#
#     user_id_2: [
#         post3,
#         post4
#     ]
#
# }

posts_by_user = {}

for post in mongo_posts:

    user_id = post.get("user_id")

    # لو الـ user_id مش موجود في الـ dictionary
    if user_id not in posts_by_user:

        posts_by_user[user_id] = []

    # مهم:
    # append لازم يكون خارج الـ if
    # عشان كل posts المستخدم تتضاف
    posts_by_user[user_id].append(post)


# ============================================================
# 9. Integrate PostgreSQL + MongoDB
# ============================================================
final_data = []
for sql_user in sql_users:
    # --------------------------------------------------------
    # SQL User Data
    # --------------------------------------------------------
    sql_id = sql_user[0]

    username = sql_user[1].strip().lower()

    email = sql_user[2].strip().lower()

    created_at = sql_user[3]

    updated_at = sql_user[4]
    # --------------------------------------------------------
    # Search for the same user inside MongoDB
    # --------------------------------------------------------
    mongo_user = None
    for user in mongo_users:

        mongo_email = user.get("email", "")

        if mongo_email:

            mongo_email = mongo_email.strip().lower()

        # Compare SQL email with Mongo email
        if mongo_email == email:
            mongo_user = user
            break

# --------------------------------------------------------
# Get MongoDB Posts
# --------------------------------------------------------

    user_posts = []
    if mongo_user:
        mongo_user_id = mongo_user["_id"]
        # Get all posts belonging to this Mongo user
        user_posts = posts_by_user.get(
            mongo_user_id,
            []
        )
 # --------------------------------------------------------
# Create Final Integrated User
# --------------------------------------------------------
    final_data.append({
        # PostgreSQL Data
        "sql_id": sql_id,
        "username": username,
        "email": email,
        "sql_created_at": created_at,
        "sql_updated_at": updated_at,
        # MongoDB User
        "mongo_user": mongo_user,
        # MongoDB Posts
        "posts": user_posts
    })

print ("\n==================")
print("Final Data ") 
for user in final_data:
    print(f"email {user['email']}")
    print(f"mongo user  {user['mongo_user']}")
    print("posts :")
    for post in user["posts"]:
        print(" -" , post.get("title"))
print ("==================\n")

 # --------------------------------------------------------
# Statstics
# --------------------------------------------------------

sql_users_count = len(sql_users)
mongo_users_count = len(mongo_users)
total_users = sql_users_count + mongo_users_count
total_unique_users = len(all_emails)


st.title("Users Integration Dashboard")
col1 , col2 , col3 ,col4 = st.columns(4)
with col1 :
    st.metric("SQL Users" , sql_users_count)
with col2 :
    st.metric("NoSQL Users" , mongo_users_count)
with col3 :
        st.metric("total Users" ,total_users)
with col4 :
        st.metric("total unique Users" ,total_unique_users)


st.divider()

st.subheader("Users")

for user in final_data:
    username = user["username"]
    email = user["email"]
    mongo_user = user["mongo_user"]
    posts = user["posts"]
    with st.container(border=True):
            st.subheader(username)
            st.write(f"Email {email}")
            if mongo_user:
                st.success("User Exist in mongo DB")
                mongo_name = mongo_user.get("name" , "N/A")
                mongo_age = mongo_user.get("age" , "N/A")
                st.write(f"Mongo Name  ({mongo_name})")
            #Display posts
            st.write(f"Posts ({len(posts)})")
            if posts:
                for posts in post :
                    st.markdown(f"{post.get("title" , "No Title")}")
                    st.subheader(f"{post.get("content" , "No content")}")
            else:
                st.info("This User doesn't have any posts ")        
