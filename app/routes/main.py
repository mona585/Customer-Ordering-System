from flask import Blueprint, render_template
from app.models.menu_item import MenuItem, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    items = MenuItem.query.all()
    
    categories = {}
    for item in items:
        cat_name = item.category.value  
        if cat_name not in categories:
            categories[cat_name] = []
        categories[cat_name].append(item)
    
    return render_template('products/home.html', categories=categories)