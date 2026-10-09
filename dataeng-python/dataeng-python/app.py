import psycopg2
import streamlit as st
 
 
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
            role
        FROM app_users
        WHERE email = %s
        AND password = %s
    """
 
    cursor.execute(
        query,
        (email, password)
    )
 
    user = cursor.fetchone()
 
    cursor.close()
    connection.close()
 
    return user
 
 
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
