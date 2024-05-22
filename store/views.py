from django.shortcuts import get_object_or_404, render
from .models import Category, Product

from django.http import HttpResponse
import paho.mqtt.publish as publishing

import pandas as pd

def product_all(request):
    products = Product.products.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, in_stock=True)
    designations_list = product.get_designations_as_list()
    return render(request, 'store/products/single.html', {'product': product, 'designations_list':designations_list})

def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'store/products/category.html', {'category':category, 'products':products})

def run_mqtt(request):
    if request.POST.get('action') == 'post':
        # designation_name = str(request.POST.get("designation").strip())
        designation_name = '6203NR'
        properties = get_properties(designation_name)
        message = f"""The bearing number {designation_name} \
has inner diameter of {properties["d"]}, \
outer diameter of {properties["D"]},  \
bearing height of {properties["B"]}"""
        publishing.single("kv/channel", message, hostname="192.168.0.113")
    return render(request, 'store/products/single.html')

def get_properties(designation_name):
    df = pd.read_csv('static/bearings.csv')
    row = df[df['designation'] == designation_name]
    if not row.empty:
        return row.iloc[0].to_dict()
    else:
        return "Designation not found."