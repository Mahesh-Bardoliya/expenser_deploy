import csv
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Expense,Category
from userincome.models import UserIncome
from django.contrib import messages
from datetime import date, timedelta
import datetime
from django.db import models
import json
from datetime import timedelta
from django.utils import timezone 
from django.http import JsonResponse,HttpResponse
from django.db.models import Sum
    
# Create your views here.
@login_required(login_url="/authentication/login")
def index(request):
    categories = Category.objects.all()
    expenses=Expense.objects.filter(owner=request.user).order_by('-date')
    context={
        'expenses':expenses,
    }
    return render(request, 'expenses/index.html',context)


@login_required(login_url="/authentication/login")
def add_expense(request):
    categories = Category.objects.all()
    context={
            'categories': categories,
            'values': request.POST
        }
    if request.method == 'GET':
        
        return render(request, 'expenses/add_expenses.html',context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['date']
        category = request.POST['category']

        if not amount:
            messages.error(request,"Amount cannot be empty")
            return render(request, 'expenses/add_expenses.html',context)
        if not description:
            messages.error(request,"Description cannot be empty")
            return render(request, 'expenses/add_expenses.html',context)
        if not category:
            messages.error(request,"Category cannot be  empty")
            return render(request, 'expenses/add_expenses.html',context)
        if not date:
            messages.error(request,"Date cannot be empty")
            return render(request, 'expenses/add_expenses.html',context)
        Expense.objects.create(owner=request.user,amount=amount,date=date,description=description,category=category)
        messages.success(request,'Expense added successfully')
        return render(request, 'expenses/add_expenses.html',context)
        
def edit_expense(request,id):
    expense= Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context={
        'expense':expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html',context)
    if request.method == 'POST':   
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['date']
        category = request.POST['category']

        if not amount:
            messages.error(request,"Amount cannot be empty")
            return render(request, 'expenses/edit_expense.html',context)
        if not description:
            messages.error(request,"Description cannot be empty")
            return render(request, 'expenses/edit_expense.html',context)
        if not category:
            messages.error(request,"Category cannot be empty")
            return render(request, 'expenses/edit_expense.html',context)
        if not date:
            messages.error(request,"Date cannot be empty")
            return render(request, 'expenses/edit_expense.html',context)
        expense.owner=request.user
        expense.amount=amount
        expense.date=date
        expense.description=description
        expense.category=category
        expense.save()
        messages.success(request,'Expense updated successfully')
        return render(request, 'expenses/edit_expense.html',context)
    
def delete_expense(request,id):
    expense= Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense deleted successfully')
    return redirect("expenses")

def expense_category_summary(request):
    from_date=request.GET.get('from_date')
    to_date=request.GET.get('to_date')
    if not from_date:
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
    else:
        expenses = Expense.objects.filter(owner=request.user,
                                        date__gte=from_date, date__lte=to_date)
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


@login_required(login_url="/authentication/login")
def stats_view(request):
    return render(request, 'expenses/stats.html')


@login_required(login_url="/authentication/login")
def dashboard(request):
    user = request.user
    today = date.today()
    one_week_ago = today - timedelta(days=7)
    yesterday = today - timedelta(days=1)
    one_month_ago = today - timedelta(days=30)
    total_income = UserIncome.objects.filter(owner=user).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate total expense
    total_expense = Expense.objects.filter(owner=user).aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate balance
    balance = total_income - total_expense
    if balance<0:
        messages.error(request, 'We have noticed a negative balance, which could indicate missing income sources. Kindly provide all relevant income data to ensure accuracy.')
    


    
    total_expense_one_week_ago = Expense.objects.filter(owner=user, date__gte=one_week_ago, date__lte=today).aggregate(models.Sum('amount'))['amount__sum'] or 0

    
    total_expense_one_month_ago = Expense.objects.filter(owner=user, date__gte=one_month_ago, date__lte=today).aggregate(models.Sum('amount'))['amount__sum'] or 0

    total_expense_yesterday= Expense.objects.filter(owner=user, date__gte=yesterday, date__lte=today).aggregate(models.Sum('amount'))['amount__sum'] or 0

    context = {
        'total_expense_one_week_ago': total_expense_one_week_ago,
        'total_expense_one_month_ago': total_expense_one_month_ago,
        'total_expense_yesterday':total_expense_yesterday,
        'user': user,
        'balance': balance 
    }

    return render(request, 'index.html', context)

def export_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses'+\
        str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])

    expenses= Expense.objects.filter(owner=request.user).order_by('-date')

    for expense in expenses:
        writer.writerow([expense.amount,expense.description , expense.category, expense.date])  

    return response


def import_csv(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('expenses')
        
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        num_rows_added = 0
        
        for row in reader:
            amount = row.get('Amount')
            description = row.get('Description')
            category_name = row.get('Category')
            date_str = row.get('Date')
           
            if not (amount and description and category_name and date_str):
                messages.warning(request, 'Skipped row: Incomplete data.')
                continue
            try:
           
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
           
                messages.error(request, f"Category '{category_name}' does not exist.")
                continue
            
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, f'Skipped row: Invalid date format ({date_str}). It should be in YYYY-MM-DD format.')
                continue
            
            Expense.objects.create(owner=request.user, amount=amount, description=description,
                                    category=category, date=date)
            num_rows_added += 1
        
        messages.success(request, f'Successfully added {num_rows_added} rows.')
        return redirect('expenses')

    return render(request, 'expenses/import_csv.html')


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
    