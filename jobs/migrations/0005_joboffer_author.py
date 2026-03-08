from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_alter_joboffer_apply_link_alter_joboffer_url'),
        ('core', '__latest__'),
    ]

    operations = [
        migrations.AddField(
            model_name='joboffer',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='job_offers', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
