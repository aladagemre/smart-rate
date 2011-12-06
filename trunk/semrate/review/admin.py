from django.contrib import admin
from review.models import Product, Parameter, Tag

class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Product, ProductAdmin)

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id','product','name')
admin.site.register(Parameter, ParameterAdmin)

class TagAdmin(admin.ModelAdmin):
    pass
admin.site.register(Tag, TagAdmin)




