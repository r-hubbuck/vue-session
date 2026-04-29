from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_rename_curriculum_to_resumecurriculum'),
        ('recruiters', '0007_add_paid_to_recruiter_registration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruiterregistration',
            name='recruiting_majors',
            field=models.ManyToManyField(
                blank=True,
                related_name='recruiter_registrations',
                to='accounts.resumecurriculum',
            ),
        ),
    ]
