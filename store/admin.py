from django.contrib import admin

from .models import Category, Product

admin.site.site_header = 'CoE Digital Manufacturing Administration'
admin.site.site_title  = 'CoE Digital Manufacturing'
admin.site.index_title  = 'Admin'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # list_display = ['title', 'slug', 'price', 'in_stock', 'created', 'updated'] # original
    list_display = ['title', 'slug', 'price', 'in_stock', 'updated']
    list_filter = ['in_stock', 'is_active']
    list_editable = ['price', 'in_stock']
    prepopulated_fields = {'slug': ('title',)}