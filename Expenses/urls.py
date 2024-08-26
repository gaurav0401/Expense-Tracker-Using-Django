from django.contrib import admin
from django.urls import path
from Expenses import views

from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('', views.index , name="home"),
    path('add-expense' , views.addExpense, name="add-expense"),
    path('expense-edit/<int:id>' , views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>', views.delete_expense, name="expense-delete"),
    path('search-expenses', csrf_exempt(views.search_expenses),name="search_expenses"),
]
