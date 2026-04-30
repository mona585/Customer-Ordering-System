


from flask import Blueprint, render_template
from app.models.menu_item import MenuItem

product_bp = Blueprint("product", __name__)

@product_bp.route("/product/<int:product_id>")
def product_details(product_id):
    item = MenuItem.query.get_or_404(product_id)
    
    # Get related items (same category)
    related = MenuItem.query.filter_by(
        category=item.category,
        is_available=True
    ).filter(MenuItem.id != product_id).limit(4).all()
    
    return render_template("products/product_details.html", 
                         item=item, 
                         related=related,
                         reviews=item.reviews)

