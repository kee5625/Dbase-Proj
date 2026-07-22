# E-Commerce Database System Requirements Document

## 1. System Overview
The purpose of this project is to develop a backend database for an e-commerce platform. The system will handle customer accounts, staff operations, product inventory, customer payment methods, and sales transactions.

## 2. User Roles
* **Customer:** An end user who creates an account, manages payment options, browses products, and places orders.
* **Staff:** An administrative user responsible for managing product inventory, updating product details, and monitoring purchase orders.

## 3. Data Requirements

### Customer - Stong Entity
* **Attributes:** Customer ID (Primary Key), First Name, Last Name, Email, Password Hash, Phone Number, Date Joined, Credit Card
* **Rules:** Email must be unique. A customer can store multiple credit cards.

### CreditCard - Composite Multivalued Attribute of Customer
* **Attributes:** Card ID (Primary Key), Customer ID (Foreign Key), Card Number, Expiration Date, Cardholder Name, Billing Address
* **Rules:** Each card must belong to exactly one customer. A customer may store zero, one, or multiple cards.

### Staff - Strong Entity
* **Attributes:** Staff ID (Primary Key), First Name, Last Name, Email, Job Title, Hire Date
* **Rules:** Email must be unique. Staff members manage products and oversee order records.

### Product - Strong Entity
* **Attributes:** Product ID (Primary Key), Product Name, Description, Price, Stock Quantity, Category
* **Rules:** Price must be greater than zero. Stock quantity updates when purchases are made.

### Purchase - Relationship between Customer and Product
* **Attributes:** Purchase ID (Primary Key), Customer ID (Foreign Key), Product ID (Foreign Key), Payment Method, Purchase Date, Total Amount, Status, PurchaseItem
* **Rules:** Every purchase must be associated with a valid customer and a stored payment method.

### PurchaseItem - Composite Multivalued Attribute of Purchase
* **Attributes:** Product ID (Foreign Key), Quantity, Unit Price
* **Rules:** Captures individual products included in a specific purchase transaction.

## 4. System Use Cases

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
* **Description:** Customers select products, choose a saved payment method, and complete a purchase. The system records the transaction and decrements product inventory.

### Use Case 5: Transaction Oversight
* **Actor:** Staff
* **Description:** Staff members view transaction history, order details, and sales totals across the system.

## 5. Technical Constraints
* **DBMS:** MySQL or PostgreSQL.
* **Data Integrity:** Primary keys must uniquely identify each record. Foreign keys must enforce referential integrity across related tables.
