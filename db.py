import sqlite3
import datetime


def new_user(tg_name, tg_id):
    db = sqlite3.connect("reminder.db")
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS users (
        tg_name TEXT,
        tg_id INTEGER,
        )""")
    db.commit()



    check = sql.execute(
        "SELECT * FROM users WHERE tg_id = ?", (tg_id, )).fetchone()
    if not check:
        sql.execute(f"INSERT INTO users VALUES(?, ?)", (tg_name, tg_id))
    db.commit()
    db.close()

new_user('Алексей', 123456789)
new_user("Людмила", 987654321)

def get_names():
    db = sqlite3.connect("reminder.db")
    sql = db.cursor()

    sql.execute("SELECT tg_name, tg_id FROM users")
    rows = sql.fetchall()

    names = [f"{row[0]}-{row[1]}" for row in rows]

    db.close()

    return names

    


def new_task(user_id, task_text, task_date, task_answer_time):
    db = sqlite3.connect("reminder.db")
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS users (
        tg_name TEXT,
        tg_id INTEGER
        )""")
    
    sql.execute("""CREATE TABLE IF NOT EXISTS tasks (
        user_id INTEGER,
        text TEXT,
        date DATE,
        answer_time TIME
        )""")
    db.commit()

    current_date = datetime.datetime.now().date()
    current_time = datetime.datetime.now().time()

    if task_date < current_date or (task_date == current_date and task_answer_time < current_time):

        return "Задача просрочена"

    check_user = sql.execute("SELECT * FROM users WHERE tg_id = ?", (user_id.split('-')[1],)).fetchone()
    if not check_user:
        name, id = user_id.split('-')
        new_user(name, id)

    user_id = check_user[1]

    sql.execute("INSERT INTO tasks VALUES (?, ?, ?, ?)", (user_id.split('-')[1], task_text, task_date, task_answer_time))
    db.commit()
    db.close()

    return "Задача добавлена в базу данных"
