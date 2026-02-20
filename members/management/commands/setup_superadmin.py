from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from members.models import School


class Command(BaseCommand):
    help = 'Create Super Admin group and assign permissions'

    def handle(self, *args, **kwargs):
        # Create Super Admin group
        super_admin_group, created = Group.objects.get_or_create(name='Super Admin')
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created Super Admin group'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Super Admin group already exists'))
        
        # Get School content type
        school_content_type = ContentType.objects.get_for_model(School)
        
        # Add all permissions for School model
        permissions = Permission.objects.filter(content_type=school_content_type)
        super_admin_group.permissions.set(permissions)
        
        # Add additional permissions
        additional_perms = [
            'add_user', 'change_user', 'delete_user', 'view_user',
            'add_group', 'change_group', 'delete_group', 'view_group',
        ]
        
        for perm_codename in additional_perms:
            try:
                perm = Permission.objects.get(codename=perm_codename)
                super_admin_group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS(f'✅ Assigned {super_admin_group.permissions.count()} permissions to Super Admin group'))
        
        # Check if super admin user exists
        try:
            super_admin_user = User.objects.get(username='superadmin')
            if not super_admin_user.groups.filter(name='Super Admin').exists():
                super_admin_user.groups.add(super_admin_group)
                super_admin_user.is_staff = True
                super_admin_user.is_superuser = True
                super_admin_user.save()
                self.stdout.write(self.style.SUCCESS('✅ Added superadmin user to Super Admin group'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠️  superadmin user not found. Run: python manage.py createsuperuser'))
