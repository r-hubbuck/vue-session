from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('convention', '0003_registration_emergency_contact_paid_accommodation_allergy_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='conventionregistration',
            name='emergency_contact_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
