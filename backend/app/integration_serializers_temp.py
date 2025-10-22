
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
