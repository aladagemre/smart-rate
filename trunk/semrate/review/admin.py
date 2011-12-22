from django.contrib import admin
from review.models import Product, Parameter, Tag

class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Product, ProductAdmin)

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id','category_parameter', 'product')
admin.site.register(Parameter, ParameterAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ('id','parameter','tagtext')
admin.site.register(Tag, TagAdmin)




