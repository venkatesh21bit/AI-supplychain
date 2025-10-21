from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Creates default user groups: Manufacturer, Retailer, and Employee'

    def handle(self, *args, **kwargs):
        groups_data = [
            {
                'name': 'Manufacturer',
                'description': 'Company owners/manufacturers who manage products and orders'
            },
            {
                'name': 'Retailer',
                'description': 'Retailers who can browse products and place orders'
            },
            {
                'name': 'Employee',
                'description': 'Company employees who can manage orders and deliveries'
            }
        ]

        for group_data in groups_data:
            group, created = Group.objects.get_or_create(name=group_data['name'])
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created group: {group.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"• Group already exists: {group.name}")
                )

        self.stdout.write(
            self.style.SUCCESS('\n✓ All groups have been set up successfully!')
        )
        
        # Display all groups
        all_groups = Group.objects.all()
        self.stdout.write(self.style.SUCCESS(f'\nTotal groups in database: {all_groups.count()}'))
        for group in all_groups:
            self.stdout.write(f"  - {group.name}")
