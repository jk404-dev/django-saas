from django.core.management.base import BaseCommand
from subscriptions.models import Subscription
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Syncs permissions from subscriptions to their associated groups'

    def handle(self, *args, **options):
        # Get all active subscriptions
        qs = Subscription.objects.filter(active=True)
        self.stdout.write(self.style.SUCCESS(f'Found {qs.count()} active subscriptions'))
        
        if qs.count() == 0:
            self.stdout.write(self.style.WARNING('No active subscriptions found'))
            return

        # Get the content type for Subscription model
        content_type = ContentType.objects.get(app_label='subscriptions', model='subscription')
        
        for subscription in qs:
            self.stdout.write(self.style.SUCCESS(f'\nProcessing subscription: {subscription.name}'))
            
            # Get all groups associated with this subscription
            groups = subscription.groups.all()
            self.stdout.write(f'Found {groups.count()} groups for this subscription')
            
            for group in groups:
                self.stdout.write(f'\nProcessing group: {group.name}')
                
                # Get all permissions for this group
                current_permissions = set(group.permissions.all())
                self.stdout.write(f'Group currently has {len(current_permissions)} permissions')
                
                # Get all permissions that should be in this group based on subscription
                required_permissions = set(subscription.permissions.all())
                self.stdout.write(f'Subscription requires {len(required_permissions)} permissions')
                
                # Find permissions to add and remove
                permissions_to_add = required_permissions - current_permissions
                permissions_to_remove = current_permissions - required_permissions
                
                # Add new permissions
                if permissions_to_add:
                    self.stdout.write('\nAdding new permissions:')
                    for permission in permissions_to_add:
                        group.permissions.add(permission)
                        self.stdout.write(f'  + {permission.name}')
                
                # Remove old permissions
                if permissions_to_remove:
                    self.stdout.write('\nRemoving old permissions:')
                    for permission in permissions_to_remove:
                        group.permissions.remove(permission)
                        self.stdout.write(f'  - {permission.name}')
                
                if not permissions_to_add and not permissions_to_remove:
                    self.stdout.write('No changes needed for this group')
                
                # Save the group
                group.save()
                self.stdout.write(self.style.SUCCESS(f'Finished processing group: {group.name}'))
            
            self.stdout.write(self.style.SUCCESS(f'Finished processing subscription: {subscription.name}'))
        
        self.stdout.write(self.style.SUCCESS('\nSync completed successfully')) 

