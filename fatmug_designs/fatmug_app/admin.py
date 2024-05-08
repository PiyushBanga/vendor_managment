from django.contrib import admin
from .models import Vendor, PurchaseOrder, HistoricalPerformance

class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor_code', 'on_time_delivery_rate', 'quality_rating_avg')
    search_fields = ('name', 'vendor_code')
    list_filter = ('on_time_delivery_rate', 'quality_rating_avg')

admin.site.register(Vendor, VendorAdmin)

class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'vendor', 'order_date', 'delivery_date', 'status')
    search_fields = ('po_number', 'vendor__name')
    list_filter = ('vendor', 'status')

admin.site.register(PurchaseOrder, PurchaseOrderAdmin)

class HistoricalPerformanceAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'date', 'on_time_delivery_rate', 'quality_rating_avg')
    search_fields = ('vendor__name',)
    list_filter = ('vendor',)

admin.site.register(HistoricalPerformance, HistoricalPerformanceAdmin)
