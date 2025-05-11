from db import get_connection

def add_friend(user_id, friend_username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (friend_username,))
    result = cursor.fetchone()
    if result:
        friend_id = result[0]
        cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)", (user_id, friend_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_friends(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username
        FROM friends f
        JOIN users u ON f.friend_id = u.id
        WHERE f.user_id = %s
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]
