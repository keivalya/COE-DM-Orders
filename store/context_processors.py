from .models import Category, Product

def categories(request):
    return {
        'categories': Category.objects.all()
    }

def products(request):
    return {
        'products': Product.objects.all()
    }