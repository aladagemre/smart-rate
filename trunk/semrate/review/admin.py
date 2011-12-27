from django.contrib import admin
from review.models import Product, Parameter, Tag, Category, CategoryParameter

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','slug','name','category','imgslug')
admin.site.register(Product, ProductAdmin)

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id','slug', 'name', 'product')
admin.site.register(Parameter, ParameterAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ('id','parameter','tagtext')
admin.site.register(Tag, TagAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name','slug')
admin.site.register(Category, CategoryAdmin)


class CategoryParameterAdmin(admin.ModelAdmin):
    list_display = ('id','name','slug')
admin.site.register(CategoryParameter, CategoryParameterAdmin)


