import psycopg2
import streamlit as st
from datetime import datetime
import math


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


# =========================
# Streamlit Config
# =========================

st.set_page_config(
    page_title="Raiseup - CRM",
    layout="wide"
)


# =========================
# Create Users Table
# =========================

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()


# =========================
# Add User Modal
# =========================

@st.dialog("Add User")
def add_user():

    username = st.text_input("Username")

    email = st.text_input("Email")

    if st.button("➕ Add User"):

        if not username or not email:
            st.error("Username and Email are required.")
            return

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                username,
                email,
                datetime.now(),
                datetime.now()
            )
        )

        conn.commit()

        st.success("User Added Successfully")

        st.rerun()


# =========================
# Edit User Modal
# =========================

@st.dialog("Edit User")
def edit_user(user):

    username = st.text_input(
        "Username",
        value=user["username"]
    )

    email = st.text_input(
        "Email",
        value=user["email"]
    )

    if st.button("💾 Save Changes"):

        cursor.execute(
            """
            UPDATE users
            SET
                username = %s,
                email = %s,
                updated_at = %s
            WHERE id = %s
            """,
            (
                username,
                email,
                datetime.now(),
                user["id"]
            )
        )

        conn.commit()

        st.success("User Updated Successfully")

        st.rerun()


# =========================
# Pagination
# =========================

page_size = 10


# =========================
# Total Users
# =========================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM users
    """
)

total_users = cursor.fetchone()[0]


total_pages = math.ceil(
    total_users / page_size
) if total_users > 0 else 1


if "page" not in st.session_state:
    st.session_state["page"] = 1


# =========================
# Prevent Invalid Page
# =========================

if st.session_state["page"] > total_pages:
    st.session_state["page"] = total_pages


skip = (
    st.session_state["page"] - 1
) * page_size


# =========================
# Users This Month
# =========================

start_month = datetime.now().replace(
    day=1,
    hour=0,
    minute=0,
    second=0,
    microsecond=0
)


cursor.execute(
    """
    SELECT COUNT(*)
    FROM users
    WHERE created_at >= %s
    """,
    (start_month,)
)


users_this_month = cursor.fetchone()[0]


# =========================
# Get Users
# =========================

cursor.execute(
    """
    SELECT
        id,
        username,
        email,
        created_at,
        updated_at
    FROM users
    ORDER BY id DESC
    LIMIT %s
    OFFSET %s
    """,
    (
        page_size,
        skip
    )
)


rows = cursor.fetchall()


# =========================
# Convert Rows To Dictionary
# =========================

users_list = []

for row in rows:

    user = {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "created_at": row[3],
        "updated_at": row[4]
    }

    users_list.append(user)


# =========================
# Page Title
# =========================

st.title("CRM Data Explorer By PostgreSQL")

st.header("Users")


# =========================
# Add User Button
# =========================

if st.button("➕ Add User"):
    add_user()


st.divider()


# =========================
# Stats For Users
# =========================

col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Total Users",
        total_users
    )


with col2:

    st.metric(
        "Users This Month",
        users_this_month
    )


st.divider()


# =========================
# Users According To Month
# =========================

current_year = datetime.now().year


years = list(
    range(
        current_year,
        current_year - 10,
        -1
    )
)


selected_year = st.selectbox(
    "Select Year",
    years
)


# =========================
# Calculate Users Each Month
# =========================

monthly_users = []


for month in range(1, 13):

    start_date = datetime(
        selected_year,
        month,
        1
    )

    if month == 12:

        end_date = datetime(
            selected_year + 1,
            1,
            1
        )

    else:

        end_date = datetime(
            selected_year,
            month + 1,
            1
        )


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE created_at >= %s
        AND created_at < %s
        """,
        (
            start_date,
            end_date
        )
    )


    count = cursor.fetchone()[0]

    monthly_users.append(count)


# =========================
# Display Months
# =========================

months = [
    "Jan",
    "Feb",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


for i in range(0, 12, 4):

    cols = st.columns(4)

    for j, col in enumerate(cols):

        month_index = i + j

        with col:

            st.metric(
                months[month_index],
                monthly_users[month_index]
            )


st.divider()


# =========================
# Table Header
# =========================

header = st.columns(
    [3, 4, 2, 2, 1]
)


with header[0]:
    st.write("**Username**")


with header[1]:
    st.write("**Email**")


with header[2]:
    st.write("**Created At**")


with header[3]:
    st.write("**Updated At**")


with header[4]:
    st.write("**Action**")


st.divider()


# =========================
# Display Users
# =========================

for user in users_list:

    row = st.columns(
        [3, 4, 2, 2, 1]
    )


    with row[0]:

        st.write(
            user["username"]
        )


    with row[1]:

        st.write(
            user["email"]
        )


    with row[2]:

        if user["created_at"]:

            st.write(
                user["created_at"]
            )


    with row[3]:

        if user["updated_at"]:

            st.write(
                user["updated_at"]
            )


    with row[4]:

        if st.button(
            "🖊 Edit",
            key=f'edit_{user["id"]}'
        ):

            edit_user(user)


# =========================
# Pagination
# =========================

col1, col2, col3 = st.columns(
    [1, 3, 1]
)


with col1:

    if st.button(
        "⬅",
        disabled=st.session_state["page"] == 1
    ):

        st.session_state["page"] -= 1

        st.rerun()


with col2:

    st.write(
        f"Page {st.session_state['page']} "
        f"of {total_pages}"
    )


with col3:

    if st.button(
        "➡",
        disabled=st.session_state["page"] >= total_pages
    ):

        st.session_state["page"] += 1

        st.rerun()
