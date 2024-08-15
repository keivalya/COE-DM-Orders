from django.shortcuts import get_object_or_404, render
from .models import Category, Product

from django.http import HttpResponse
import paho.mqtt.publish as publishing

from opcua import Client

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
        properties = get_bearing_properties(designation_name)
        message = f"""The bearing number {designation_name} \
has inner diameter of {properties["d"]}, \
outer diameter of {properties["D"]},  \
bearing height of {properties["B"]}
bearing cell is {properties["cell"]}"""
        publishing.single("kv/channel", message, hostname="192.168.0.113")
    return render(request, 'store/products/single.html')

def run_client(request):
    server_url = "opc.tcp://10.10.14.77:4840"
    client = Client(server_url)
    if request.POST.get('action') == 'post':
        try:
            client.connect()
            print(f"Client connected to {server_url}")

            # READ THE STATION DETAILS
            message_node = client.get_node("ns=2;i=2")
            message_node.set_value(1)
            print("Station Number #", message_node.get_value())
            # FINISH STATION DETAILS

            ### BEARING PROPERTIES AND OPERATIONS  -- START HERE \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
            designation_name = str(request.POST.get("designation").strip())
            bearing_properties = get_bearing_properties(designation_name)
            print(bearing_properties)

            # get bearing number (or name)
            bearing_no_node = client.get_node("ns=2;i=3")
            bearing_no_node.set_value(bearing_properties["designation"])
            bearing_cell_node = client.get_node("ns=2;i=10")
            bearing_cell_node.set_value(bearing_properties["cell"])
            print("The selected bearing number is: ", bearing_no_node.get_value() , "in the cell number", str(bearing_cell_node.get_value()))

            # inner diameter of bearing
            inner_diameter_node = client.get_node("ns=2;i=4")
            inner_diameter_node.set_value(bearing_properties["d"])
            print("The inner diameter is: ", inner_diameter_node.get_value())

            # outer diameter of bearing
            outer_diameter_node = client.get_node("ns=2;i=5")
            outer_diameter_node.set_value(bearing_properties["D"])
            print("The outer diameter is: ", outer_diameter_node.get_value())

            # height of bearing
            bearing_height_node = client.get_node("ns=2;i=6")
            bearing_height_node.set_value(bearing_properties["B"])
            print("The height of the bearing is: ", bearing_height_node.get_value())
            ### BEARING PROPERTIES AND OPERATIONS  -- END HERE \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\


            ### HOUSING PROPERTIES AND OPERATIONS  -- START HERE \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
            housing_type = str(request.POST.get("housing").strip())
            housing_properties = get_housing_properties(housing_type)
            housing_type_node = client.get_node("ns=2;i=7")
            housing_type_node.set_value(housing_type)
            print("The selected housing number is: ", housing_type_node.get_value())

            # get housing cell number=
            housing_cell_node = client.get_node("ns=2;i=11")
            housing_cell_node.set_value(housing_properties["cell"])
            print("The selected housing is:", housing_type_node.get_value(), "in the cell number", str(housing_cell_node.get_value()))
            ### HOUSING PROPERTIES AND OPERATIONS  -- END HERE \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

            ### SHAFT PROPERTIES -- START HERE \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
            shaft = str(request.POST.get("shaft").strip())
            shaft_properties = get_shaft_properties(shaft)
            shaft_node = client.get_node("ns=2;i=8")
            shaft_node.set_value(shaft)

            # get shaft cell number
            shaft_cell_node = client.get_node("ns=2;i=13")
            shaft_cell_node.set_value(shaft_properties["cell"])
            print("The selected shaft is:", shaft_node.get_value(), "in the cell number", str(shaft_cell_node.get_value()))
            ### SHAFT PROPERTIES -- END HERE \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client.disconnect()
            print("Client disconnected")
    return render(request, 'store/products/single.html')

def get_bearing_properties(designation_name):
    df = pd.read_csv('static/0_bearings.csv')
    row = df[df['designation'] == designation_name]
    if not row.empty:
        return row.iloc[0].to_dict()
    else:
        return "Bearing designation not found."

def get_housing_properties(housing_type):
    df = pd.read_csv('static/0_housings.csv')
    row = df[df['housing_type'] == housing_type]
    if not row.empty:
        return row.iloc[0].to_dict()
    else:
        return "Housing type not found."

def get_shaft_properties(shaft):
    df = pd.read_csv('static/0_shafts.csv')
    row = df[df['shaft'] == shaft]
    if not row.empty:
        return row.iloc[0].to_dict()
    else:
        return "Shaft not found."