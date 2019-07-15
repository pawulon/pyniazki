from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo

from db import BudgetDB
from utils import round_float, format_float_input_string

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/budget_db'
mongo = PyMongo(app)
expenses = mongo.db.expenses
categories = mongo.db.categories
db = BudgetDB(expenses=expenses, categories=categories)


@app.route('/add_expense', methods=['POST'])
def add_expense():
    date_string = request.values['date_string']
    try:
        expense_value = format_float_input_string(request.values['value'])
    except ValueError as e:
        return redirect(url_for('.home_page', day=date_string, error=e))
    category_name = request.values['name']
    date = datetime.strptime(date_string, '%Y-%m-%d')
    db.insert_expense(name=category_name,
                      value=expense_value,
                      date=date)
    if not db.does_category_exist(category_name):
        db.insert_category(category_name)
    return redirect(f'/{date_string}')


@app.route('/delete_expense/<id>', methods=['POST'])
def delete_expense(id: str):
    date_string = request.values['date_string']
    db.delete_expense(id)
    return redirect(f'/{date_string}')


months = {
    1: 'stycznia',
    2: 'lutego',
    3: 'marca',
    4: 'kwietnia',
    5: 'maja',
    6: 'czerwca',
    7: 'lipca',
    8: 'sierpnia',
    9: 'września',
    10: 'października',
    11: 'listopada',
    12: 'grudnia'
}


@app.route('/category')
def category():
    pass


@app.route('/', methods=['GET'])
@app.route('/<day>', methods=['GET'])
def home_page(day=None):
    error = request.args['error'] if 'error' in request.args else None
    if day is None:
        date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        date = datetime.strptime(day, '%Y-%m-%d')
    prev_date = (date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (date + timedelta(days=1)).strftime('%Y-%m-%d')
    date_string = date.strftime('%Y-%m-%d')
    today_expenses = db.get_expenses_on_date(date)
    day = str(date.day).zfill(2)
    month = months[date.month]
    year = date.year
    date_formatted = f'{day} {month} {year}'
    total = db.sum_expenses_on_date(date)
    categories = db.get_all_categories()
    categories_values = db.sum_all_categories_on_month(date)
    month_total = round_float(sum([value for value in categories_values.values()]))
    return render_template('index.html',
                           date_formatted=date_formatted,
                           today_expenses=today_expenses,
                           total=total,
                           date_string=date_string,
                           prev_date=prev_date,
                           next_date=next_date,
                           categories=categories,
                           categories_values=categories_values,
                           month_total=month_total,
                           error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # db = BudgetDB(expenses=expenses, categories=categories)
    # print(db.is_category_empty('Bubu'))
    # db.insert_category('Jedzenie')
    # db.insert_category('Praca - transport')
