from flask import Blueprint, render_template, abort
from app.services.menu_service import MenuService 

product_bp = Blueprint("product", __name__)

@product_bp.route("/product/<int:product_id>")
def product_details(product_id):
    result = MenuService.get_product_details(product_id)
    
    if not result.success:
        abort(404)
    
    return render_template("products/product_details.html", 
                         item=result.data['item'], 
                         related=result.data['related'],
                         reviews=result.data['item'].reviews)
