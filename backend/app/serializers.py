from rest_framework import serializers
from .models import (
    Product, Category, Retailer, Order, OrderItem, Employee, Truck, Shipment,
    Invoice, InvoiceItem, Company, PasswordResetOTP, RetailerProfile, 
    CompanyRetailerConnection, CompanyInvite, RetailerRequest,
    IntegrationConfig, IntegrationLog
)
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
   

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'  # Keep all fields from the Product model, but override 'category'
        extra_kwargs = {
            'company': {'required': True},
            'category': {'required': False, 'allow_null': True},
            'created_by': {'read_only': True},
        }


class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retailer
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    retailer_name = serializers.CharField(source='retailer.name', read_only=True)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['order_id', 'retailer', 'retailer_name', 'order_date', 'status', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        return instance


class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class ShipmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = Shipment
        fields = '__all__'
    
    def get_employee_name(self, obj):
        if obj.employee and obj.employee.user:
            return obj.employee.user.username
        return None

    def update(self, instance, validated_data):
        """
        When status is updated to 'delivered', update:
        - The order's status
        - The product's total_required_quantity and total_shipped
        """
        if "status" in validated_data and validated_data["status"] == "delivered":
            order = instance.order

            # Update order status
            order.status = "delivered"
            order.save(update_fields=["status"])

            # Update all products in the order
        for item in order.items.all():
            product = item.product
            product.total_required_quantity = max(0, product.total_required_quantity - item.quantity)
            product.total_shipped += item.quantity
            product.save(update_fields=["total_required_quantity", "total_shipped"])

        return super().update(instance, validated_data)
    
class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['category_id', 'name', 'product_count']


class UserRegistrationSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(write_only=True)  # Accept group name during registration

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'group_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        group_name = validated_data.pop('group_name', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Assign the user to the specified group
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
                # Assign all permissions of the group to the user
                permissions = group.permissions.all()
                user.user_permissions.add(*permissions)
            except Group.DoesNotExist:
                raise serializers.ValidationError({"group_name": "Group does not exist."})

        return user
    
# accounting
class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            'product', 'quantity','price', 'taxable_value', 'gst_rate',
            'cgst', 'sgst', 'igst', 'hsn_code'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    retailer_name = serializers.CharField(source='retailer.name', read_only=True)  

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'company', 'retailer','retailer_name', 'invoice_date','due_date',
            'is_einvoice_generated', 'irn', 'qr_code',
            'total_taxable_value', 'total_cgst', 'total_sgst', 'total_igst',
            'grand_total', 'payment_mode', 'payment_status', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        return invoice


# Password Reset Serializers
class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        
        try:
            user = User.objects.get(username=username, email=email)
            attrs['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username and email does not exist.")
        
        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    otp = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        username = attrs.get('username')
        otp = attrs.get('otp')
        
        try:
            user = User.objects.get(username=username)
            otp_instance = PasswordResetOTP.objects.filter(
                user=user, 
                otp=otp, 
                is_verified=False
            ).first()
            
            if not otp_instance:
                raise serializers.ValidationError("Invalid OTP.")
            
            if otp_instance.is_expired():
                raise serializers.ValidationError("OTP has expired.")
            
            attrs['user'] = user
            attrs['otp_instance'] = otp_instance
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        try:
            user = User.objects.get(username=username)
            otp_instance = PasswordResetOTP.objects.filter(
                user=user, 
                otp=otp, 
                is_verified=True
            ).first()
            
            if not otp_instance:
                raise serializers.ValidationError("Invalid or unverified OTP.")
            
            if otp_instance.is_expired():
                raise serializers.ValidationError("OTP has expired.")
            
            attrs['user'] = user
            attrs['otp_instance'] = otp_instance
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        
        return attrs


# Retailer-specific Serializers
class RetailerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    # Connection statistics
    connected_companies_count = serializers.SerializerMethodField()
    pending_requests_count = serializers.SerializerMethodField()
    total_orders_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RetailerProfile
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
    
    def get_connected_companies_count(self, obj):
        """Get count of connected companies"""
        try:
            return CompanyRetailerConnection.objects.filter(
                retailer=obj,
                status='approved'
            ).count()
        except:
            return 0
    
    def get_pending_requests_count(self, obj):
        """Get count of pending join requests"""
        try:
            return RetailerRequest.objects.filter(
                retailer=obj,
                status='pending'
            ).count()
        except:
            return 0
    
    def get_total_orders_count(self, obj):
        """Get total orders count for this retailer"""
        try:
            return Order.objects.filter(retailer=obj).count()
        except:
            return 0


class CompanyRetailerConnectionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    retailer_name = serializers.CharField(source='retailer.business_name', read_only=True)
    
    class Meta:
        model = CompanyRetailerConnection
        fields = '__all__'


class PublicCompanySerializer(serializers.ModelSerializer):
    """Serializer for public companies that retailers can discover"""
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'city', 'state', 'created_at']


class CompanyInviteSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.username', read_only=True)
    
    class Meta:
        model = CompanyInvite
        fields = '__all__'
        extra_kwargs = {
            'invite_code': {'read_only': True},
            'invited_by': {'read_only': True}
        }


class RetailerRequestSerializer(serializers.ModelSerializer):
    retailer_name = serializers.CharField(source='retailer.business_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = RetailerRequest
        fields = '__all__'
        extra_kwargs = {
            'retailer': {'read_only': True}
        }


class JoinByCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=20)
    
    def validate_invite_code(self, value):
        try:
            invite = CompanyInvite.objects.get(invite_code=value, is_used=False)
            if invite.is_expired():
                raise serializers.ValidationError("Invite code has expired.")
            return value
        except CompanyInvite.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used invite code.")


# Update existing serializers to use new models
class RetailerOrderSerializer(serializers.ModelSerializer):
    """Serializer for orders from retailer perspective"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['order_id', 'company', 'company_name', 'order_date', 'status', 'items']


class RetailerProductSerializer(serializers.ModelSerializer):
    """Serializer for products from retailer perspective"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'category_name', 'company_name', 
            'available_quantity', 'unit', 'price', 'hsn_code', 
            'cgst_rate', 'sgst_rate', 'igst_rate', 'status'
        ]

