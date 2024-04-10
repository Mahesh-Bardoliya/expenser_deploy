from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="income"),
    path('add-income', views.add_income, name="add-income"),
    path('edit-income/<int:id>', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>', views.delete_income, name="income-delete"),
    path('income_source_summary', views.income_source_summary,name="income_source_summary"),
    path('income-stats', views.instats_view,name="instats"),
    path('export_income_csv', views.export_income_csv,name="export-income-csv"),
    path('import_income_csv', views.import_income_csv,name="import-income-csv"),
    path('search-income', csrf_exempt(views.search_income),name="search_income") 
]