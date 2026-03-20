from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('convention', '0004_conventionregistration_emergency_contact_phone'),
    ]

    operations = [
        # --- Create ConventionMeal table ---
        migrations.CreateModel(
            name='ConventionMeal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('convention', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='meals',
                    to='convention.convention',
                )),
            ],
            options={
                'db_table': 'convention_meal',
                'ordering': ['sort_order', 'name'],
            },
        ),

        # --- ConventionGuest: add new non-destructive fields first ---
        migrations.AddField(
            model_name='conventionguest',
            name='guest_food_allergies',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='conventionguest',
            name='guest_food_allergies_other',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='conventionguest',
            name='guest_dietary_restrictions_other',
            field=models.TextField(blank=True),
        ),

        # --- Data migration: convert any existing free-form dietary text to
        #     the new _other field before changing the column type ---
        migrations.RunSQL(
            sql=[
                """
                UPDATE convention_guest
                SET guest_dietary_restrictions_other = guest_dietary_restrictions
                WHERE guest_dietary_restrictions != '' AND guest_dietary_restrictions_other = ''
                """,
                "UPDATE convention_guest SET guest_dietary_restrictions = '[]'",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),

        # --- Alter guest_dietary_restrictions from TextField to JSONField ---
        migrations.AlterField(
            model_name='conventionguest',
            name='guest_dietary_restrictions',
            field=models.JSONField(blank=True, default=list),
        ),

        # --- Add M2M relationship between ConventionGuest and ConventionMeal ---
        migrations.AddField(
            model_name='conventionguest',
            name='guest_meals',
            field=models.ManyToManyField(
                blank=True,
                related_name='guests',
                to='convention.conventionmeal',
            ),
        ),
    ]
