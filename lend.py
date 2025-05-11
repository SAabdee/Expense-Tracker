from db import get_connection

def request_lend(to_user_id, from_username, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (from_username,))
    result = cursor.fetchone()
    if result:
        from_user_id = result[0]
        cursor.execute("""
            INSERT INTO lend_requests (from_user_id, to_user_id, amount, date, status)
            VALUES (%s, %s, %s, CURDATE(), NULL)
        """, (from_user_id, to_user_id, amount))
        conn.commit()
    conn.close()

def get_lend_requests(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT lr.id, u.username, lr.amount, lr.status
        FROM lend_requests lr
        JOIN users u ON lr.to_user_id = u.id
        WHERE lr.from_user_id = %s
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def mark_as_paid(request_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE lend_requests SET status = 'paid' WHERE id = %s", (request_id,))
    conn.commit()
    conn.close()

def respond_to_lend_request(request_id, action):
    conn = get_connection()
    cursor = conn.cursor()
    if action == 'accept':
        cursor.execute("UPDATE lend_requests SET status = 'pending' WHERE id = %s", (request_id,))
    elif action == 'decline':
        cursor.execute("UPDATE lend_requests SET status = 'declined' WHERE id = %s", (request_id,))
    conn.commit()
    conn.close()

def get_friend_usernames(user_id):
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
