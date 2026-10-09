import psycopg2
import streamlit as st
import bcrypt
 
 
# ==================================================
# PAGE CONFIGURATION
# ==================================================
 
st.set_page_config(
    page_title="RaiseUp - CRM",
    layout="wide"
)
 
 
# ==================================================
# POSTGRESQL CONNECTION
# ==================================================
 
def get_connection():
 
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="",
        user="postgres",
        password=""
    )
 
 
# ==================================================
# LOGIN FUNCTION
# ==================================================
 
def login(email, password):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            username,
            email,
            role,
            password
        FROM app_users
        WHERE email = %s
    """

    cursor.execute(query, (email,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user:

        stored_hash = user[4]

        if bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        ):
            return user[:4]

    return None
 
 
# ==================================================
# AUTHENTICATION
# ==================================================
 
if not st.session_state.get(
    "logged_in",
    False
):
 
    st.title("Login")
 
    email = st.text_input(
        "Email"
    )
 
    password = st.text_input(
        "Password",
        type="password"
    )
 
 
    # ==================================================
    # LOGIN BUTTON
    # ==================================================
 
    if st.button("Login"):
 
        user = login(
            email,
            password
        )
 
 
        # ==================================================
        # LOGIN SUCCESS
        # ==================================================
 
        if user:
 
            st.session_state["logged_in"] = True
 
            st.session_state["user_id"] = user[0]
 
            st.session_state["username"] = user[1]
 
            st.session_state["email"] = user[2]
 
            st.session_state["role"] = user[3]
 
            st.success(
                "Login Successfully"
            )
 
            st.rerun()
 
 
        # ==================================================
        # LOGIN FAILED
        # ==================================================
 
        else:
 
            st.error(
                "Invalid Email or Password"
            )
 
 
# ==================================================
# AUTHORIZED APPLICATION
# ==================================================
 
else:
 
    # ==================================================
    # CURRENT USER
    # ==================================================
 
    username = st.session_state["username"]
 
    role = st.session_state["role"]
 
 
    # ==================================================
    # SIDEBAR USER INFORMATION
    # ==================================================
 
    st.sidebar.write(
        f"Welcome {username}"
    )
 
    st.sidebar.write(
        f"Role: {role}"
    )
 
 
    # ==================================================
    # LOGOUT
    # ==================================================
 
    if st.sidebar.button("Logout"):
 
        st.session_state.clear()
 
        st.rerun()
 
 
    # ==================================================
    # PAGES
    # ==================================================
 
    mongo_page = st.Page(
        "pages/mongo.py",
        title="NoSQL Data",
        icon="🍃"
    )
 
 
    postgres_page = st.Page(
        "pages/postgres.py",
        title="SQL Data",
        icon="🐘"
    )
 
 
    etl_page = st.Page(
        "pages/etl_pipline.py",
        title="ETL"
    )
 
 
    oltp_olap_page = st.Page(
        "pages/oltp_olap.py",
        title="OLTP VS OLAP"
    )
 
 
    hadoop_demo = st.Page(
        "pages/hadoop_demo.py",
        title="Hadoop Demo"
    )
 
 
    partitioned = st.Page(
        "pages/partitioned.py",
        title="Partitioned"
    )
 
 
    add_user_pg = st.Page(
        "pages/add_user_pg.py",
        title="Add User PG"
    )
 
 
    # ==================================================
    # COMMON PAGES
    # ==================================================
 
    pages = [
 
        mongo_page,
 
        postgres_page,
 
        etl_page,
 
        oltp_olap_page,
 
        hadoop_demo,
 
        partitioned,
 
    ]
 
 
    # ==================================================
    # ADMIN ONLY PAGE
    # ==================================================
 
    if role == "super-admin":
 
        pages.append(
            add_user_pg
        )
 
 
    # ==================================================
    # NAVIGATION
    # ==================================================
 
    pg = st.navigation(
        {
            "Database": pages
        }
    )
 
 
    # ==================================================
    # RUN APPLICATION
    # ==================================================
 
    pg.run()
 
import psycopg2
import streamlit as st
from datetime import datetime
import pandas as pd
 
 
# ==================================================
# PAGE AUTHORIZATION
# ==================================================
 
if not st.session_state.get("logged_in", False):
 
    st.error("You must login first")
 
    st.stop()
 
 
# ==================================================
# GET CURRENT USER
# ==================================================
 
role = st.session_state.get("role")
 
 
# ==================================================
# POSTGRESQL CONNECTION
# ==================================================
 
def get_connection():
 
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="raiseup",
        user="postgres",
        password="12345"
    )
 
 # ==================================================
# HASH PASSWORD
# ==================================================
def hash_password(password):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


# ==================================================
# ADD USER
# ==================================================
 
def add_user(
    name,
    email,
    password,
    created_at
):
 
    connection = get_connection()
 
    cursor = connection.cursor()
 
    query = """
        INSERT INTO users_partitioned
        (
            username,
            email,
            password,
            created_at,
            updated_at
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """
    hashed_password = hash_password(password)

    cursor.execute(
        query,
        (
            name,
            email,
            hashed_password,
            created_at,
            created_at
        )
    )
 
    connection.commit()
 
    cursor.close()
    connection.close()
 
 
# ==================================================
# PAGE
# ==================================================
 
st.header("PostgreSQL Partitioning")
 
 
# ==================================================
# SHOW CURRENT ROLE
# ==================================================
 
st.write(
    f"Current Role: **{role}**"
)
 
 
# ==================================================
# USER FORM
# ==================================================
 
name = st.text_input(
    "Username"
)
 
email = st.text_input(
    "Email"
)
 
password = st.text_input(
    "Password",
    type="password"
)
 
created_at = st.date_input(
    "Created At"
)
 
 
# ==================================================
# ADD USER
# ==================================================
 
if st.button("Add User"):
 
    # ----------------------------------------------
    # Authorization
    # ----------------------------------------------
 
    if role != "super-admin":
 
        st.error(
            "You are not authorized to add users."
        )
 
        st.stop()
 
 
    # ----------------------------------------------
    # Validation
    # ----------------------------------------------
 
    if not name or not email or not password:
 
        st.warning(
            "Please fill all fields."
        )
 
        st.stop()
 
 
    # ----------------------------------------------
    # Insert User
    # ----------------------------------------------
 
    try:
 
        add_user(
            name,
            email,
            password,
            created_at
        )
 
        st.success(
            "User added successfully."
        )
 
    except Exception as e:
 
        st.error(
            f"Error: {e}"
        )
 
