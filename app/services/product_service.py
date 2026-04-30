from app.repositories.product import get_product_by_id
from app.repositories.review import get_reviews_by_product

def get_product_details(product_id):
    product = get_product_by_id(product_id)
    reviews = get_reviews_by_product(product_id)

    return {
        "product": product,
        "reviews": reviews
    }