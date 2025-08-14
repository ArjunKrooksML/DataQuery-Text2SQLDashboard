#!/usr/bin/env python3
"""
Client Database setup script for DataWise backend.
Creates client databases with sample business data.
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))


def create_database_if_not_exists(engine, db_name):
    """Check if a PostgreSQL database exists, and create if it doesn't."""
    with engine.connect() as conn:
        # Check if database exists
        exists_result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"), {"dbname": db_name}
        )
        exists = exists_result.scalar() is not None

        if not exists:
            # COMMIT any open transaction before CREATE DATABASE (Postgres limitation)
            conn.execute(text("COMMIT"))
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database '{db_name}' created.")
        else:
            print(f"Database '{db_name}' already exists.")


def setup_client1_database():
    """Setup Client 1 Database (E-commerce)"""

    # Connect to PostgreSQL to manage client databases (connected to 'postgres' default db)
    platform_engine = create_engine("postgresql://postgres:root@postgres:5432/postgres")

    # Create client1_database if not exists
    create_database_if_not_exists(platform_engine, "client1_database")

    # Connect to client1_database
    client1_engine = create_engine("postgresql://postgres:root@postgres:5432/client1_database")

    with client1_engine.connect() as conn:
        # Create sales_data table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales_data (
                id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                region VARCHAR(50) NOT NULL,
                sales_amount DECIMAL(10,2) NOT NULL,
                sales_date DATE NOT NULL,
                customer_id INTEGER
            )
        """))

        # Create orders table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                order_date DATE NOT NULL,
                customer_name VARCHAR(100) NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending'
            )
        """))

        # Create customers table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                region VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Insert sample data
        insert_client1_sample_data(conn)

        conn.commit()

    print("✅ Client 1 Database (E-commerce) setup completed!")


def setup_client2_database():
    """Setup Client 2 Database (Manufacturing)"""

    # Connect to PostgreSQL to manage client databases (connected to 'postgres' default db)
    platform_engine = create_engine("postgresql://postgres:root@postgres:5432/postgres")

    # Create client2_database if not exists
    create_database_if_not_exists(platform_engine, "client2_database")

    # Connect to client2_database
    client2_engine = create_engine("postgresql://postgres:root@postgres:5432/client2_database")

    with client2_engine.connect() as conn:
        # Create inventory table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL,
                warehouse VARCHAR(50) NOT NULL,
                last_updated DATE NOT NULL,
                supplier_id INTEGER
            )
        """))

        # Create products table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create suppliers table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                contact_email VARCHAR(100) NOT NULL,
                region VARCHAR(50) NOT NULL,
                rating INTEGER DEFAULT 5
            )
        """))

        # Insert sample data
        insert_client2_sample_data(conn)

        conn.commit()

    print("✅ Client 2 Database (Manufacturing) setup completed!")


def insert_client1_sample_data(conn):
    """Insert sample data for Client 1 (E-commerce)"""

    # Sales data
    sales_data = [
        (1, 'Widget A', 'North', 1500.00, '2024-01-15', 101),
        (2, 'Widget B', 'South', 2200.00, '2024-01-16', 102),
        (3, 'Gadget C', 'North', 900.00, '2024-01-17', 103),
        (4, 'Widget A', 'East', 1800.00, '2024-01-18', 104),
        (5, 'Gadget C', 'West', 1200.00, '2024-01-19', 105),
        (6, 'Widget B', 'North', 2500.00, '2024-01-20', 106),
        (7, 'Widget A', 'South', 1600.00, '2024-01-21', 107),
        (8, 'Gadget C', 'East', 1100.00, '2024-01-22', 108),
        (9, 'Widget B', 'West', 1900.00, '2024-01-23', 109),
        (10, 'Widget A', 'North', 2100.00, '2024-01-24', 110)
    ]

    for data in sales_data:
        conn.execute(text("""
            INSERT INTO sales_data (id, product_name, region, sales_amount, sales_date, customer_id)
            VALUES (:id, :product_name, :region, :sales_amount, :sales_date, :customer_id)
        """), {
            'id': data[0],
            'product_name': data[1],
            'region': data[2],
            'sales_amount': data[3],
            'sales_date': data[4],
            'customer_id': data[5]
        })

    # Orders data
    orders_data = [
        (1, '2024-01-15', 'John Doe', 1500.00, 'completed'),
        (2, '2024-01-16', 'Jane Smith', 2200.00, 'pending'),
        (3, '2024-01-17', 'Bob Johnson', 900.00, 'completed'),
        (4, '2024-01-18', 'Alice Brown', 1800.00, 'shipped'),
        (5, '2024-01-19', 'Charlie Wilson', 1200.00, 'pending')
    ]

    for data in orders_data:
        conn.execute(text("""
            INSERT INTO orders (id, order_date, customer_name, total_amount, status)
            VALUES (:id, :order_date, :customer_name, :total_amount, :status)
        """), {
            'id': data[0],
            'order_date': data[1],
            'customer_name': data[2],
            'total_amount': data[3],
            'status': data[4]
        })

    # Customers data
    customers_data = [
        (101, 'John Doe', 'john@example.com', 'North'),
        (102, 'Jane Smith', 'jane@example.com', 'South'),
        (103, 'Bob Johnson', 'bob@example.com', 'North'),
        (104, 'Alice Brown', 'alice@example.com', 'East'),
        (105, 'Charlie Wilson', 'charlie@example.com', 'West')
    ]

    for data in customers_data:
        conn.execute(text("""
            INSERT INTO customers (id, name, email, region)
            VALUES (:id, :name, :email, :region)
        """), {
            'id': data[0],
            'name': data[1],
            'email': data[2],
            'region': data[3]
        })

    print("✅ Sample data inserted for Client 1 (E-commerce)")


