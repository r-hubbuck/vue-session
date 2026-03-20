from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('convention', '0005_conventionmeal_guest_allergy_dietary_meals'),
    ]

    operations = [
        # Step 1: add temp column
        migrations.AddField(
            model_name='conventionregistration',
            name='visible_to_recruiters_new',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('none', 'None'),
                    ('business', 'Businesses'),
                    ('graduate_school', 'Graduate Schools'),
                    ('both', 'Both'),
                ],
                default='both',
            ),
        ),
        # Step 2: migrate boolean data → string
        migrations.RunSQL(
            sql=(
                "UPDATE convention_registration "
                "SET visible_to_recruiters_new = CASE "
                "  WHEN visible_to_recruiters THEN 'both' "
                "  ELSE 'none' "
                "END"
            ),
            reverse_sql=(
                "UPDATE convention_registration "
                "SET visible_to_recruiters = CASE "
                "  WHEN visible_to_recruiters_new IN ('business', 'graduate_school', 'both') THEN 1 "
                "  ELSE 0 "
                "END"
            ),
        ),
        # Step 3: remove old boolean column
        migrations.RemoveField(
            model_name='conventionregistration',
            name='visible_to_recruiters',
        ),
        # Step 4: rename new column to original name
        migrations.RenameField(
            model_name='conventionregistration',
            old_name='visible_to_recruiters_new',
            new_name='visible_to_recruiters',
        ),
    ]
