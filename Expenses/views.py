from django.shortcuts import render , redirect
from django.http import HttpResponse  , FileResponse
from django.contrib.auth.decorators import login_required
from .models import Category , Expense
from django.contrib import messages
from django.core.paginator import Paginator
from userpreferences.models import UserPreferences
import json
import datetime
import csv
from django.http import JsonResponse
from django.db.models import Sum

from django.template.loader import get_template
from xhtml2pdf import pisa
# Create your views here.



def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url="auth/login")
def index(request):
    currency=UserPreferences.objects.get(user=request.user).currency
    expense=Expense.objects.filter(owner=request.user)
    paginator=Paginator(expense , 8)
    page_number=request.GET.get('page')
    page_obj=Paginator.get_page(paginator,page_number)

    context={
        'expenses':expense,
        'page_obj':page_obj,
        'currency':currency
    }
    return render(request, 'expenses/index.html' , context)

def addExpense(request): 
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add-expenses.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add-expenses.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add-expenses.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('home')
  




@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('home')
    


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('home')





def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')



def Export_CSV(request):
    response=HttpResponse(content_type='text/csv')
    response['Content-disposition']='attachment; file=Expenses'+ str(datetime.datetime.now()) + '.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Category', 'Date'])
    expenses=Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount , expense.description , expense.category , expense.date])
    
    return response


import xlwt

def Export_EXCEL(request):
    response=HttpResponse(content_type='application/ms-excel')
    response['Content-disposition']=f'attachment; filename="Expenses {str(datetime.datetime.now())}.xls"'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Expenses')
    row_num=0
    font_style=xlwt.XFStyle()
    font_style.font.bold=True


    
    columns=['Amount','Description','Category', 'Date']
    for col_num in range (len(columns)):
        ws.write( row_num , col_num , columns[col_num], font_style)
    
    font_style=xlwt.XFStyle()
    rows=Expense.objects.filter(owner=request.user).values_list('amount','description','category', 'date')
    
    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write( row_num , col_num , str(row[col_num]), font_style)

    wb.save(response)
    return response



import io

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = HttpResponse(content_type='application/pdf' )
    # pdf = pisa.CreatePDF(html, dest=result)
    cur=datetime.datetime.now()
 
    with open("ExpenseReport.pdf", 'wb') as output:
        pdf = pisa.CreatePDF(io.StringIO(html), dest=output)
    
    if not pdf.err:
    
        return redirect('/')
    return HttpResponse('We had some errors while generating the PDF', status=400)

def Export_PDF(request):
   
    expenses=Expense.objects.filter(owner=request.user)
    total=expenses.aggregate(Sum('amount'))
    # Create the context to pass to the template
    context = {
        'expenses': expenses,
        'total': total['amount__sum']
        
    }

    # Render the PDF
    return render_to_pdf('expenses\expense-pdf.html', context)