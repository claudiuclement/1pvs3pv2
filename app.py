import os
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, render_template, request, jsonify
import base64
from io import BytesIO
import time

def calculate_profit_3P_Seller(x, fba_fee):
    vat_rate = 0.2
    price_without_vat = x / (1 + vat_rate)
    referral_cost = x * 0.15
    advertising = x * 0.1
    profit = price_without_vat - referral_cost - fba_fee - advertising
    return profit

def calculate_profit_1P_Vendor(x, vendor_terms):
    vat_rate = 0.2
    price_without_vat = x / (1 + vat_rate)
    margin = 0.3
    discounted_price = price_without_vat * (1 - margin)
    amz_vendor_terms = discounted_price * (vendor_terms / 100)
    advertising = x * 0.1
    profit = discounted_price - amz_vendor_terms - advertising
    return profit

def find_tilting_point(fba_fee, vendor_terms):
    price = 0.1
    max_price = 10000
    counter = 0
    while True:
        profit_3P_Seller = calculate_profit_3P_Seller(price, fba_fee)
        profit_1P_Vendor = calculate_profit_1P_Vendor(price, vendor_terms)
        if profit_3P_Seller > profit_1P_Vendor:
            break
        price += 0.01
        counter += 1
        if price > max_price or counter > 100000:
            print("Could not find tilting point within reasonable limits.")
            return None, None, None
    return price, profit_3P_Seller, profit_1P_Vendor

def generate_profit_graph(fba_fee, vendor_terms, tilting_point):
    x = np.arange(1, 301, 1)
    y_3P = [calculate_profit_3P_Seller(price, fba_fee) for price in x]
    y_1P = [calculate_profit_1P_Vendor(price, vendor_terms) for price in x]

    plt.figure(figsize=(10, 5))
    plt.plot(x, y_3P, label="3P Model")
    plt.plot(x, y_1P, label="1P Model")
    
    # Plot the intersection point and add a text annotation
    if tilting_point is not None:
        profit_3P_Seller = calculate_profit_3P_Seller(tilting_point, fba_fee)
        plt.plot(tilting_point, profit_3P_Seller, marker='o', markersize=5, color="red")
        plt.annotate(f'({tilting_point:.2f}, {profit_3P_Seller:.2f})', (tilting_point, profit_3P_Seller), textcoords="offset points", xytext=(-15,7), ha='center', fontsize=8, color='red')
    
    plt.xlabel("Price")
    plt.ylabel("Profit")
    plt.title("Profit Intersection of 3P and 1P Models")
    plt.legend()
    plt.grid(True)
    file_name = f'static/profit_graph_{int(time.time())}.png'
    plt.savefig(file_name, bbox_inches='tight')
    plt.close()
    return file_name


# Flask App
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    fba_fee = float(request.form['fba_fee'])
    vendor_terms = float(request.form['vendor_terms'])
    tilting_point, profit_3P_Seller, profit_1P_Vendor = find_tilting_point(fba_fee, vendor_terms)

    graph_file_name = generate_profit_graph(fba_fee, vendor_terms, tilting_point)

    if tilting_point is not None:
        return jsonify({
            'tilting_point': f"{tilting_point:.2f}",
            'profit_3P_Seller': f"{profit_3P_Seller:.2f}",
            'profit_1P_Vendor': f"{profit_1P_Vendor:.2f}",
            'graph_url': f'/{graph_file_name}'
        })
    else:
        return jsonify({'error': "Could not find tilting point within reasonable limits."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
