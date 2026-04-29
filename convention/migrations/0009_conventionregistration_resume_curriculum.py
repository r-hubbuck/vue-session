from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_rename_curriculum_to_resumecurriculum'),
        ('convention', '0008_guest_attending'),
    ]

    operations = [
        migrations.AddField(
            model_name='conventionregistration',
            name='resume_curriculum',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='convention_registrations',
                to='accounts.resumecurriculum',
            ),
        ),
    ]
