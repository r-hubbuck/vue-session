from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_person_ethnicity'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Curriculum',
            new_name='ResumeCurriculum',
        ),
        migrations.AlterModelTable(
            name='resumecurriculum',
            table='resume_curriculum',
        ),
    ]
