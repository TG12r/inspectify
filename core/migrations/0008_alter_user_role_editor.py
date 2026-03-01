from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_profilepost_link_alter_profilepost_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('ADMIN', 'Administrador'), ('SEEKER', 'Profesional'), ('RECRUITER', 'Editor')],
                default='SEEKER',
                max_length=50,
            ),
        ),
    ]
