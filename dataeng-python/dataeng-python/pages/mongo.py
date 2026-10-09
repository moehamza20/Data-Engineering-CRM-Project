from pymongo import MongoClient
import streamlit as st
from datetime import datetime
import math 

# =========================
# Connect to MongoDB
# =========================
client = MongoClient("mongodb://localhost:27017/")
db = client["crm"]

users_collection = db["users"]
posts_collection = db["posts"]

# =========================
# Streamlit Config
# =========================
st.set_page_config(
    page_title="Raiseup - CRM",
    layout="wide"
)


# =========================
# Add User Modal
# =========================
@st.dialog("Add User")
def add_user():
    name = st.text_input("Name")
    email = st.text_input("Email")
    age = st.number_input(
        "Age",
        min_value=1,
        max_value=100,
        step=1,
        value=18
    )

    if st.button("➕ Add User"):
        if not name or not email:
            st.error("Name and Email are required.")
            return

        user = {
            "name": name,
            "email": email,
            "age": age,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        users_collection.insert_one(user)

        st.success("User Added Successfully")
        st.rerun()


# =========================
# Edit User Modal
# =========================
@st.dialog("Edit User")
def edit_user(user):
    name = st.text_input(
        "Name",
        value=user.get("name", "")
    )

    email = st.text_input(
        "Email",
        value=user.get("email", "")
    )

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=100,
        step=1,
        value=user.get("age", 18)
    )

    if st.button("💾 Save Changes"):
        users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "name": name,
                    "email": email,
                    "age": age,
                    "updated_at": datetime.now()
                }
            }
        )

        st.success("User Updated Successfully")
        st.rerun()


# =========================
# Get Users
# =========================
page_size = 10
# total users 
total_users = users_collection.count_documents({})
total_pages = math.ceil(total_users / page_size)
if "page" not in st.session_state:
    st.session_state["page"] = 1

skip = (st.session_state["page"] - 1) * page_size


#user sign at this month 
start_month= datetime.now().replace(day=1 , hour=0 , minute=0 , second=0 , microsecond=0)
users_this_month = users_collection.count_documents({
    "created_at" : {
        "$gte" : start_month
    }
})





users_data = users_collection.find(
    {},
    {
        "_id": 1,
        "name": 1,
        "email": 1,
        "age": 1,
        "created_at": 1,
        "updated_at": 1
    }
).skip(skip).limit(page_size)

users_list = list(users_data)


# =========================
# Page Title
# =========================
st.title("CRM Data Explorer By mongo")
st.header("Users")


# =========================
# Add User Button
# =========================
if st.button("➕ Add User"):
    add_user()


st.divider()
#===============
#Stats for users
#================
col1 , col2 = st.columns(2)
with col1 :
    st.metric("Total users" , total_users)
with col2 :
    st.metric("Users This month" , users_this_month)
st.divider()

#users sign accordinf to month
current_year = datetime.now().year 
years = list(range(current_year , current_year -10  , -1 ))
selected_year = st.selectbox("select year" , years)

#calcualte users each month
monthly_users = [] 
for month in range(1 , 13):
    start_date = datetime(selected_year , month , 1 )
    if month == 12 :
        end_date= datetime(selected_year + 1 , 1  , 1)
    else:
        end_date= datetime(selected_year  , month + 1 ,1)
    count = users_collection.count_documents({
        "created_at" : {
                "$gte" : start_date,
                "$lte" : end_date
        }
    })
    monthly_users.append(count)
# st.write(monthly_users)

months= ["Jan" , "Feb"  , "March " , "April" , "May" , "june" , "July" , "August" , "septemper" , "october" , "november" , "december"]
for i in range(0 , 12 , 4):
    cols = st.columns(4)
    for j , col in enumerate(cols):
        month_index = i + j 
        with col: st.metric(months[month_index] , monthly_users[month_index])   

st.divider()
# =========================
# Table Header
# =========================
header = st.columns([2, 3, 1, 2, 2, 1])

with header[0]:
    st.write("**Name**")

with header[1]:
    st.write("**Email**")

with header[2]:
    st.write("**Age**")

with header[3]:
    st.write("**Created At**")

with header[4]:
    st.write("**Updated At**")

with header[5]:
    st.write("**Action**")


st.divider()


# =========================
# Display Users
# =========================
for user in users_list:

    row = st.columns([2, 3, 1, 2, 2, 1])

    with row[0]:
        st.write(user.get("name", ""))

    with row[1]:
        st.write(user.get("email", ""))

    with row[2]:
        st.write(user.get("age", ""))

    with row[3]:
        created_at = user.get("created_at", "")
        if created_at:
            st.write(created_at)

    with row[4]:
        updated_at = user.get("updated_at", "")
        if updated_at:
            st.write(updated_at)

    with row[5]:
        if st.button( "🖊 Edit",key=f'edit_{user["_id"]}'):
            edit_user(user)

#pagination 
col1,col2,col3 = st.columns([1 , 3 , 1])
with col1:
    if st.button("⬅" , disabled= st.session_state["page"] == 1):
        st.session_state.page -=1
        st.rerun()
with col2:
    st.write(f"Page {st.session_state.page} of {total_pages}")
with col3:
    if st.button("➡" , disabled= st.session_state["page"] == total_pages ):
        st.session_state.page +=1
        st.rerun()      


