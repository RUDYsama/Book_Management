# Generated for Lab 9.5: JWT Authorization & RBAC
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Book_Management', '0004_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('viewer', 'Viewer'),
                    ('editor', 'Editor'),
                    ('admin', 'Admin'),
                    ('manager', 'Manager')
                ],
                default='viewer',
                max_length=20
            ),
        ),
    ]
