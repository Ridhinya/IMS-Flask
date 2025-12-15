from flask import Flask, render_template, request, redirect, url_for, flash, session
from model import Model
import os

app = Flask(__name__)
app.secret_key = 'your-super-secret-key-ims-2025'
app.config['UPLOAD_FOLDER'] = 'static'

# Initialize your existing Model
model = Model()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if model.register_user(username, email, password):
            flash('✅ Registration successful! Please login.', 'success')
            return redirect(url_for('index'))
        else:
            flash('❌ Registration failed! Username or email already exists.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user_id = model.authenticate_user(username, password)
    if user_id:
        session['user_id'] = user_id
        session['username'] = username
        flash('✅ Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('❌ Invalid credentials!', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    products = model.get_products(user_id)
    low_stock = model.check_stock(user_id)
    
    return render_template('dashboard.html', 
                         products=products, 
                         low_stock=low_stock,
                         username=session.get('username'))

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']
    
    try:
        model.add_product(user_id, name, float(price), int(quantity))
        flash('✅ Product added successfully!', 'success')
    except ValueError:
        flash('❌ Invalid price or quantity!', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    if model.remove_product(user_id, product_id):
        flash('✅ Product removed successfully!', 'success')
    else:
        flash('❌ Product not found!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/update_quantity/<int:product_id>', methods=['POST'])
def update_quantity(product_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    new_quantity = int(request.form['quantity'])
    
    if model.update_product_quantity(user_id, product_id, new_quantity):
        flash('✅ Quantity updated successfully!', 'success')
    else:
        flash('❌ Product not found!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('🔒 Logged out successfully!', 'info')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    query = request.args.get('q', '').lower().strip()
    
    if query:
        products = model.search_products(user_id, query)
    else:
        products = model.get_products(user_id)
    
    return render_template('dashboard.html',  # Reuse same template
                         products=products, 
                         low_stock=model.check_stock(user_id),
                         username=session.get('username'),
                         search_query=query)


if __name__ == '__main__':
    app.run()
