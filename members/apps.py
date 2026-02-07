from django.apps import AppConfig


class MembersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'members'

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType

        def ensure_groups(sender, **kwargs):
            roles = ['Admin', 'Accountant', 'Teacher', 'Librarian', 'Student']
            for r in roles:
                Group.objects.get_or_create(name=r)

            # Minimal permissions (admin panel remains intact; fine-grained rules can be expanded)
            try:
                members_ct = ContentType.objects.get(app_label='members', model='member')
                view_member = Permission.objects.get(content_type=members_ct, codename='view_member')
                for name in ['Teacher', 'Accountant', 'Admin']:
                    Group.objects.get(name=name).permissions.add(view_member)
            except Exception:
                pass

        post_migrate.connect(ensure_groups, sender=self)
