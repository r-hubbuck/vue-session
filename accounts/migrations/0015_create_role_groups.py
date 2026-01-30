from django.db import migrations

def create_role_groups(apps, schema_editor):
    """Create all TBP role groups"""
    Group = apps.get_model('auth', 'Group')
    
    roles = [
        'member',
        'alumni',
        'collegiate_officer',
        'alumni_officer',
        'district_director',
        'engineering_futures_facilitator',
        'executive_council',
        'trust_advisory_committee',
        'chapter_development_committee',
        'fellowship_board',
        'editorial_board',
        'director_alumni_affairs',
        'director_district_program',
        'director_engineering_futures',
        'director_fellowships',
        'director_rituals',
        'nest_program_lead',
        'hq_staff',
        'hq_it',
        'hq_finance',
        'hq_chapter_services',
        'hq_admin',
    ]
    
    for role_name in roles:
        Group.objects.get_or_create(name=role_name)
    
    print(f"Created {len(roles)} role groups")

def reverse_create_role_groups(apps, schema_editor):
    """Remove all TBP role groups"""
    Group = apps.get_model('auth', 'Group')
    
    roles = [
        'member',
        'alumni',
        'collegiate_officer',
        'alumni_officer',
        'district_director',
        'engineering_futures_facilitator',
        'executive_council',
        'trust_advisory_committee',
        'chapter_development_committee',
        'fellowship_board',
        'editorial_board',
        'director_alumni_affairs',
        'director_district_program',
        'director_engineering_futures',
        'director_fellowships',
        'director_rituals',
        'nest_program_lead',
        'hq_staff',
        'hq_it',
        'hq_finance',
        'hq_chapter_services',
        'hq_admin',
    ]
    
    Group.objects.filter(name__in=roles).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_remove_user_role_member_district'),  # Replace with your actual previous migration name
    ]

    operations = [
        migrations.RunPython(create_role_groups, reverse_create_role_groups),
    ]