def insert_client2_sample_data(conn):
    """Insert sample data for Client 2 (Manufacturing)"""

    # Inventory data
    inventory_data = [
        (1, 'Product X', 100, 'Warehouse A', '2024-01-15', 201),
        (2, 'Product Y', 250, 'Warehouse B', '2024-01-15', 202),
        (3, 'Product Z', 75, 'Warehouse A', '2024-01-15', 201),
        (4, 'Product X', 50, 'Warehouse C', '2024-01-16', 201),
        (5, 'Product Y', 180, 'Warehouse A', '2024-01-16', 202),
        (6, 'Product Z', 120, 'Warehouse B', '2024-01-17', 201),
        (7, 'Product X', 90, 'Warehouse B', '2024-01-17', 201),
        (8, 'Product Y', 300, 'Warehouse C', '2024-01-18', 202),
        (9, 'Product Z', 60, 'Warehouse A', '2024-01-18', 201),
        (10, 'Product X', 200, 'Warehouse C', '2024-01-19', 201)
    ]

    for data in inventory_data:
        conn.execute(text("""
            INSERT INTO inventory (id, product_name, quantity, warehouse, last_updated, supplier_id)
            VALUES (:id, :product_name, :quantity, :warehouse, :last_updated, :supplier_id)
        """), {
            'id': data[0],
            'product_name': data[1],
            'quantity': data[2],
            'warehouse': data[3],
            'last_updated': data[4],
            'supplier_id': data[5]
        })

    # Products data
    products_data = [
        (1, 'Product X', 'Electronics', 299.99),
        (2, 'Product Y', 'Machinery', 1499.99),
        (3, 'Product Z', 'Tools', 89.99),
        (4, 'Product A', 'Electronics', 199.99),
        (5, 'Product B', 'Machinery', 899.99)
    ]

    for data in products_data:
        conn.execute(text("""
            INSERT INTO products (id, name, category, price)
            VALUES (:id, :name, :category, :price)
        """), {
            'id': data[0],
            'name': data[1],
            'category': data[2],
            'price': data[3]
        })

    # Suppliers data
    suppliers_data = [
        (201, 'Tech Supplies Inc', 'contact@techsupplies.com', 'North', 5),
        (202, 'Industrial Parts Co', 'sales@industrialparts.com', 'South', 4),
        (203, 'Quality Tools Ltd', 'info@qualitytools.com', 'East', 5),
        (204, 'Machinery Pro', 'orders@machinerypro.com', 'West', 4),
        (205, 'Electronics Plus', 'support@electronicsplus.com', 'North', 5)
    ]

    for data in suppliers_data:
        conn.execute(text("""
            INSERT INTO suppliers (id, name, contact_email, region, rating)
            VALUES (:id, :name, :contact_email, :region, :rating)
        """), {
            'id': data[0],
            'name': data[1],
            'contact_email': data[2],
            'region': data[3],
            'rating': data[4]
        })

    print("✅ Sample data inserted for Client 2 (Manufacturing)")


def verify_client_databases():
    """Verify client databases were created successfully"""

    print("\n🔍 Verifying Client Databases:")
    print("=" * 50)

    # Check Client 1 Database
    try:
        client1_engine = create_engine("postgresql://postgres:root@postgres:5432/client1_database")
        with client1_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM sales_data"))
            sales_count = result.fetchone()[0]
            result = conn.execute(text("SELECT COUNT(*) FROM orders"))
            orders_count = result.fetchone()[0]
            result = conn.execute(text("SELECT COUNT(*) FROM customers"))
            customers_count = result.fetchone()[0]

            print(f"✅ Client 1 Database (E-commerce):")
            print(f"   - sales_data: {sales_count} records")
            print(f"   - orders: {orders_count} records")
            print(f"   - customers: {customers_count} records")
    except Exception as e:
        print(f"❌ Client 1 Database error: {e}")

    # Check Client 2 Database
    try:
        client2_engine = create_engine("postgresql://postgres:root@postgres:5432/client2_database")
        with client2_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM inventory"))
            inventory_count = result.fetchone()[0]
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            products_count = result.fetchone()[0]
            result = conn.execute(text("SELECT COUNT(*) FROM suppliers"))
            suppliers_count = result.fetchone()[0]

            print(f"✅ Client 2 Database (Manufacturing):")
            print(f"   - inventory: {inventory_count} records")
            print(f"   - products: {products_count} records")
            print(f"   - suppliers: {suppliers_count} records")
    except Exception as e:
        print(f"❌ Client 2 Database error: {e}")


if __name__ == "__main__":
    print("🚀 Setting up Client Databases...")
    print("=" * 50)

    # Setup Client 1 Database (E-commerce)
    setup_client1_database()

    # Setup Client 2 Database (Manufacturing)
    setup_client2_database()

    # Verify setup
    verify_client_databases()

    print("\n" + "=" * 50)
    print("✅ Client Databases setup completed!")
    print("\n📊 Database Architecture:")
    print("   Platform DB (datawiser_platform): User management & configurations")
    print("   Client 1 DB (client1_database): E-commerce business data")
    print("   Client 2 DB (client2_database): Manufacturing business data")
