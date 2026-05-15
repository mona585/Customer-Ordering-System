# Customer Ordering System

A full-stack **order management platform** for restaurants and food services, built with Flask. Customers browse the menu, manage a cart, place orders, and track delivery in real time. Admins manage products and order statuses through a dedicated dashboard. The app is branded **AURA** in the UI and codebase.

---

## Table of Contents

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Demo Mode](#demo-mode)
- [Folder Structure](#folder-structure)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Key Features

### Authentication & authorization

| Feature | Description |
|--------|-------------|
| **Register / Login** | Customer registration with Firebase (email verification required). Staff accounts use local password authentication. |
| **Role-based access (RBAC)** | Roles: `customer`, `admin`, `delivery`, `chef`. Routes protected via `@role_required()`. |
| **Post-login routing** | Admins → `/admin/`, delivery → `/delivery/`, customers → `/customer/menu`. |

### Customer experience

| Feature | Description |
|--------|-------------|
| **Menu browsing** | Browse by category (Appetizers, Main Course, Desserts, Beverages, Sides) or view all items. |
| **Search** | Full-text style search across menu items (`/customer/search?q=...`). |
| **Product details** | Individual product pages with related items, reviews, and wishlist toggle. |
| **Shopping cart** | Session-based cart: add, update quantity, remove, special requests per item. |
| **Promo codes** | `SAVE10` (10% off), `AURA20` (20% off) applied at checkout. |
| **Wishlist** | Save favorite menu items; toggle via UI or AJAX. |
| **Checkout** | Delivery address, special instructions, payment method selection. |
| **Order placement** | Creates `Order`, `OrderItem`, `Payment`, and initial `OrderStatusHistory` in one transaction. |
| **Order history** | View and cancel orders (cancel allowed while `PENDING` or `CONFIRMED`). |
| **Reviews** | Rate products 1–5 stars with optional comments. |

### Order tracking (4 stages)

Visual timeline with live timers:

1. **Confirmation** — order received (`PENDING` / `CONFIRMED`)
2. **Preparation** — kitchen preparing (`PREPARING`)
3. **Shipping** — ready for delivery (`READY`)
4. **Delivery** — completed (`DELIVERED`)

Additional tracking capabilities:

- **Status history** — every status change stored in `order_status_history` with timestamps.
- **Live stage timers** — elapsed time updates every second for active stages and the blue “gap” period.
- **Blue gap animation** — animated connector between Confirmation and Preparation while status is `CONFIRMED` (waiting for preparation).
- **Demo mode** — `?demo=1` auto-advances stages every 10 seconds (see [Demo Mode](#demo-mode)).
- **Responsive UI** — mobile and desktop layouts via Tailwind CSS and custom CSS.

### Admin panel

| Feature | Description |
|--------|-------------|
| **Dashboard** | Order and revenue statistics. |
| **Order management** | List, filter by status, view details, update status. |
| **Product management** | List menu items, edit details, toggle availability (CRUD-style via admin UI). |

### Profile

| Feature | Description |
|--------|-------------|
| **View / edit profile** | Username, email, phone, address, password. |
| **Loyalty points** | Calculated from order totals and reviews. |
| **Payment cards** | Add-card UI (placeholder validation). |
| **Dietary preferences** | JSON API for preferences and allergies. |

### Staff roles (partial)

- **Delivery** — placeholder dashboard at `/delivery/` (role-protected).
- **Chef** — role defined; kitchen dashboard planned (redirects to home for now).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | [Flask](https://flask.palletsprojects.com/) 3.0, [SQLAlchemy](https://www.sqlalchemy.org/) 2.0, [Flask-Login](https://flask-login.readthedocs.io/), Flask-Migrate, Flask-WTF |
| **Database** | **SQLite** by default (`instance/app.db`). Production-ready via `DATABASE_URL` — supports **PostgreSQL** and **MySQL** (any SQLAlchemy-compatible URI). |
| **Auth** | Firebase Identity Toolkit (customers) + Werkzeug password hashing (staff) |
| **Frontend** | Jinja2 templates, [Tailwind CSS](https://tailwindcss.com/) (CDN on tracking page), vanilla JavaScript |
| **Styling / animations** | Custom CSS (`style.css`, `admin.css`) — `pulse-blue`, `shimmer`, `slide-dot` keyframes on order tracking |
| **Architecture** | Layered: **Routes → Services → Repositories → Models** |

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐     ┌────────────┐
│   Routes    │ ──► │  Services   │ ──► │  Repositories    │ ──► │   Models   │
│  (thin)     │     │ (business)  │     │  (data access)   │     │ (SQLAlchemy)│
└─────────────┘     └─────────────┘     └──────────────────┘     └────────────┘
```

Blueprints are registered in `app/__init__.py` via the application factory (`create_app`).

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- pip
- (Optional) Firebase project for customer registration/login

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Customer-Ordering-System.git
cd Customer-Ordering-System
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root (see [Environment Variables](#environment-variables)).

For Firebase setup details, see [SETUP.md](SETUP.md).

### 5. Initialize the database

Tables are created automatically on first run via `db.create_all()` in the app factory. To seed sample data:

```bash
python seed.py
```

Optional dev staff accounts (admin + delivery):

```bash
# Windows PowerShell
$env:SEED_DEV_STAFF="1"; python seed.py

# macOS / Linux
SEED_DEV_STAFF=1 python seed.py
```

### 6. Run the application

**Development:**

```bash
python run.py
```

Or:

```bash
flask --app run.py run --debug
```

Open [http://localhost:5000](http://localhost:5000).

**Production (WSGI):**

```bash
gunicorn wsgi:app
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Recommended | Flask session secret |
| `DATABASE_URL` | No | Override SQLite default (e.g. `postgresql://user:pass@host/db`) |
| `FIREBASE_WEB_API_KEY` | For customers | Firebase Web API key |
| `FIREBASE_CREDENTIALS` | For Firebase Admin | Path to service account JSON (default: `firebase-service-account.json`) |
| `WTF_CSRF_SECRET_KEY` | No | CSRF token secret |
| `SEED_DEV_STAFF` | No | Set to `1` to create dev admin/delivery users when running `seed.py` |

Default SQLite path: `instance/app.db` (created automatically).

---

## Database Schema

### Entity relationship overview

```mermaid
erDiagram
    User ||--o{ Order : places
    User }o--o{ Role : has
    User ||--o{ Review : writes
    User ||--o{ Wishlist : saves
    Order ||--|{ OrderItem : contains
    Order ||--o| Payment : has
    Order ||--o{ OrderStatusHistory : tracks
    MenuItem ||--o{ OrderItem : referenced_by
    MenuItem ||--o{ Review : receives
    MenuItem ||--o{ Wishlist : favorited_in
```

### Main tables

| Table | Purpose |
|-------|---------|
| `users` | Accounts (Firebase UID for customers, password hash for staff) |
| `roles` | Role definitions (`customer`, `admin`, `delivery`, `chef`) |
| `user_roles` | Many-to-many user ↔ role |
| `menu_items` | Products (name, price, category, stock, images, etc.) |
| `orders` | Orders (customer, total, status, delivery info) |
| `order_items` | Line items (quantity, unit price, special requests) |
| `payments` | Payment record per order (method, status, transaction ID) |
| `order_status_history` | Timestamped status changes |
| `reviews` | Product ratings and comments |
| `wishlists` | Customer saved items |

### Order status enum

| Status | Customer-facing stage |
|--------|------------------------|
| `PENDING` | Confirmation (placed, awaiting confirm) |
| `CONFIRMED` | Confirmation (blue gap — waiting for preparation) |
| `PREPARING` | Preparation |
| `READY` | Shipping |
| `DELIVERED` | Delivery |
| `CANCELLED` | Order cancelled |

---

## API Endpoints

All JSON APIs require login unless noted. Base URL: `http://localhost:5000`.

### Order (demo & tracking)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/order/order/<id>/track` | Order tracking page (`?demo=1` enables demo) |
| `POST` | `/api/order/<id>/advance` | Advance demo stage (JSON response) |
| `POST` | `/order/order/<id>/demo-advance` | Legacy form POST → redirect with `demo=1` |
| `GET` | `/order/my-orders` | Customer order history page |

**`POST /api/order/<id>/advance` — example response**

```json
{
  "success": true,
  "status": "PREPARING",
  "done": false
}
```

### Cart & wishlist

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/customer/api/cart/add` | Add item to cart (JSON or form) |
| `GET` | `/customer/api/cart/count` | Cart item count (0 if logged out) |
| `GET` | `/customer/api/product/<item_id>` | Product JSON for quick-view modal |
| `POST` | `/customer/api/wishlist/toggle/<item_id>` | Add/remove wishlist item |

### Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/update` | Update profile (JSON) |
| `POST` | `/profile/update-preferences` | Dietary preferences (JSON) |

### Auth (JSON on POST)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/auth/register` | Register customer |
| `GET/POST` | `/auth/login` | Login |
| `GET` | `/auth/logout` | Logout |

### Web routes (selected)

| Area | Prefix | Examples |
|------|--------|----------|
| Main | `/` | Home / menu landing |
| Customer | `/customer` | `/menu`, `/cart`, `/checkout`, `/orders`, `/product/<id>` |
| Admin | `/admin` | `/`, `/orders`, `/menu`, `/menu/<id>/edit` |
| Profile | `/` | `/profile`, `/profile/edit` |
| Delivery | `/delivery` | Staff dashboard (placeholder) |

---

## Demo Mode

Use demo mode to present the order tracking timeline without manual admin updates.

### How to enable

Append `?demo=1` to any order tracking URL:

```
http://localhost:5000/order/order/42/track?demo=1
```

Restart the demo from the beginning:

```
http://localhost:5000/order/order/42/track?demo=1&restart=1
```

### Behavior

| Setting | Value |
|---------|--------|
| **Auto-advance interval** | 10 seconds per stage |
| **Progression** | `CONFIRMED` → `PREPARING` → `READY` → `DELIVERED` |
| **On first visit** | Order resets to `CONFIRMED` (so the blue gap is visible) |
| **Blue gap** | Shown only while status is `CONFIRMED` (connector between Confirmation and Preparation) |
| **Manual advance** | “Force next stage” button in the demo panel |
| **API** | `POST /api/order/<id>/advance` called by JavaScript; page reloads after each step |

> **Note:** Demo mode mutates order status in the database. Use test orders, not production data.

### Default seed accounts (development)

| Account | Credentials | Role |
|---------|-------------|------|
| `test@aura.com` | `password123` | Customer (local DB; Firebase may be required for login) |
| `aura_admin` | `AdminPass!123` | Admin (`SEED_DEV_STAFF=1`) |
| `aura_delivery` | `DeliveryPass!123` | Delivery (`SEED_DEV_STAFF=1`) |

---

## Folder Structure

```
Customer-Ordering-System/
├── app/
│   ├── __init__.py              # Application factory (create_app)
│   ├── config.py                # App-level config (duplicate of root; factory uses root config)
│   ├── extensions.py            # db, login_manager, migrate, csrf
│   ├── bootstrap/
│   │   └── rbac.py              # Seed default roles on startup
│   ├── constants/
│   │   └── roles.py             # Role slug constants
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── menu_item.py
│   │   ├── orders.py
│   │   ├── order_item.py
│   │   ├── order_status_history.py
│   │   ├── payment.py
│   │   ├── review.py
│   │   └── wishlist.py
│   ├── repositories/            # Data access layer
│   ├── services/                # Business logic
│   ├── routes/                  # Blueprints (thin controllers)
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   ├── admin.py
│   │   ├── profile.py
│   │   └── delivery.py
│   ├── security/
│   │   └── rbac.py              # role_required, post-login redirect
│   ├── templates/               # Jinja2 HTML
│   │   ├── auth/
│   │   ├── products/
│   │   ├── cart/
│   │   ├── orders/
│   │   ├── admin/
│   │   └── profile/
│   ├── static/
│   │   ├── css/                 # style.css, admin.css
│   │   └── images/              # Menu item images
│   └── utils/
│       ├── seed_data.py
│       └── seed_data_new.py
├── config.py                    # Environment config (development/production/testing)
├── run.py                       # Dev server entry point
├── wsgi.py                      # Production WSGI entry point
├── seed.py                      # Database seeding script
├── requirements.txt
├── schema.sql                   # Legacy SQL reference schema
├── firebase_config.py           # Firebase Admin SDK init
├── SETUP.md                     # Firebase setup guide
├── instance/                    # SQLite DB (gitignored)
└── README.md
```

---

## Screenshots

> Add screenshots to `docs/screenshots/` and reference them here.

### Home / Menu

<!-- ![Menu](docs/screenshots/menu.png) -->
*Placeholder: menu browsing with categories*

### Shopping cart & checkout

<!-- ![Cart](docs/screenshots/cart.png) -->
*Placeholder: cart with promo code and checkout*

### Order tracking

<!-- ![Tracking](docs/screenshots/order-tracking.png) -->
*Placeholder: 4-stage timeline with live timers*

### Demo mode

<!-- ![Demo](docs/screenshots/demo-mode.png) -->
*Placeholder: demo panel with countdown and blue gap animation*

### Admin dashboard

<!-- ![Admin](docs/screenshots/admin-dashboard.png) -->
*Placeholder: admin orders and menu management*

---

## Future Improvements

- [ ] Full **chef/kitchen** dashboard for `PREPARING` → `READY` workflow
- [ ] Complete **delivery driver** UI (map, assign orders, mark delivered)
- [ ] **Email/SMS notifications** on status changes
- [ ] **Payment gateway** integration (Stripe/PayPal) instead of placeholder card form
- [ ] **Alembic migrations** committed to repo (currently `migrations/` is gitignored)
- [ ] **Promo codes** stored in database with expiry and usage limits
- [ ] **Order rating** after delivery (order-level, not only product reviews)
- [ ] **REST API** versioning and OpenAPI/Swagger documentation
- [ ] **Docker Compose** for one-command local and production deploy
- [ ] **Automated tests** (pytest coverage for services and routes)
- [ ] **i18n** / multi-language support
- [ ] **Dark mode** toggle across all pages (partial on tracking page)

---

## License

This project is provided for educational and demonstration purposes. Add your license file (`LICENSE`) before public distribution.

---

## Related documentation

- [SETUP.md](SETUP.md) — Firebase authentication setup
- [schema.sql](schema.sql) — Reference SQL schema (legacy; ORM models are authoritative)
