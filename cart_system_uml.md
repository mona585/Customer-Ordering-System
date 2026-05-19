# Cart System UML Diagram

This diagram visualizes the architecture and data flow of the Cart System.

## Architecture Diagram (Class Diagram)

```mermaid
classDiagram
    class CustomerRoutes {
        <<Blueprint>>
        +cart()
        +add_to_cart()
        +update_cart(item_id)
        +remove_from_cart(item_id)
        +api_add_to_cart()
        +api_cart_count()
    }

    class CartService {
        <<Service>>
        +get_cart_items(cart_data) ServiceResult
        +apply_promo_code(cart_total, promo_code) ServiceResult
        +add_to_cart(cart_data, item_id, quantity, special_requests) ServiceResult
        +update_cart_item(cart_data, item_id, new_quantity) ServiceResult
        +remove_from_cart(cart_data, item_id) ServiceResult
        +get_cart_count(cart_data) ServiceResult
        +validate_cart_for_checkout(cart_data) ServiceResult
    }

    class CartRepository {
        <<Repository>>
        +get_cart(session) dict
        +save_cart(session, cart_data) void
        +clear_cart(session) void
        +get_item_quantity(cart_data, item_id) int
        +update_item(cart_data, item_id, quantity, special_requests) dict
        +remove_item(cart_data, item_id) dict
        +get_total_count(cart_data) int
    }

    class MenuRepository {
        <<Repository>>
        +get_by_id(item_id) MenuItem
    }

    class CheckoutService {
        <<Service>>
        +_validate_promo(code, cart_total) ServiceResult
    }

    class FlaskSession {
        <<Storage>>
        dict cart
        float promo_discount
        string applied_promo
        string promo_code
    }

    CustomerRoutes ..> CartService : "Calls for business logic"
    CustomerRoutes ..> FlaskSession : "Reads/Writes session state"
    CartService ..> CartRepository : "Delegates dictionary manipulation"
    CartService ..> MenuRepository : "Fetches items & validates stock"
    CartService ..> CheckoutService : "Validates promo codes"
    CartRepository ..> FlaskSession : "Saves data to session"
```

## Explanation of Layers

1. **`CustomerRoutes` (Presentation Layer)**: Endpoints defined in `app/routes/customer.py` intercept user actions (adding items, updating quantities, applying promos). They extract the `cart_data` from the `FlaskSession` and pass it to the `CartService`.
2. **`CartService` (Business Logic Layer)**: Contains the core cart logic inside `app/services/cart_service.py`. It handles stock validation against the `MenuRepository`, calculates totals, processes promo codes using `CheckoutService`, and delegates raw data manipulation to the repository.
3. **`CartRepository` (Data Access Layer)**: A thin abstraction in `app/repositories/cart_repository.py` to handle the pure manipulation of the cart dictionary structure without knowing about external concepts like pricing or stock.
4. **`FlaskSession` (Storage Layer)**: The cart items are currently stored persistently per-user in the Flask server-side session dictionary (`session['cart']`). It acts as transient key-value storage.
