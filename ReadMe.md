# eCommerce API - QA Testing Assignment

## Project Overview
This is a REST API for a simple eCommerce platform. The development team has just completed the initial implementation and needs comprehensive QA testing before deployment to production.

## Setup Instructions

### Using Docker

**Build the Docker image:**
```bash
docker build -t ecommerce-api .
```

**Run with non-persistent database (resets on restart):**
```bash
docker run -p 5000:5000 ecommerce-api
```

**Run with persistent database:**
```bash
docker run -p 5000:5000 -v $(pwd)/data:/app/data ecommerce-api
```

The API will be available at `http://localhost:5000`

## Testing Assignment

### Your Task
You are responsible for testing the eCommerce API endpoints listed below. Your objectives are to:

1. **Understand the Requirements** - Review each endpoint and determine what it should do
2. **Write Acceptance Criteria** - Define clear acceptance criteria for each feature
3. **Identify Issues** - Find and document any bugs, security vulnerabilities, or unexpected behavior
4. **Report Findings** - Create detailed bug reports with reproduction steps

### Test Coverage Areas

When testing, consider:
- **Functionality** - Does the endpoint work as expected?
- **Validation** - Are inputs properly validated?
- **Security** - Are there any security vulnerabilities?
- **Error Handling** - How does the API handle invalid inputs?
- **Data Integrity** - Is data stored and retrieved correctly?
- **Business Logic** - Do the workflows make sense for an eCommerce platform?

---

## API Endpoints to Test

### 1. User Management

#### Create User
**POST** `/api/users`

**Purpose:** Register a new user in the system

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123"
}
```

---

#### Get Users
**GET** `/api/users`

**Purpose:** Retrieve user information

**Query Parameters:**
- `id` (optional) - Filter by specific user ID

---

### 2. Product Management

#### Get Products
**GET** `/api/products`

**Purpose:** Retrieve available products

**Query Parameters:**
- `search` (optional) - Search products by name

---

### 3. Shopping Cart

#### Create/Update Cart
**POST** `/api/cart`

**Purpose:** Create a new cart or update an existing cart for a user

**Request Body:**
```json
{
  "user_id": 1,
  "product_ids": [1, 2, 3]
}
```

---

#### Remove from Cart
**POST** `/api/cart/{cart_id}/remove`

**Purpose:** Remove a product from a cart

**Request Body:**
```json
{
  "product_id": 2
}
```

---

### 4. Checkout Process

#### Checkout
**POST** `/api/checkout`

**Purpose:** Process a cart and create an order

**Request Body:**
```json
{
  "user_id": 1,
  "cart_id": 1
}
```

---

#### Get Orders
**GET** `/api/orders`

**Purpose:** Retrieve order history

**Query Parameters:**
- `user_id` (optional) - Filter by user ID

---

## Testing Workflows

### End-to-End Scenarios

Test these complete user journeys:

1. **New User Purchase Flow**
   - Create a new user
   - Browse products
   - Add items to cart
   - Remove an item
   - Complete checkout
   - Verify order was created

2. **Multiple Users**
   - Create two different users
   - Create carts for both
   - Verify data isolation

---

## Deliverables

### 1. Test Plan Document
- List of test cases for each endpoint
- Acceptance criteria you've defined
- Test data used

### 2. Bug Reports
For each bug found, include:
- **Bug ID** (e.g., BUG-001)
- **Severity** (Critical/High/Medium/Low)
- **Title** (Short, descriptive summary)
- **Description** (What is the issue?)
- **Steps to Reproduce** (Exact steps)
- **Expected Result** (What should happen)
- **Actual Result** (What actually happens)
- **Evidence** (Screenshots, API responses)
- **Impact** (Why does this matter?)

### Severity Guidelines
- **Critical**: Security vulnerabilities, data loss, system crashes
- **High**: Major functionality broken, no workaround
- **Medium**: Functionality impaired, workaround exists
- **Low**: Minor issues, cosmetic problems

---

## Resources

### Sample Products
The API comes pre-loaded with these products:
- Laptop ($999.99, stock: 10)
- Mouse ($29.99, stock: 50)
- Keyboard ($79.99, stock: 30)
- Monitor ($299.99, stock: 15)
- Headphones ($149.99, stock: 25)

### Postman Collection
Import the provided `ecommerce_api_postman_collection.json` file into Postman for quick testing setup.
