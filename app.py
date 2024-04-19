from flask import Flask, request, render_template, jsonify
import json

app = Flask(__name__)

# Define the knowledge base with updated tax rules and brackets
knowledge_base_data = {
    "federal": {
        "basic_personal_amount": 14270,
        "tax_brackets": [
            {"rate": 0.15, "up_to": 55867},
            {"rate": 0.205, "up_to": 111733},
            {"rate": 0.26, "up_to": 173205},
            {"rate": 0.29, "up_to": 246752},
            {"rate": 0.33, "up_to": None}
        ]
    },
    "provinces": {
        "Ontario": [
            {"rate": 0.0505, "up_to": 51446},
            {"rate": 0.0915, "up_to": 102894},
            {"rate": 0.1116, "up_to": 150000},
            {"rate": 0.1216, "up_to": 220000},
            {"rate": 0.1316, "up_to": None}
        ]
    },
    "deductions": {
        "rrsp": 0.18
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            income = float(request.form['income'])
            province = request.form['province']
            rrsp_contribution = float(request.form['rrsp']) / 100
            tax_payable = calculate_tax(income, province, rrsp_contribution)
            return render_template('index.html', result=f"Your estimated tax payable is: ${tax_payable:.2f}")
        except ValueError:
            return render_template('index.html', result="Invalid input. Please enter numeric values.")
    return render_template('index.html', result=None)

def calculate_tax(income, province, rrsp_contribution):
    rules = knowledge_base_data
    federal_tax_due = apply_tax_brackets(income, rules["federal"]["tax_brackets"])
    provincial_tax_due = apply_tax_brackets(income, rules["provinces"][province])
    total_tax_due = federal_tax_due + provincial_tax_due - (income * rules["deductions"]["rrsp"] * rrsp_contribution)
    return max(0, total_tax_due)

def apply_tax_brackets(income, brackets):
    tax_due = 0
    for bracket in brackets:
        if bracket["up_to"] is not None:
            taxable_income = min(income, bracket["up_to"])
        else:
            taxable_income = income

        tax_due += taxable_income * bracket["rate"]
        income -= taxable_income

        if income <= 0:
            break

    return tax_due

if __name__ == '__main__':
    app.run(debug=True)
