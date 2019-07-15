from calendar import monthrange
from datetime import datetime
from typing import Dict

from bson import ObjectId

from utils import round_float


class BudgetDB:
    def __init__(self, expenses, categories):
        self.expenses = expenses
        self.categories = categories

    def insert_expense(self, name: str, value: float, date: datetime = None) -> None:
        if date is None:
            date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        expense = {
            'name': name,
            'value': value,
            'date': date
        }
        self.expenses.insert_one(expense)

    def sum_expenses_on_date(self, date: datetime = None) -> float:
        if date is None:
            date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        pipe = [{'$match': {'date': {'$eq': date}}},
                {'$group': {'_id': None, 'total': {'$sum': '$value'}}}]
        results = self.expenses.aggregate(pipeline=pipe)
        try:
            return round_float(results.next()['total'])
        except StopIteration:
            return 0

    def get_all_expenses_from_category_on_month(self, date: datetime = None):
        pass

    def sum_all_categories_on_month(self, date: datetime = None) -> Dict[str, float]:
        if date is None:
            date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        categories = self.get_all_categories()
        categories_values = {}
        for category in categories:
            category_name = category['name']
            if not self.is_category_empty(category_name):
                categories_values[category_name] = self.sum_category_expenses_on_month(category_name, date)
        return categories_values

    def sum_category_expenses_on_month(self, category: str, date: datetime = None) -> float:
        if date is None:
            date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = date.replace(day=1)
        end_date = date.replace(day=monthrange(date.year, date.month)[1])
        pipe = [{'$match': {'date': {'$gte': start_date, '$lte': end_date},
                            'name': {'$eq': category}}},
                {'$group': {'_id': None, 'total': {'$sum': '$value'}}}]
        results = self.expenses.aggregate(pipeline=pipe)
        try:
            return results.next()['total']
        except StopIteration:
            return 0

    def delete_expense(self, id: str):
        expense_name = self.get_expense_name(id)
        self.expenses.delete_one({'_id': ObjectId(id)})
        if self.is_category_empty(expense_name):
            self.delete_category(expense_name)

    def get_expense_name(self, id: str):
        expense = self.expenses.find_one({'_id': ObjectId(id)})
        return expense['name']

    def get_expenses_on_date(self, date: datetime = None):
        if date is None:
            date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        return [expense for expense in self.expenses.find(filter={'date': date})]

    def get_all_expenses(self):
        return [expense for expense in self.expenses.find()]

    def insert_category(self, name: str) -> None:
        category = {
            'name': name
        }
        self.categories.insert_one(category)

    def delete_category(self, name: str):
        self.categories.delete_one({'name': name})

    def get_all_categories(self):
        return [category for category in self.categories.find()]

    def does_category_exist(self, name: str):
        if self.categories.find_one({'name': name}):
            return True
        else:
            return False

    def is_category_empty(self, name):
        if self.expenses.find_one({'name': name}):
            return False
        else:
            return True
