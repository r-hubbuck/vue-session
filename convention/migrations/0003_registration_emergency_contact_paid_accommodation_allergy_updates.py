from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('convention', '0002_conventionregistration_confirmation_email_sent'),
    ]

    operations = [
        # --- ConventionRegistration new fields ---
        migrations.AddField(
            model_name='conventionregistration',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='conventionregistration',
            name='emergency_contact_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='conventionregistration',
            name='emergency_contact_relationship',
            field=models.CharField(blank=True, max_length=100),
        ),

        # --- ConventionAccommodation: add dietary_restrictions_other ---
        migrations.AddField(
            model_name='conventionaccommodation',
            name='dietary_restrictions_other',
            field=models.TextField(blank=True),
        ),

        # --- Data migration (SQL): preserve any existing free-form text,
        #     then set both columns to JSON empty arrays before altering types ---
        migrations.RunSQL(
            sql=[
                # Move any existing food_allergies text into other_allergies
                # (only when other_allergies is empty, to avoid overwriting)
                """
                UPDATE convention_accomodation
                SET other_allergies = food_allergies
                WHERE food_allergies != '' AND other_allergies = ''
                """,
                # Move any existing dietary_restrictions text into dietary_restrictions_other
                """
                UPDATE convention_accomodation
                SET dietary_restrictions_other = dietary_restrictions
                WHERE dietary_restrictions != '' AND dietary_restrictions_other = ''
                """,
                # Reset both columns to JSON empty arrays
                "UPDATE convention_accomodation SET food_allergies = '[]'",
                "UPDATE convention_accomodation SET dietary_restrictions = '[]'",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),

        # --- Alter food_allergies and dietary_restrictions to JSONField ---
        migrations.AlterField(
            model_name='conventionaccommodation',
            name='food_allergies',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='conventionaccommodation',
            name='dietary_restrictions',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
