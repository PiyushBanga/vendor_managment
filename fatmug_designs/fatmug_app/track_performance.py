from .models import PurchaseOrder, HistoricalPerformance
from django.db.models import Avg, ExpressionWrapper, F, fields
from django.utils import timezone

def create_performance_metrics(vendor):
    """
    Create and update performance metrics for a given vendor based on their purchase orders.

    Args:
        vendor (Vendor): The vendor for which performance metrics are to be calculated.
    """
    # Filter purchase orders for the specified vendor.
    purchase_orders = PurchaseOrder.objects.filter(vendor_id=vendor.id)
    
    # Filter completed orders.
    completed_orders = purchase_orders.filter(status="complete")

    if purchase_orders.exists():
        if completed_orders.exists():
            # Calculate on-time delivery rate.
            on_time_delivery_purchase_orders = completed_orders.filter(delivery_date__gte=F('acknowledgment_date'))
            on_time_delivery_rate = (on_time_delivery_purchase_orders.count() / completed_orders.count()) * 100
            vendor.on_time_delivery_rate = on_time_delivery_rate

        # Calculate average quality rating.
        average_quality_rating = purchase_orders.aggregate(average_quality_rating=Avg("quality_rating"))
        average_quality_rating = round(average_quality_rating["average_quality_rating"], 2)
        vendor.quality_rating_avg = average_quality_rating

        # Calculate average response time.
        average_response_time = purchase_orders.filter(acknowledgment_date__isnull=False).aggregate(average_response_time=Avg(
            ExpressionWrapper(F('acknowledgment_date') - F('order_date'), output_field=fields.DurationField())
        ))

        if average_response_time["average_response_time"]:
            average_response_time = round(average_response_time["average_response_time"].total_seconds() // (24 * 3600), 2)
            vendor.average_response_time = average_response_time

        # Calculate fulfillment rate.
        completed_order_percentage = (completed_orders.count() / purchase_orders.count()) * 100
        fulfillment_rate = round(completed_order_percentage, 2)
        vendor.fulfillment_rate = fulfillment_rate

        # Save updated performance metrics to the vendor.
        vendor.save()

        # Create historical performance record.
        HistoricalPerformance.objects.create(vendor=vendor, on_time_delivery_rate=on_time_delivery_rate,
                                             quality_rating_avg=average_quality_rating,
                                             average_response_time=average_response_time,
                                             fulfillment_rate=fulfillment_rate)
