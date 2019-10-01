from flask import Flask, render_template, redirect, url_for, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import reduce
import os

app = Flask(__name__)

app.config["MONGO_URI"] = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/fruit_baskets')
mongo = PyMongo(app)

fruit_baskets = mongo.db.baskets

# Make a list of all available fruits - this could be stored in the database,
# but it's hardcoded for now
all_fruits = [
    {
        'name': 'banana',
        'cost': 1.00,
        'img_url': '/static/img/banana.png',
    },
    {
        'name': 'apple',
        'cost': 2.00,
        'img_url': '/static/img/apple.png',
    },
    {
        'name': 'watermelon',
        'cost': 3.00,
        'img_url': '/static/img/watermelon.png',
    },
    {
        'name': 'avocado',
        'cost': 2.00,
        'img_url': '/static/img/avocado.png',
    },
    {
        'name': 'pear',
        'cost': 4.00,
        'img_url': '/static/img/pear.png'
    }
]

@app.route('/')
def index():
    """Return homepage."""
    return render_template('index.html', baskets=fruit_baskets.find())

@app.route('/new')
def new_basket():
    """Return new basket creation page."""
    return render_template('new_basket.html')

@app.route('/create', methods=['POST'])
def create_basket():
    """Make a new basket according to user's specifications."""
    basket = {
        'name': request.form.get('name'),
        'recipient': request.form.get('recipient'),
        'fruits': [],
        'fruits_count': 0
    }
    # Add each fruit in basket - quantity starts at 0
    for fruit in all_fruits:
        updated_fruit = {
            'name': fruit['name'],
            'cost': fruit['cost'],
            'img_url': fruit['img_url'],
            'quantity': 0,
        }
        basket['fruits'].append(updated_fruit)

    basket_id = fruit_baskets.insert_one(basket).inserted_id
    return redirect(url_for('show_basket', basket_id=basket_id))

@app.route('/basket/<basket_id>')
def show_basket(basket_id):
    """Show a single fruit basket."""
    basket = fruit_baskets.find_one({'_id': ObjectId(basket_id)})
    return render_template('show_basket.html', basket=basket)

@app.route('/basket', methods=['POST'])
def submit_basket():
    """Make changes to a specific basket by editing its 'fruits' field."""
    basket_id = request.form.get('basket_id')
    basket = fruit_baskets.find_one({'_id': ObjectId(basket_id)})
    fruits_count = 0

    # Update the quantity of each fruit in basket, according to user-entered
    # form fields
    for fruit in basket['fruits']:
        quantity = int(request.form.get(fruit['name']))
        fruit['quantity'] = quantity
        fruits_count += quantity

    # Update the count to be the sum of all fruits
    basket['fruits_count'] = fruits_count

    # Update the database entry
    fruit_baskets.update_one(
        {'_id': ObjectId(basket_id)},
        {'$set': basket}
    )
    return redirect(url_for('show_basket', basket_id=basket_id))

@app.route('/delete', methods=['POST'])
def delete_basket():
    """Delete a fruit basket."""
    basket_id = request.form.get('basket_id')
    fruit_baskets.delete_one({'_id': ObjectId(basket_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
