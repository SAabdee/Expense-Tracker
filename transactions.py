from db import get_connection

def add_transaction(user_id, amount, t_type, category, description, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, type, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, amount, t_type, category, description, date))
    conn.commit()
    conn.close()

def delete_transaction(transaction_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s AND user_id = %s", (transaction_id, user_id))
    conn.commit()
    conn.close()

def get_user_transactions(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, amount, type, category, description, date
        FROM transactions
        WHERE user_id = %s
    """, (user_id,))
    real_txns = cursor.fetchall()

    cursor.execute("""
        SELECT NULL, lr.amount, 'expense', 'Lend Given',
               CONCAT('Lent to ', u.username), lr.date
        FROM lend_requests lr
        JOIN users u ON lr.to_user_id = u.id
        WHERE lr.from_user_id = %s AND lr.status = 'paid'
    """, (user_id,))
    lend_given = cursor.fetchall()

    cursor.execute("""
        SELECT NULL, lr.amount, 'income', 'Lend Received',
               CONCAT('Received from ', u.username), lr.date
        FROM lend_requests lr
        JOIN users u ON lr.from_user_id = u.id
        WHERE lr.to_user_id = %s AND lr.status = 'paid'
    """, (user_id,))
    lend_received = cursor.fetchall()

    all_txns = real_txns + lend_given + lend_received
    all_txns.sort(key=lambda x: x[5], reverse=True)
    conn.close()
    return all_txns
