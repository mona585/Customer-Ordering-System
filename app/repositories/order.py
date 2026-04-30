from db.connection import get_connection

def get_order_by_id(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    result = cursor.fetchone()

    conn.close()
    return result


def get_order_items(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM order_items WHERE order_id = ?
    """, (order_id,))

    result = cursor.fetchall()
    conn.close()
    return result


def get_order_status_history(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM order_status_history
        WHERE order_id = ?
        ORDER BY changed_at ASC
    """, (order_id,))

    result = cursor.fetchall()
    conn.close()
    return result