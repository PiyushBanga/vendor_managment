# serializers.py

from rest_framework import serializers
from .models import Vendor, PurchaseOrder
from django.utils import timezone
import uuid
from .track_performance import create_performance_metrics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    CustomTokenObtainPairSerializer extends TokenObtainPairSerializer to customize token generation.

    Attributes:
        model (User): The User model used for authentication.
        fields (list): The fields included in the serialized data.
    """

    class Meta:
        model = User
        fields = ["username", "password"]

    @classmethod
    def get_token(cls, user):
        """
        Override the get_token method to customize the token response.

        Args:
            user (User): The authenticated user.

        Returns:
            dict: A dictionary containing the access and refresh tokens.
        """
        token = super().get_token(user)
        user.last_login = timezone.now()
        user.save()
        return {
            'refresh': str(token),
            'access': str(token.access_token),
        }

class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer is a serializer for the User model.

    Attributes:
        model (User): The User model.
        fields (list): The fields included in the serialized data.
    """

    class Meta:
        model = User
        fields = "__all__"

class VendorSerializer(serializers.ModelSerializer):
    """
    VendorSerializer is a serializer for the Vendor model.

    Attributes:
        model (Vendor): The Vendor model.
        fields (list): The fields included in the serialized data.
    """

    class Meta:
        model = Vendor
        fields = ["id", "name", "contact_details", "address"]

    def create(self, validated_data):
        """
        Override the create method to add a vendor code during creation.

        Args:
            validated_data (dict): Validated data for creating a Vendor instance.

        Returns:
            Vendor: The created Vendor instance.
        """
        vendor_code = str(uuid.uuid4().int % 10**6).zfill(6)
        vendor = Vendor.objects.create(**validated_data, vendor_code=vendor_code)
        return vendor

class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
    PurchaseOrderSerializer is a serializer for the PurchaseOrder model.

    Attributes:
        vendor_details (SerializerMethodField): A serializer method field for vendor details.
        model (PurchaseOrder): The PurchaseOrder model.
        fields (list): The fields included in the serialized data.
    """

    vendor_details = serializers.SerializerMethodField('get_vendor_details')

    def get_vendor_details(self, obj):
        """
        Get the serialized vendor details for a PurchaseOrder.

        Args:
            obj (PurchaseOrder): The PurchaseOrder instance.

        Returns:
            dict: Serialized vendor details.
        """
        serializer = VendorSerializer(obj.vendor)
        return serializer.data

    class Meta:
        model = PurchaseOrder
        fields = "__all__"

    def create(self, validated_data):
        """
        Override the create method to add a purchase order number and handle completion status.

        Args:
            validated_data (dict): Validated data for creating a PurchaseOrder instance.

        Returns:
            PurchaseOrder: The created PurchaseOrder instance.
        """
        status = validated_data.get("status")
        po_number = str(uuid.uuid4().int % 10**6).zfill(6)
        purchase_order = PurchaseOrder.objects.create(**validated_data, po_number=po_number)

        if status == "complete":
            purchase_order.acknowledgment_date = timezone.now()
            purchase_order.save()

        create_performance_metrics(purchase_order.vendor)
        return purchase_order

    def update(self, instance, validated_data):
        """
        Override the update method to handle status updates and performance metrics.

        Args:
            instance (PurchaseOrder): The existing PurchaseOrder instance.
            validated_data (dict): Validated data for updating the PurchaseOrder instance.

        Returns:
            PurchaseOrder: The updated PurchaseOrder instance.
        """
        if validated_data:
            for key, value in validated_data.items():
                setattr(instance, key, value)

        if "status" in validated_data.keys():
            status = validated_data.get("status")
            if status == "complete":
                instance.acknowledgment_date = timezone.now()
            else:
                instance.acknowledgment_date = None

            instance.save()

        create_performance_metrics(instance.vendor)
        return instance
