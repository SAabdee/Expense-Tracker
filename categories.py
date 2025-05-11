from db import get_connection

def add_category(user_id, name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (user_id, name) VALUES (%s, %s)", (user_id, name))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories WHERE user_id = %s", (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]
