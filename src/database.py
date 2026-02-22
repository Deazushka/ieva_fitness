import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple

DATABASE = "fitness_bot.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            exercise_name TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL,
            FOREIGN KEY (workout_id) REFERENCES workouts(id)
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_category(name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row["id"]
    cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return category_id


def get_categories() -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories ORDER BY id")
    categories = [row["name"] for row in cursor.fetchall()]
    conn.close()
    return categories


def delete_category(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exercises WHERE category_id = (SELECT id FROM categories WHERE name = ?)", (name,))
    cursor.execute("DELETE FROM categories WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def get_exercises_for_category(category_name: str) -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.name FROM exercises e
        JOIN categories c ON e.category_id = c.id
        WHERE c.name = ?
    """, (category_name,))
    exercises = [row["name"] for row in cursor.fetchall()]
    conn.close()
    return exercises


def get_or_create_exercise(name: str, category_name: str) -> int:
    category_id = get_or_create_category(category_name)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM exercises WHERE name = ? AND category_id = ?", (name, category_id))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row["id"]
    cursor.execute("INSERT INTO exercises (name, category_id) VALUES (?, ?)", (name, category_id))
    conn.commit()
    exercise_id = cursor.lastrowid
    conn.close()
    return exercise_id


def delete_exercise(name: str, category_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM exercises 
        WHERE name = ? AND category_id = (SELECT id FROM categories WHERE name = ?)
    """, (name, category_name))
    conn.commit()
    conn.close()


def create_workout(user_id: int, category_name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO workouts (user_id, category_name, started_at, is_active)
        VALUES (?, ?, ?, 1)
    """, (user_id, category_name, now))
    conn.commit()
    workout_id = cursor.lastrowid
    conn.close()
    return workout_id


def get_active_workout(user_id: int) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM workouts 
        WHERE user_id = ? AND is_active = 1
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def add_workout_exercise(workout_id: int, exercise_name: str, sets: int, reps: int, weight: Optional[float] = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO workout_exercises (workout_id, exercise_name, sets, reps, weight)
        VALUES (?, ?, ?, ?, ?)
    """, (workout_id, exercise_name, sets, reps, weight))
    conn.commit()
    conn.close()


def get_workout_exercises(workout_id: int) -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workout_exercises WHERE workout_id = ?", (workout_id,))
    exercises = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return exercises


def finish_workout(workout_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE workouts SET finished_at = ?, is_active = 0 WHERE id = ?
    """, (now, workout_id))
    conn.commit()
    conn.close()


def cancel_workout(workout_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workout_exercises WHERE workout_id = ?", (workout_id,))
    cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
    conn.commit()
    conn.close()


def get_user_workouts(user_id: int, limit: int = 10) -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM workouts 
        WHERE user_id = ? AND is_active = 0
        ORDER BY id DESC LIMIT ?
    """, (user_id, limit))
    workouts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return workouts


def get_workout_by_id(workout_id: int) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
