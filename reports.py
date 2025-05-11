from db import get_connection

def get_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT type, SUM(amount)
        FROM transactions
        WHERE user_id = %s
          AND MONTH(date) = MONTH(CURDATE())
          AND YEAR(date) = YEAR(CURDATE())
        GROUP BY type
    """, (user_id,))
    real = cursor.fetchall()

    cursor.execute("""
        SELECT 'income', SUM(amount)
        FROM lend_requests
        WHERE to_user_id = %s
          AND status = 'paid'
          AND MONTH(date) = MONTH(CURDATE())
          AND YEAR(date) = YEAR(CURDATE())
    """, (user_id,))
    lend_income = cursor.fetchall()

    cursor.execute("""
        SELECT 'expense', SUM(amount)
        FROM lend_requests
        WHERE from_user_id = %s
          AND status = 'paid'
          AND MONTH(date) = MONTH(CURDATE())
          AND YEAR(date) = YEAR(CURDATE())
    """, (user_id,))
    lend_expense = cursor.fetchall()

    
    summary = {'income': 0.0, 'expense': 0.0}
    for t_type, total in real + lend_income + lend_expense:
        if total:
            summary[t_type] += float(total)

    summary['remaining'] = summary['income'] - summary['expense']
    conn.close()
    return summary
