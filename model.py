from connect_db import sql_connection

class Model:
    def __init__(self):
        self.conn = sql_connection()
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                username VARCHAR(255) UNIQUE NOT NULL,
                                email VARCHAR(255) UNIQUE NOT NULL,
                                password VARCHAR(255) NOT NULL)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                name VARCHAR(255) NOT NULL,
                                price DECIMAL(10,2) NOT NULL,
                                quantity INT NOT NULL,
                                user_id INT,
                                FOREIGN KEY (user_id) REFERENCES users(id))''')
        self.conn.commit()

    def register_user(self, username, email, password):
        try:
            self.cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                                (username, email, password))
            self.conn.commit()
            return True
        except:
            return False

    def authenticate_user(self, username, password):
        self.cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", 
                            (username, password))
        user = self.cursor.fetchone()
        return user[0] if user else None

    def add_product(self, user_id, name, price, quantity):
        """UPDATED: Check if product exists, UPDATE quantity or INSERT new"""
        try:
            # Check if product already exists for this user
            self.cursor.execute("SELECT id, quantity FROM products WHERE name = %s AND user_id = %s", 
                               (name, user_id))
            existing = self.cursor.fetchone()
            
            if existing:
                # Product exists → UPDATE quantity
                product_id, current_qty = existing
                new_qty = current_qty + int(quantity)
                self.cursor.execute("UPDATE products SET quantity = %s WHERE id = %s AND user_id = %s", 
                                   (new_qty, product_id, user_id))
            else:
                # Product doesn't exist → INSERT new row
                self.cursor.execute("INSERT INTO products (name, price, quantity, user_id) VALUES (%s, %s, %s, %s)", 
                                   (name, float(price), int(quantity), user_id))
            
            self.conn.commit()
        except Exception as e:
            print("Error:", e)

    def remove_product(self, user_id, product_id):
        self.cursor.execute("DELETE FROM products WHERE id = %s AND user_id = %s", (product_id, user_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_product_quantity(self, user_id, product_id, new_quantity):
        self.cursor.execute("UPDATE products SET quantity = %s WHERE id = %s AND user_id = %s", 
                            (new_quantity, product_id, user_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_products(self, user_id):
        self.cursor.execute("SELECT id, name, price, quantity FROM products WHERE user_id = %s", (user_id,))
        return self.cursor.fetchall()

    def check_stock(self, user_id):
        self.cursor.execute("SELECT id, name, price, quantity FROM products WHERE user_id = %s AND quantity < 5", (user_id,))
        return self.cursor.fetchall()

    def search_products(self, user_id, query):
        """Search products by name"""
        self.cursor.execute("""
            SELECT id, name, price, quantity 
            FROM products 
            WHERE user_id = %s AND LOWER(name) LIKE %s
        """, (user_id, f'%{query}%'))
        return self.cursor.fetchall()
