from db import get_connection

def signup(username, password, email):
    if not username or not password or not email:
        return False  # Prevent empty values

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False  # Username exists

        # Insert new user
        cursor.execute("""
            INSERT INTO users (username, password, email)
            VALUES (%s, %s, %s)
        """, (username, password, email))
        conn.commit()
        return True
    except Exception as e:
        print(f"Signup Error: {e}")
        return False
    finally:
        conn.close()

def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM users
        WHERE username = %s AND password = %s
    """, (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user[0]
    return None

def reset_password(email, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET password = %s
        WHERE email = %s
    """, (new_password, email))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0
