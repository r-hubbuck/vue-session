import os
import pymssql
from django.core.management.base import BaseCommand
from accounts.models import Member


class Command(BaseCommand):
    help = 'Backfill school_name on Member records that have an empty value'

    def handle(self, *args, **options):
        members = Member.objects.filter(school_name='').exclude(chapter_code='')
        if not members.exists():
            self.stdout.write('No members need backfilling.')
            return

        conn = pymssql.connect(
            server=os.getenv('SQL_PROD_HOST'),
            tds_version=r'7.0',
            user=os.getenv('SQL_USER'),
            password=os.getenv('SQL_PASSWORD'),
            database='Member',
        )
        cursor = conn.cursor(as_dict=True)

        updated = 0
        for member in members:
            cursor.execute(
                '''SELECT TOP 1 schools.sch_school
                   FROM chapters
                   INNER JOIN schools ON chapters.chp_id = schools.sch_chpid
                   WHERE RTRIM(LTRIM(chapters.chp_code)) = %s AND schools.sch_active = 1''',
                [member.chapter_code.strip()],
            )
            row = cursor.fetchone()
            if row:
                member.school_name = (row['sch_school'] or '').strip()
                member.save(update_fields=['school_name'])
                self.stdout.write(f'  {member} ({member.chapter_code.strip()}) -> {member.school_name}')
                updated += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'  No school found for chapter_code={member.chapter_code.strip()} ({member})')
                )

        conn.close()
        self.stdout.write(self.style.SUCCESS(f'Done. {updated} record(s) updated.'))
