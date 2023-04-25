from flask import Flask, render_template, request, jsonify
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

if __name__ == "__main__":
    fba_fee = float(input("Please enter the FBA fee for 3P(Seller) business model: "))
    vendor_terms = float(input("Please enter the vendor terms (in percentage) for 1P(Vendor) business model: "))

    tilting_point, profit_3P_Seller, profit_1P_Vendor = find_tilting_point(fba_fee, vendor_terms)
    if tilting_point is not None:
        print(f"The tilting point where the 3P(Seller) business model becomes more profitable is at a price of {tilting_point:.2f}")
        print(f"Profit for 3P(Seller) business model at the tilting point: {profit_3P_Seller:.2f}")
        print(f"Profit for 1P(Vendor) business model at the tilting point: {profit_1P_Vendor:.2f}")

# Flask App
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    fba_fee = float(request.form['fba_fee'])
    vendor_terms = float(request.form['vendor_terms'])
    tilting_point, profit_3P_Seller, profit_1P_Vendor = find_tilting_point(fba_fee, vendor_terms)

    if tilting_point is not None:
        return jsonify({
            'tilting_point': f"{tilting_point:.2f}",
            'profit_3P_Seller': f"{profit_3P_Seller:.2f}",
            'profit_1P_Vendor': f"{profit_1P_Vendor:.2f}",
        })
    else:
        return jsonify({'error': "Could not find tilting point within reasonable limits."})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
