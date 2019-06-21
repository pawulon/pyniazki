from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, request
from flask_pymongo import PyMongo

from db import BudgetDB

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://192.168.1.20:27017/budget_db'
mongo = PyMongo(app)
expenses = mongo.db.expenses
categories = mongo.db.categories
db = BudgetDB(expenses=expenses, categories=categories)


@app.route('/add_expense', methods=['POST'])
def add_expense():
    category_name = request.values['name']
    if not db.does_category_exist(category_name):
        db.insert_category(category_name)
    date_string = request.values['date_string']
    date = datetime.strptime(date_string, '%Y-%m-%d')
    db.insert_expense(name=category_name,
                      value=float(request.values['value']),
                      date=date)
    return redirect(f'/{date_string}')


@app.route('/delete_expense/<id>', methods=['POST'])
def delete_expense(id: str):
    db.delete_expense(id)
    return redirect('/')


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
    return render_template('index.html',
                           date_formatted=date_formatted,
                           today_expenses=today_expenses,
                           total=total,
                           date_string=date_string,
                           prev_date=prev_date,
                           next_date=next_date,
                           categories=categories,
                           categories_values=categories_values)


if __name__ == '__main__':
    app.run()
    # db = BudgetDB(expenses=expenses, categories=categories)
    # print(db.sum_all_categories_on_month())
    # db.insert_category('Jedzenie')
    # db.insert_category('Praca - transport')