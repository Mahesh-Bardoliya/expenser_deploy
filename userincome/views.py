import csv
from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
import datetime
from django.http import JsonResponse,HttpResponse
# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user).order_by('-date')
    context = {
        'income': income,
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['date']
        source = request.POST['source']

        if not amount:
            messages.error(request,"Amount cannot be empty")
            return render(request, 'income/add_income.html',context)
        if not description:
            messages.error(request,"Description cannot be empty")
            return render(request, 'income/add_income.html',context)
        if not source:
            messages.error(request,"Source cannot be  empty")
            return render(request, 'income/add_income.html',context)
        if not date:
            messages.error(request,"Date cannot be empty")
            return render(request, 'income/add_income.html',context)
        UserIncome.objects.create(owner=request.user, amount=amount, date=date,source=source, description=description)
        messages.success(request,'Income added successfully')
        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['date']
        source = request.POST['source']

        if not amount:
            messages.error(request,"Amount cannot be empty")
            return render(request, 'income/edit_income.html',context)
        if not description:
            messages.error(request,"Description cannot be empty")
            return render(request, 'income/edit_income.html',context)
        if not source:
            messages.error(request,"Source cannot be empty")
            return render(request, 'income/edit_income.html',context)
        if not date:
            messages.error(request,"Date cannot be empty")
            return render(request, 'income/edit_income.html',context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description
        income.save()
        messages.success(request,'Income updated successfully')
        return redirect('income')

    

def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')



def income_source_summary(request):
    from_date=request.GET.get('from_date')
    to_date=request.GET.get('to_date')
    if not from_date:
        todays_date = datetime.date.today()
        six_months_ago = todays_date-datetime.timedelta(days=30*6)
        incomz = UserIncome.objects.filter(owner=request.user,
                                        date__gte=six_months_ago, date__lte=todays_date)
        finalrep = {}
        def get_source(income):
            return income.source
        source_list = list(set(map(get_source, incomz)))
        def get_income_source_amount(source):
            amount = 0
            filtered_by_source = incomz.filter(source=source)

            for item in filtered_by_source:
                amount += item.amount
            return amount

        for x in incomz:
            for y in source_list:
                finalrep[y] = get_income_source_amount(y)

        return JsonResponse({'income_source_data': finalrep}, safe=False)
    else:
        incomz = UserIncome.objects.filter(owner=request.user,
                                        date__gte=from_date, date__lte=to_date)
        finalrep = {}
        def get_source(income):
            return income.source
        source_list = list(set(map(get_source, incomz)))
        def get_income_source_amount(source):
            amount = 0
            filtered_by_source = incomz.filter(source=source)

            for item in filtered_by_source:
                amount += item.amount
            return amount

        for x in incomz:
            for y in source_list:
                finalrep[y] = get_income_source_amount(y)

        return JsonResponse({'income_source_data': finalrep}, safe=False)



@login_required(login_url="/authentication/login")
def instats_view(request):
    return render(request, 'income/stats.html')


def export_income_csv(request):
    
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=income'+\
        str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])

    expenses= UserIncome.objects.filter(owner=request.user).order_by('-date')

    for expense in expenses:
        writer.writerow([expense.amount,expense.description , expense.source, expense.date])  

    return response

def import_income_csv(request):
    from_date=request.GET.get('from_date')
    to_date=request.GET.get('to_date')
    if not from_date:
        todays_date = datetime.date.today()
        six_months_ago = todays_date-datetime.timedelta(days=30*6)
        incomz = UserIncome.objects.filter(owner=request.user,
                                        date__gte=six_months_ago, date__lte=todays_date)
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('income')
        
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        num_rows_added = 0
        
        for row in reader:
            amount = row.get('Amount')
            description = row.get('Description')
            source_name = row.get('Source')
            date_str = row.get('Date')
           
            if not (amount and description and source_name and date_str):
                messages.warning(request, 'Skipped row: Incomplete data.')
                continue
           


            try:
           
                source = Source.objects.get(name=source_name)
            except Source.DoesNotExist:
           
                messages.error(request, f"Source '{source_name}' does not exist.")
                continue
            
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, f'Skipped row: Invalid date format ({date_str }). It should be in YYYY-MM-DD format.')
                continue
            
            UserIncome.objects.create(owner=request.user, amount=amount, description=description,
                                    source=source, date=date)
            num_rows_added += 1
        
        messages.success(request, f'Successfully added {num_rows_added} rows.')
        return redirect('income')

    return render(request, 'income')

def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)
    