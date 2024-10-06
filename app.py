from flask import Flask, render_template, request, jsonify, session
import os
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)  

user_data_store = {}
coupon_discount = 100

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = os.urandom(8).hex()

    user_id = session['user_id']
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            'product_price': 1500,
            'user_balance': 500,
            'coupon_applied': False,
            'coupon_code': "",
            'coupon_error_message': ""
        }

    user_data = user_data_store[user_id]
    return render_template('index.html', product_price=user_data['product_price'],
                           user_balance=user_data['user_balance'], 
                           coupon_applied=user_data['coupon_applied'], 
                           coupon_code=user_data['coupon_code'], 
                           coupon_error_message=user_data['coupon_error_message'])

@app.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    user_id = session['user_id']
    user_data = user_data_store.get(user_id, {})

    coupon_code_input = request.form['coupon_code']

    if not user_data.get('coupon_applied') and coupon_code_input == "race":
        time.sleep(0.5)  

        discounted_price = user_data['product_price'] - coupon_discount
        user_data['product_price'] = max(0, discounted_price)

        user_data['coupon_applied'] = True
        user_data['coupon_code'] = coupon_code_input

        user_data_store[user_id] = user_data 

        return jsonify({"status": "success", 
                        "message": "Coupon applied successfully.", 
                        "new_product_price": user_data['product_price'], 
                        "new_user_balance": user_data['user_balance']})

    return jsonify({"status": "error", 
                    "message": "Coupon application failed or already applied."})


@app.route('/delete_coupon', methods=['POST'])
def delete_coupon():
    user_id = session['user_id']
    user_data = user_data_store.get(user_id, {})

    if user_data.get('coupon_applied', False):
        user_data['product_price'] += coupon_discount
        user_data['coupon_applied'] = False
        user_data['coupon_code'] = ""

        user_data_store[user_id] = user_data 

        return jsonify({"status": "success", "message": "Coupon deleted successfully.", "new_product_price": user_data['product_price']})
    else:
        return jsonify({"status": "error", "message": "No coupon to delete."})


@app.route('/buy_product', methods=['POST'])
def buy_product():
    user_id = session['user_id']
    user_data = user_data_store.get(user_id, {})

    if user_data.get('user_balance', 0) < user_data.get('product_price', 0):
        return jsonify({"status": "error", "message": "Insufficient funds to purchase the product."})

    user_data['user_balance'] -= user_data.get('product_price', 0)
    reset_coupon(user_id)  

    user_data_store[user_id] = user_data

    return jsonify({"status": "success", "message": "GDSC{XXXXXXX}"})

def reset_coupon(user_id):
    user_data = user_data_store.get(user_id, {})
    user_data['coupon_applied'] = False
    user_data['coupon_code'] = ""
    user_data_store[user_id] = user_data

def apply_coupon_logic(coupon_code_input):
    return coupon_code_input == "race"

if __name__ == '__main__':
    app.run(debug=True)