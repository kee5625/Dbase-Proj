# E-Commerce Database System Requirements Document

## 1. System Overview
The purpose of this project is to develop a backend database for an e-commerce platform. The system will handle customer accounts, staff operations, product inventory, customer payment methods, and sales transactions.

## 2. User Roles
* **Customer:** An end user who creates an account, manages payment options, browses products, and places orders.
* **Staff:** An administrative user responsible for managing product inventory, updating product details, and monitoring purchase orders.

## 3. Data Requirements

### Customer - Strong Entity
* **Attributes:** Customer ID (Primary Key), First Name, Last Name, Email, Password Hash, Phone Number, Date Joined
* **Rules:** Email must be unique. A customer may store zero, one, or multiple credit cards (see CreditCard).

### CreditCard - Weak Entity (dependent on Customer)
* **Attributes:** Card ID (Partial Key), Customer ID (Foreign Key), Card Number, Expiration Date, Cardholder Name, Billing Address
* **Rules:** Each card must belong to exactly one customer and cannot exist without one (identifying relationship `Stores`). A customer may store zero, one, or multiple cards. Participation: Customer side is partial (a customer may have no cards); CreditCard side is total (every card must belong to a customer).

### Staff - Strong Entity
* **Attributes:** Staff ID (Primary Key), First Name, Last Name, Email, Job Title, Hire Date
* **Rules:** Email must be unique. Staff members manage products and oversee order records.

### Product - Strong Entity
* **Attributes:** Product ID (Primary Key), Staff ID (Foreign Key), Product Name, Description, Price, Stock Quantity, Category
* **Rules:** Price must be greater than zero. Stock quantity updates when purchases are made. Each product is managed by a staff member (relationship `Manages`).

### Purchase - Strong Entity
* **Attributes:** Purchase ID (Primary Key), Customer ID (Foreign Key), Card ID (Foreign Key), Purchase Date, Total Amount, Status
* **Rules:** Every purchase must be associated with exactly one valid customer (relationship `Places`, total participation on the Purchase side) and exactly one stored payment card (Card ID references CreditCard, replacing the earlier free-text Payment Method field). A purchase must contain one or more purchase items (relationship `Contains`, total participation on the Purchase side).

### PurchaseItem - Weak Entity (dependent on Purchase and Product)
* **Attributes:** Purchase ID (Foreign Key, part of Primary Key), Product ID (Foreign Key, part of Primary Key), Quantity, Unit Price
* **Rules:** Composite primary key is (Purchase ID, Product ID). Captures individual products included in a specific purchase transaction. Cannot exist without both a parent Purchase (identifying relationship `Contains`) and a referenced Product (identifying relationship `Appears_in`). This entity resolves the many-to-many relationship between Purchase and Product: a purchase can contain many products, and a product can appear in many purchases. Participation: total on the PurchaseItem side for both relationships; partial on the Product side (a product may exist with zero purchases).

## 4. Relationships Summary
| Relationship | Entities | Cardinality | Participation |
|---|---|---|---|
| Places | Customer – Purchase | 1:M | Partial (Customer), Total (Purchase) |
| Stores | Customer – CreditCard | 1:M | Partial (Customer), Total (CreditCard) |
| Manages | Staff – Product | 1:M | Partial or Total (Staff, per business rule), Total (Product) |
| Contains | Purchase – PurchaseItem | 1:M | Total (Purchase), Total (PurchaseItem) |
| Appears_in | Product – PurchaseItem | 1:M | Partial (Product), Total (PurchaseItem) |

## 5. System Use Cases

### Use Case 1: Account & Payment Management
* **Actor:** Customer
* **Description:** Customers register an account and can attach one or more credit cards to their profile for future checkout operations.

### Use Case 2: Product Catalog Browsing
* **Actor:** Customer
* **Description:** Customers view available products, filter items by category, and search by product name or price.

### Use Case 3: Product Inventory Management
* **Actor:** Staff
* **Description:** Staff members add new items to the inventory, update existing product details (such as price and description), and modify stock levels.

### Use Case 4: Order Processing
* **Actor:** Customer
* **Description:** Customers select products, choose a saved payment method, and complete a purchase. The system records the transaction, itemizes each product in the purchase, and decrements product inventory.

### Use Case 5: Transaction Oversight
* **Actor:** Staff
* **Description:** Staff members view transaction history, order details, and sales totals across the system.

## 6. Technical Constraints
* **DBMS:** MySQL or PostgreSQL.
* **Data Integrity:** Primary keys must uniquely identify each record. Foreign keys must enforce referential integrity across related tables. Weak entities (CreditCard, PurchaseItem) must cascade appropriately on deletion of their owning entity, per business rule.
