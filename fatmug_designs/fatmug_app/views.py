from rest_framework import generics
from rest_framework import status
from .serializers import *
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from .models import *
from django.contrib.auth import authenticate


class AdminTokensView(generics.GenericAPIView):
    """
    AdminTokensView is a class-based view for handling token authentication.

    Attributes:
        serializer_class (Serializer): The serializer class for handling token authentication.
        permission_classes (list): The list of permission classes, allowing any user to access this view.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        """
        Handle POST requests to authenticate an admin user and generate an authentication token.

        Args:
            request (Request): The incoming POST request.
            format (str): The format of the response.

        Returns:
            Response: A JSON response containing the authentication token or an error message.
        """
        try:
            # Extract username and password from the incoming POST request data.
            username = request.data.get('username')
            password = request.data.get('password')

            # Attempt to authenticate the user using the provided credentials.
            user = authenticate(username=username, password=password)

            if user:
                # If authentication is successful, generate a token using the specified serializer.
                token = self.serializer_class.get_token(user)

                # Prepare a success response with the generated token and a success message.
                response_dict = {
                    'token': token,
                    'msg': 'Admin login Success'
                }

                # Return a JSON response with the success code and the response data.
                return Response({"code": 200, "data": response_dict}, status=status.HTTP_200_OK)
            else:
                # If authentication fails, return a JSON response indicating the error with a 404 status code.
                return Response({"code": 404, 'errors': 'Email or Password is not Valid'},
                                status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle any exceptions that may occur during the authentication process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class VendorAPIView(generics.GenericAPIView):
    """
    VendorAPIView is a class-based view for handling Vendor-related operations.

    Attributes:
        serializer_class (Serializer): The serializer class for handling vendor data.
        permission_classes (list): The list of permission classes, allowing only admin users to access this view.
    """

    serializer_class = VendorSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        """
        Get the serializer class for retrieving Vendor data with additional metadata.

        Returns:
            Serializer: A custom serializer class for retrieving Vendor data with additional metadata.
        """
        class VendorRetrieveSerializer(self.serializer_class):
            class Meta:
                model = self.serializer_class.Meta.model
                fields = "__all__"
                ref_name = "VendorRetrieveSerializer"
        return VendorRetrieveSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new Vendor instance.

        Args:
            request (Request): The incoming POST request.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A JSON response indicating the success or failure of the vendor creation.
        """
        try:
            # Attempt to create a new Vendor instance using the provided data.
            serializer = self.serializer_class(data=request.data)
            
            if serializer.is_valid(raise_exception=True):
                # If validation is successful, save the Vendor instance and return a success response.
                serializer.save()
                return Response({"message": "Vendor Created Successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle any exceptions that may occur during the creation process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, vendor_id=None):
        """
        Handle GET requests to retrieve vendor data.

        Args:
            request (Request): The incoming GET request.
            vendor_id (int): The ID of the specific vendor to retrieve.

        Returns:
            Response: A JSON response containing the serialized vendor data or an error message.
        """
        try:
            if vendor_id:
                # Retrieve a specific Vendor instance by ID and serialize it using the custom serializer.
                vendor = Vendor.objects.get(id=vendor_id)
                serializer_class = self.get_serializer_class()
                serializer = serializer_class(vendor)
            else:
                # Retrieve all Vendor instances and serialize them using the default serializer.
                vendors = Vendor.objects.all()
                serializer = self.serializer_class(vendors, many=True)

            # Return a JSON response with the serialized data and a success status code.
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any exceptions that may occur during the retrieval process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, vendor_id=None):
        """
        Handle PUT requests to update an existing Vendor instance.

        Args:
            request (Request): The incoming PUT request.
            vendor_id (int): The ID of the specific vendor to update.

        Returns:
            Response: A JSON response indicating the success or failure of the vendor update.
        """
        try:
            if vendor_id:
                # Retrieve a specific Vendor instance by ID, update it with the provided data, and save it.
                vendor = Vendor.objects.get(id=vendor_id)
                serializer = self.serializer_class(data=request.data, instance=vendor, partial=True)
                
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response({"message": "Your details are updated successfully"}, status=status.HTTP_200_OK)

            else:
                # If no vendor_id is provided, return an error response.
                return Response({"error": "Enter a valid vendor_id"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any exceptions that may occur during the update process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, vendor_id=None):
        """
        Handle DELETE requests to delete a specified Vendor instance.

        Args:
            request (Request): The incoming DELETE request.
            vendor_id (int): The ID of the specific vendor to delete.

        Returns:
            Response: A JSON response indicating the success or failure of the vendor deletion.
        """
        try:
            if vendor_id:
                # Retrieve a specific Vendor instance by ID and delete it.
                vendor = Vendor.objects.get(id=vendor_id)
                vendor.delete()
                
                # Return a success response indicating the successful deletion.
                return Response({"message": "Vendor deleted successfully"}, status=status.HTTP_200_OK)

            else:
                # If no vendor_id is provided, return an error response.
                return Response({"error": "Enter a valid vendor ID"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any exceptions that may occur during the deletion process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class PurchaseOrderView(generics.GenericAPIView):
    """
    PurchaseOrderView is a class-based view for handling Purchase Order-related operations.

    Attributes:
        serializer_class (Serializer): The serializer class for handling purchase order data.
        permission_classes (list): The list of permission classes, allowing only admin users to access this view.
    """

    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new Purchase Order instance.

        Args:
            request (Request): The incoming POST request.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A JSON response indicating the success or failure of the purchase order creation.
        """
        try:
            # Attempt to create a new Purchase Order instance using the provided data.
            serializer = self.serializer_class(data=request.data, partial=True)
            
            if serializer.is_valid(raise_exception=True):
                # If validation is successful, save the Purchase Order instance and return a success response.
                serializer.save()
                return Response({"message": "Purchase Order Created Successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle any exceptions that may occur during the creation process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        """
        Get the queryset of Purchase Orders based on query parameters.

        Returns:
            QuerySet: A queryset of Purchase Orders based on the provided parameters.
        """
        # Retrieve query parameters for filtering Purchase Orders.
        vendor_id = request.GET.get("vendor_id", None)
        purchase_order_id = kwargs.get("po_id", None)
        
        try:
            if vendor_id:
                purchase_orders = PurchaseOrder.objects.filter(vendor_id=vendor_id)
                serializer = self.serializer_class(purchase_orders, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            if purchase_order_id:
                purchase_orders = PurchaseOrder.objects.get(id=purchase_order_id)
                serializer = self.serializer_class(purchase_orders)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # If no parameters are provided, return all Purchase Orders.
            purchase_orders = PurchaseOrder.objects.all()
            serializer = self.serializer_class(purchase_orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests to update an existing Purchase Order instance.

        Args:
            request (Request): The incoming PUT request.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A JSON response indicating the success or failure of the purchase order update.
        """
        try:
            # Retrieve Purchase Order ID from URL parameters.
            po_id = kwargs.get("po_id")
            purchase_order = PurchaseOrder.objects.get(id=po_id)
            
            # Update the existing Purchase Order instance with the provided data.
            serializer = self.serializer_class(data=request.data, instance=purchase_order, partial=True)
            
            if serializer.is_valid(raise_exception=True):
                # If validation is successful, save the updated Purchase Order and return a success response.
                serializer.save()
                return Response({"message": "Purchase Order Updated Successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any exceptions that may occur during the update process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, po_id=None):
        """
        Handle DELETE requests to delete a specified Purchase Order instance.

        Args:
            request (Request): The incoming DELETE request.
            po_id (int): The ID of the Purchase Order to be deleted.

        Returns:
            Response: A JSON response indicating the success or failure of the purchase order deletion.
        """
        try:
            # Retrieve and delete the specified Purchase Order instance by ID.
            purchase_order = PurchaseOrder.objects.get(id=po_id)
            purchase_order.delete()
            
            # Return a success response indicating the successful deletion.
            return Response({"message": "Purchase Order Successfully Deleted"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any exceptions that may occur during the deletion process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PerformanceMetricsView(generics.GenericAPIView):
    """
    PerformanceMetricsView is a class-based view for retrieving performance metrics of a specific vendor.

    Attributes:
        serializer_class (Serializer): The serializer class for handling vendor data.
        permission_classes (list): The list of permission classes, allowing only admin users to access this view.
    """

    serializer_class = VendorSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        """
        Get the serializer class specifically tailored for performance metrics.

        Returns:
            Serializer: A serializer class with a subset of fields related to performance metrics.
        """
        class PurchaseMetricsSerializer(self.serializer_class):
            class Meta:
                model = self.serializer_class.Meta.model
                fields = ["on_time_delivery_rate", "quality_rating_avg", "average_response_time", "fulfillment_rate"]

        return PurchaseMetricsSerializer

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve performance metrics for a specific vendor.

        Args:
            request (Request): The incoming GET request.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A JSON response containing the performance metrics data or an error message.
        """
        try:
            # Retrieve the vendor ID from URL parameters.
            vendor_id = kwargs.get("vendor_id")

            # Retrieve the vendor instance using the ID.
            vendor = Vendor.objects.get(id=vendor_id)

            # Get the serializer class tailored for performance metrics.
            serializer_class = self.get_serializer_class()

            # Serialize the vendor instance with the performance metrics serializer.
            serializer = serializer_class(vendor)

            # Return a JSON response with the serialized data and a success status code.
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any exceptions that may occur during the retrieval process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcknowledgePOView(generics.GenericAPIView):
    """
    AcknowledgePOView is a class-based view for updating the acknowledgment status of a purchase order.

    Attributes:
        serializer_class (Serializer): The serializer class for handling purchase order data.
        permission_classes (list): The list of permission classes, allowing only admin users to access this view.
    """

    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to update the acknowledgment status of a purchase order.

        Args:
            request (Request): The incoming POST request.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A JSON response indicating the success or failure of the acknowledgment update.
        """
        try:
            # Retrieve the purchase order ID from URL parameters.
            po_id = kwargs.get("po_id")

            # Retrieve the purchase order instance using the ID.
            purchase_order = PurchaseOrder.objects.get(id=po_id)

            # Update the acknowledgment date to the current time.
            purchase_order.acknowledgment_date = timezone.now()

            if not purchase_order.status == "complete":
                # If the purchase order status is not "complete," update it and save the changes.
                purchase_order.status = "complete"
                purchase_order.save()

                # Trigger the creation of performance metrics for the associated vendor.
                create_performance_metrics(purchase_order.vendor)

                # Return a success response.
                return Response({"message": "Acknowledgment updated successfully"}, status=status.HTTP_200_OK)

            # If the purchase order is already acknowledged, return an error response.
            return Response({"error": "This Purchase Order is already acknowledged"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Handle any exceptions that may occur during the acknowledgment process and return an error response.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    