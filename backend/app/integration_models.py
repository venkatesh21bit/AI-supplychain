# Integration Configuration Models
from django.db import models
from django.contrib.auth.models import User
from .models import Company
from django.core.exceptions import ValidationError
import json


class IntegrationConfig(models.Model):
    """
    Stores integration credentials and configuration for each company/user.
    This allows users to configure their own Google Sheets, Calendar, Slack, etc.
    """
    
    INTEGRATION_TYPES = [
        ('gmail', 'Gmail'),
        ('slack', 'Slack'),
        ('google_sheets', 'Google Sheets'),
        ('google_calendar', 'Google Calendar'),
        ('google_drive', 'Google Drive'),
    ]
    
    STATUS_CHOICES = [
        ('not_configured', 'Not Configured'),
        ('active', 'Active'),
        ('error', 'Error'),
        ('disabled', 'Disabled'),
    ]
    
    # Ownership
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='integrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integrations')
    
    # Integration details
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    integration_name = models.CharField(max_length=100, help_text="Custom name for this integration")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_configured')
    is_active = models.BooleanField(default=True)
    
    # Configuration data (stored as JSON for flexibility)
    config_data = models.JSONField(default=dict, help_text="Integration-specific configuration")
    
    # OAuth tokens (encrypted in production)
    access_token = models.TextField(blank=True, null=True, help_text="OAuth access token")
    refresh_token = models.TextField(blank=True, null=True, help_text="OAuth refresh token")
    token_expires_at = models.DateTimeField(blank=True, null=True)
    
    # Composio entity ID (if using Composio)
    composio_entity_id = models.CharField(max_length=200, blank=True, null=True)
    
    # Metadata
    last_used_at = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('company', 'integration_type', 'integration_name')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.get_integration_type_display()}: {self.integration_name}"
    
    def get_config_value(self, key, default=None):
        """Safely get a value from config_data."""
        return self.config_data.get(key, default)
    
    def set_config_value(self, key, value):
        """Safely set a value in config_data."""
        if not isinstance(self.config_data, dict):
            self.config_data = {}
        self.config_data[key] = value
        self.save()
    
    def validate_config(self):
        """Validate integration-specific configuration."""
        if self.integration_type == 'google_sheets':
            sheet_id = self.get_config_value('sheet_id')
            if not sheet_id:
                raise ValidationError("Google Sheets integration requires a sheet_id")
        
        elif self.integration_type == 'slack':
            webhook_url = self.get_config_value('webhook_url')
            channel = self.get_config_value('channel')
            if not webhook_url and not channel:
                raise ValidationError("Slack integration requires either webhook_url or channel")
        
        elif self.integration_type == 'google_calendar':
            calendar_id = self.get_config_value('calendar_id')
            if not calendar_id:
                raise ValidationError("Google Calendar integration requires a calendar_id")
        
        elif self.integration_type == 'google_drive':
            folder_id = self.get_config_value('folder_id')
            if not folder_id:
                raise ValidationError("Google Drive integration requires a folder_id")
    
    def mark_as_used(self):
        """Update last_used_at timestamp."""
        from django.utils import timezone
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
    
    def mark_error(self, error_message):
        """Mark integration as having an error."""
        self.status = 'error'
        self.last_error = error_message
        self.save(update_fields=['status', 'last_error'])
    
    def clear_error(self):
        """Clear error status."""
        if self.status == 'error':
            self.status = 'active'
            self.last_error = None
            self.save(update_fields=['status', 'last_error'])


class IntegrationLog(models.Model):
    """
    Logs all integration activity for debugging and audit purposes.
    """
    
    ACTION_TYPES = [
        ('send_email', 'Send Email'),
        ('send_message', 'Send Message'),
        ('update_sheet', 'Update Sheet'),
        ('create_event', 'Create Calendar Event'),
        ('upload_file', 'Upload File'),
        ('webhook', 'Webhook Call'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    integration = models.ForeignKey(IntegrationConfig, on_delete=models.CASCADE, related_name='logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Request/Response data
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    
    # Error tracking
    error_message = models.TextField(blank=True, null=True)
    
    # Performance
    duration_ms = models.IntegerField(blank=True, null=True, help_text="Duration in milliseconds")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['integration', 'status']),
        ]
    
    def __str__(self):
        return f"{self.integration} - {self.action_type} ({self.status})"
