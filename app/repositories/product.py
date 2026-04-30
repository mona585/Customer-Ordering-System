from db.connection import get_connection

def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )

    result = cursor.fetchone()
    conn.close()
    return result


def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()

    conn.close()
    return result