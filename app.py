import streamlit as st
import sqlite3

# ------------------ Database Setup ------------------

def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

# ------------------ Database Functions ------------------

def create_user(username, password, email):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users(username, password, email) VALUES (?, ?, ?)", (username, password, email))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def add_task(user_id, task):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks(user_id, task) VALUES (?, ?)", (user_id, task))
    conn.commit()
    conn.close()

def get_tasks(user_id):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT id, task, status FROM tasks WHERE user_id=?", (user_id,))
    tasks = c.fetchall()
    conn.close()
    return tasks

def mark_done(task_id):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

# ------------------ UI Styling ------------------

st.set_page_config(page_title="Task Manager", page_icon="✅", layout="wide")

st.markdown("""
<style>
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

init_db()

# ------------------ Login System ------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Login or Create Account")

    menu = st.selectbox("Select Option", ["Login", "Sign Up"])

    if menu == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = verify_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    else:
        username = st.text_input("Choose Username")
        email = st.text_input("Email (Optional)")
        password = st.text_input("Choose Password", type="password")

        if st.button("Create Account"):
            if create_user(username, password, email):
                st.success("✅ Account created! Now login.")
            else:
                st.error("⚠ Username already exists!")

# ------------------ Dashboard ------------------

else:
    st.sidebar.title("🔧 Menu")
    choice = st.sidebar.radio("Navigate", ["Dashboard", "Add Task", "Logout"])

    st.sidebar.write(f"👤 Logged in as: **{st.session_state.user_id}**")

    if choice == "Dashboard":
        st.title("📋 Your Task Dashboard")

        tasks = get_tasks(st.session_state.user_id)

        if tasks:
            for task_id, task_name, status in tasks:
                cols = st.columns([4,1,1])
                cols[0].write(f"**{task_name}**")

                if status == "Pending":
                    cols[0].markdown(f"<span style='color:red;'>⏳ {status}</span>", unsafe_allow_html=True)
                else:
                    cols[0].markdown(f"<span style='color:green;'>✅ {status}</span>", unsafe_allow_html=True)

                if cols[1].button("✔ Done", key=f"done{task_id}"):
                    mark_done(task_id)
                    st.rerun()

                if cols[2].button("🗑 Delete", key=f"delete{task_id}"):
                    delete_task(task_id)
                    st.rerun()
        else:
            st.info("No tasks yet! Add some from the **Add Task** section.")

    elif choice == "Add Task":
        st.title("➕ Add New Task")
        task = st.text_input("Task Name")
        if st.button("Add"):
            if task.strip() != "":
                add_task(st.session_state.user_id, task)
                st.success("✅ Task Added")
            else:
                st.warning("Please enter something!")

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.rerun()
