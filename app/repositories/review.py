from db.connection import get_connection

def get_reviews_by_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM reviews
        WHERE product_id = ?
        ORDER BY created_at DESC
    """, (product_id,))

    result = cursor.fetchall()
    conn.close()
    return result


def add_review(product_id, user_name, rating, comment):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reviews (product_id, user_name, rating, comment)
        VALUES (?, ?, ?, ?)
    """, (product_id, user_name, rating, comment))

    conn.commit()
    conn.close()