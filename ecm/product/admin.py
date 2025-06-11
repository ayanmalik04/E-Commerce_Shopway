from django.contrib import admin
from .models import productt , Payment , Review 
# Register your models here.
admin.site.register(productt)
admin.site.register(Payment)
admin.site.register(Review)


# class SalesReportAdmin(admin.ModelAdmin):
#     list_display = ('report',)

# admin.site.register(SalesReport, SalesReportAdmin)