# Integration Configuration Serializers
class IntegrationConfigSerializer(serializers.ModelSerializer):
    """Serializer for Integration Configuration."""
    integration_type_display = serializers.CharField(source='get_integration_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = IntegrationConfig
        fields = [
            'id', 'company', 'company_name', 'user', 'user_name',
            'integration_type', 'integration_type_display', 'integration_name',
            'status', 'status_display', 'is_active', 'config_data',
            'composio_entity_id', 'last_used_at', 'last_error',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_used_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
        }
    
    def validate(self, data):
        """Validate integration configuration."""
        integration_type = data.get('integration_type')
        config_data = data.get('config_data', {})
        
        # Validate based on integration type
        if integration_type == 'google_sheets':
            if not config_data.get('sheet_id') and not config_data.get('sheet_url'):
                raise serializers.ValidationError({
                    'config_data': 'Google Sheets integration requires either sheet_id or sheet_url'
                })
        
        elif integration_type == 'slack':
            if not config_data.get('webhook_url') and not config_data.get('channel'):
                raise serializers.ValidationError({
                    'config_data': 'Slack integration requires either webhook_url or channel'
                })
        
        elif integration_type == 'google_calendar':
            if not config_data.get('calendar_id'):
                raise serializers.ValidationError({
                    'config_data': 'Google Calendar integration requires calendar_id'
                })
        
        elif integration_type == 'google_drive':
            if not config_data.get('folder_id'):
                raise serializers.ValidationError({
                    'config_data': 'Google Drive integration requires folder_id'
                })
        
        return data


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer for Integration Logs."""
    integration_name = serializers.CharField(source='integration.integration_name', read_only=True)
    integration_type = serializers.CharField(source='integration.integration_type', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'integration', 'integration_name', 'integration_type',
            'action_type', 'action_type_display', 'status', 'status_display',
            'request_data', 'response_data', 'error_message',
            'duration_ms', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class IntegrationConfigCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating integrations via UI."""
    
    # Google Sheets specific
    sheet_url = serializers.URLField(required=False, write_only=True, help_text="Full Google Sheets URL")
    sheet_id = serializers.CharField(required=False, write_only=True, help_text="Google Sheets ID")
    
    # Slack specific
    webhook_url = serializers.URLField(required=False, write_only=True, help_text="Slack Webhook URL")
    channel = serializers.CharField(required=False, write_only=True, help_text="Slack channel name")
    bot_token = serializers.CharField(required=False, write_only=True, help_text="Slack Bot Token")
    
    # Google Calendar specific
    calendar_id = serializers.EmailField(required=False, write_only=True, help_text="Google Calendar ID (email)")
    
    # Google Drive specific
    folder_id = serializers.CharField(required=False, write_only=True, help_text="Google Drive Folder ID")
    folder_url = serializers.URLField(required=False, write_only=True, help_text="Google Drive Folder URL")
    
    class Meta:
        model = IntegrationConfig
        fields = [
            'id', 'integration_type', 'integration_name', 'is_active',
            # Google Sheets
            'sheet_url', 'sheet_id',
            # Slack
            'webhook_url', 'channel', 'bot_token',
            # Google Calendar
            'calendar_id',
            # Google Drive
            'folder_id', 'folder_url',
        ]
    
    def create(self, validated_data):
        """Create integration config with proper config_data structure."""
        # Extract company and user from context
        request = self.context.get('request')
        company = request.user.companies.first()
        
        if not company:
            raise serializers.ValidationError("User must be associated with a company")
        
        integration_type = validated_data.get('integration_type')
        config_data = {}
        
        # Build config_data based on integration type
        if integration_type == 'google_sheets':
            sheet_url = validated_data.pop('sheet_url', None)
            sheet_id = validated_data.pop('sheet_id', None)
            
            if sheet_url:
                # Extract sheet ID from URL
                import re
                match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
                if match:
                    sheet_id = match.group(1)
            
            config_data['sheet_id'] = sheet_id
            config_data['sheet_url'] = sheet_url
        
        elif integration_type == 'slack':
            config_data['webhook_url'] = validated_data.pop('webhook_url', None)
            config_data['channel'] = validated_data.pop('channel', None)
            config_data['bot_token'] = validated_data.pop('bot_token', None)
        
        elif integration_type == 'google_calendar':
            config_data['calendar_id'] = validated_data.pop('calendar_id', None)
        
        elif integration_type == 'google_drive':
            folder_url = validated_data.pop('folder_url', None)
            folder_id = validated_data.pop('folder_id', None)
            
            if folder_url:
                # Extract folder ID from URL
                import re
                match = re.search(r'/folders/([a-zA-Z0-9-_]+)', folder_url)
                if match:
                    folder_id = match.group(1)
            
            config_data['folder_id'] = folder_id
            config_data['folder_url'] = folder_url
        
        # Create the integration
        integration = IntegrationConfig.objects.create(
            company=company,
            user=request.user,
            integration_type=integration_type,
            integration_name=validated_data.get('integration_name'),
            is_active=validated_data.get('is_active', True),
            config_data=config_data,
            status='active'
        )
        
        return integration
