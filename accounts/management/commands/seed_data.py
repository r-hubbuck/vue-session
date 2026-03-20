"""
Management command to seed reference/lookup data.

Run with:
  python manage.py seed_data                  # reference data only
  python manage.py seed_data --with-test-data # also loads test expense reports

Safe to run multiple times — uses update_or_create on natural keys.

Tables seeded (reference data):
  - state_province      (accounts app)
  - airport             (convention app)
  - convention          (convention app)
  - expense_report_type (expense_reports app)
  - booth_package       (recruiters app)
  - meal_option         (recruiters app)

Tables seeded only with --with-test-data (dev only):
  - expense_report + expense_report_detail (3 sample records)
"""

import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed reference data tables (safe to re-run)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-test-data',
            action='store_true',
            help='Also seed test expense reports and details (dev only)',
        )

    def handle(self, *args, **options):
        self.seed_groups()
        self.seed_state_provinces()
        self.seed_genders()
        self.seed_pronouns()
        self.seed_airports()
        convention = self.seed_conventions()
        self.seed_expense_report_types()
        self.seed_booth_packages(convention)
        self.seed_meal_options(convention)
        self.seed_convention_meals(convention)
        if options['with_test_data']:
            self.seed_test_expense_reports()
        self.stdout.write(self.style.SUCCESS('\nAll seed data loaded successfully.'))

    # -------------------------------------------------------------------------
    # groups (roles)
    # -------------------------------------------------------------------------
    def seed_groups(self):
        from django.contrib.auth.models import Group
        from accounts.models import ALL_ROLES

        created = 0
        for role in ALL_ROLES:
            _, c = Group.objects.get_or_create(name=role)
            if c:
                created += 1
        existing = len(ALL_ROLES) - created
        self.stdout.write(f'  groups:              {created} created, {existing} already existed')

    # -------------------------------------------------------------------------
    # state_province
    # -------------------------------------------------------------------------
    def seed_state_provinces(self):
        from accounts.models import StateProvince

        # (st_id, st_name, st_abbrev, st_strtzip, st_endzip, st_region, st_conus, st_foreign, st_ctrid)
        data = [
            (1,  'Alabama',                       'AL',  '340', '369', 'EAST SOUTH CENTRAL',  True,  False, 0),
            (2,  'Alaska',                         'AK',  '995', '999', 'PACIFIC',              True,  False, 0),
            (3,  'American Samoa',                 'AS',  '967', '967', 'OTHER USA',            False, False, 0),
            (4,  'Arizona',                        'AZ',  '850', '865', 'MOUNTAIN',             True,  False, 0),
            (5,  'Arkansas',                       'AR',  '716', '729', 'WEST SOUTH CENTRAL',   True,  False, 0),
            (6,  'California',                     'CA',  '900', '966', 'PACIFIC',              True,  False, 0),
            (7,  'Colorado',                       'CO',  '800', '816', 'MOUNTAIN',             True,  False, 0),
            (8,  'Connecticut',                    'CT',  '060', '069', 'NEW ENGLAND',          True,  False, 0),
            (9,  'Delaware',                       'DE',  '197', '199', 'SOUTH ATLANTIC',       True,  False, 0),
            (10, 'District of Columbia',           'DC',  '200', '205', 'SOUTH ATLANTIC',       True,  False, 0),
            (11, 'Federated States of Micronesia', 'FM',  '969', '969', 'OTHER USA',            False, False, 0),
            (12, 'Florida',                        'FL',  '320', '349', 'SOUTH ATLANTIC',       True,  False, 0),
            (13, 'Georgia',                        'GA',  '300', '319', 'SOUTH ATLANTIC',       True,  False, 0),
            (14, 'Guam',                           'GU',  '969', '969', 'OTHER USA',            True,  False, 0),
            (15, 'Hawaii',                         'HI',  '967', '968', 'PACIFIC',              True,  False, 0),
            (16, 'Idaho',                          'ID',  '832', '838', 'MOUNTAIN',             True,  False, 0),
            (17, 'Illinois',                       'IL',  '600', '629', 'EAST NORTH CENTRAL',   True,  False, 0),
            (18, 'Indiana',                        'IN',  '460', '479', 'EAST NORTH CENTRAL',   True,  False, 0),
            (19, 'Iowa',                           'IA',  '500', '528', 'WEST NORTH CENTRAL',   True,  False, 0),
            (20, 'Kansas',                         'KS',  '660', '679', 'WEST NORTH CENTRAL',   True,  False, 0),
            (21, 'Kentucky',                       'KY',  '400', '427', 'EAST SOUTH CENTRAL',   True,  False, 0),
            (22, 'Louisiana',                      'LA',  '700', '714', 'WEST SOUTH CENTRAL',   True,  False, 0),
            (23, 'Maine',                          'ME',  '039', '049', 'NEW ENGLAND',          True,  False, 0),
            (24, 'Marshall Islands',               'MH',  '969', '969', 'OTHER USA',            False, False, 0),
            (25, 'Maryland',                       'MD',  '206', '219', 'SOUTH ATLANTIC',       True,  False, 0),
            (26, 'Massachusetts',                  'MA',  '010', '027', 'NEW ENGLAND',          True,  False, 0),
            (27, 'Michigan',                       'MI',  '480', '499', 'EAST NORTH CENTRAL',   True,  False, 0),
            (28, 'Minnesota',                      'MN',  '550', '567', 'WEST NORTH CENTRAL',   True,  False, 0),
            (29, 'Mississippi',                    'MS',  '386', '397', 'EAST SOUTH CENTRAL',   True,  False, 0),
            (30, 'Missouri',                       'MO',  '630', '658', 'WEST NORTH CENTRAL',   True,  False, 0),
            (31, 'Montana',                        'MT',  '590', '599', 'MOUNTAIN',             True,  False, 0),
            (32, 'Nebraska',                       'NE',  '680', '693', 'WEST NORTH CENTRAL',   True,  False, 0),
            (33, 'Nevada',                         'NV',  '889', '898', 'MOUNTAIN',             True,  False, 0),
            (34, 'New Hampshire',                  'NH',  '030', '038', 'NEW ENGLAND',          True,  False, 0),
            (35, 'New Jersey',                     'NJ',  '070', '089', 'MIDDLE ATLANTIC',      True,  False, 0),
            (36, 'New Mexico',                     'NM',  '870', '884', 'MOUNTAIN',             True,  False, 0),
            (37, 'New York',                       'NY',  '004', '149', 'MIDDLE ATLANTIC',      True,  False, 0),
            (38, 'North Carolina',                 'NC',  '270', '289', 'SOUTH ATLANTIC',       True,  False, 0),
            (39, 'North Dakota',                   'ND',  '580', '588', 'WEST NORTH CENTRAL',   True,  False, 0),
            (40, 'Northern Mariana Islands',       'MP',  '969', '969', 'OTHER USA',            False, False, 0),
            (41, 'Ohio',                           'OH',  '430', '458', 'EAST NORTH CENTRAL',   True,  False, 0),
            (42, 'Oklahoma',                       'OK',  '730', '749', 'WEST SOUTH CENTRAL',   True,  False, 0),
            (43, 'Oregon',                         'OR',  '970', '979', 'PACIFIC',              True,  False, 0),
            (44, 'Palau',                          'PW',  '969', '969', 'OTHER USA',            False, False, 0),
            (45, 'Pennsylvania',                   'PA',  '150', '196', 'MIDDLE ATLANTIC',      True,  False, 0),
            (46, 'Puerto Rico',                    'PR',  '006', '009', 'OTHER USA',            True,  False, 0),
            (47, 'Rhode Island',                   'RI',  '028', '029', 'NEW ENGLAND',          True,  False, 0),
            (48, 'South Carolina',                 'SC',  '290', '299', 'SOUTH ATLANTIC',       True,  False, 0),
            (49, 'South Dakota',                   'SD',  '570', '577', 'WEST NORTH CENTRAL',   True,  False, 0),
            (50, 'Tennessee',                      'TN',  '370', '385', 'EAST SOUTH CENTRAL',   True,  False, 0),
            (51, 'Texas',                          'TX',  '750', '799', 'WEST SOUTH CENTRAL',   True,  False, 0),
            (52, 'Utah',                           'UT',  '840', '847', 'MOUNTAIN',             True,  False, 0),
            (53, 'Vermont',                        'VT',  '050', '059', 'NEW ENGLAND',          True,  False, 0),
            (54, 'Virginia',                       'VA',  '220', '246', 'SOUTH ATLANTIC',       True,  False, 0),
            (55, 'Virgin Islands',                 'VI',  '006', '009', 'OTHER USA',            False, False, 0),
            (56, 'Washington',                     'WA',  '980', '994', 'PACIFIC',              True,  False, 0),
            (57, 'West Virginia',                  'WV',  '247', '268', 'SOUTH ATLANTIC',       True,  False, 0),
            (58, 'Wisconsin',                      'WI',  '530', '549', 'EAST NORTH CENTRAL',   True,  False, 0),
            (59, 'Wyoming',                        'WY',  '820', '831', 'MOUNTAIN',             True,  False, 0),
            (65, 'Armed Forces Europe',            'AE',  '090', '098', '',                     False, False, 0),
            (66, 'Armed Forces America',           'AA',  '340', '340', '',                     False, False, 0),
            (67, 'Armed Forces Pacific',           'AP',  '962', '966', '',                     False, False, 0),
            # Canada
            (68, 'Alberta',                        'AB',  '', '', 'Canada', False, True, 19),
            (69, 'British Columbia',               'BC',  '', '', 'Canada', False, True, 19),
            (70, 'Manitoba',                       'MB',  '', '', 'Canada', False, True, 19),
            (71, 'New Brunswick',                  'NB',  '', '', 'Canada', False, True, 19),
            (72, 'Newfoundland',                   'NL',  '', '', 'Canada', False, True, 19),
            (73, 'Nova Scotia',                    'NS',  '', '', 'Canada', False, True, 19),
            (74, 'Northwest Territories',          'NT',  '', '', 'Canada', False, True, 19),
            (75, 'Nunavut',                        'NU',  '', '', 'Canada', False, True, 19),
            (76, 'Ontario',                        'ON',  '', '', 'Canada', False, True, 19),
            (77, 'Prince Edward Island',           'PE',  '', '', 'Canada', False, True, 19),
            (78, 'Quebec',                         'QC',  '', '', 'Canada', False, True, 19),
            (79, 'Saskatchewan',                   'SK',  '', '', 'Canada', False, True, 19),
            (80, 'Yukon',                          'YT',  '', '', 'Canada', False, True, 19),
            # Australia
            (81, 'New South Wales',                'NSW', '', '', 'Australia', False, True, 4),
            (82, 'Australian Capital Territory',   'ACT', '', '', 'Australia', False, True, 4),
            (83, 'Victoria',                       'VIC', '', '', 'Australia', False, True, 4),
            (84, 'Queensland',                     'QLD', '', '', 'Australia', False, True, 4),
        ]

        created = updated = 0
        for st_id, st_name, st_abbrev, st_strtzip, st_endzip, st_region, st_conus, st_foreign, st_ctrid in data:
            _, c = StateProvince.objects.update_or_create(
                st_id=st_id,
                defaults=dict(
                    st_name=st_name,
                    st_abbrev=st_abbrev,
                    st_strtzip=st_strtzip,
                    st_endzip=st_endzip,
                    st_region=st_region,
                    st_conus=st_conus,
                    st_foreign=st_foreign,
                    st_ctrid=st_ctrid,
                ),
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  state_province:      {created} created, {updated} updated')

    # -------------------------------------------------------------------------
    # gender
    # -------------------------------------------------------------------------
    def seed_genders(self):
        from accounts.models import Gender

        data = [
            (1, 'Female',     None),
            (2, 'Male',       None),
            (3, 'Non-Binary', None),
        ]

        created = updated = 0
        for pk, gender, title in data:
            _, c = Gender.objects.update_or_create(
                id=pk,
                defaults=dict(gender=gender, title=title),
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  gender:              {created} created, {updated} updated')

    # -------------------------------------------------------------------------
    # pronoun
    # -------------------------------------------------------------------------
    def seed_pronouns(self):
        from accounts.models import Pronoun

        data = [
            (1, 'Female',     None),
            (2, 'Male',       None),
            (3, 'Non-Binary', None),
        ]

        created = updated = 0
        for pk, gender, title in data:
            _, c = Pronoun.objects.update_or_create(
                id=pk,
                defaults=dict(gender=gender, title=title),
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  pronoun:             {created} created, {updated} updated')

    # -------------------------------------------------------------------------
    # airport
    # -------------------------------------------------------------------------
    def seed_airports(self):
        from convention.models import Airport

        data = [
            ('BHM', 'AL', 'Birmingham International Airport'),
            ('DHN', 'AL', 'Dothan Regional Airport'),
            ('HSV', 'AL', 'Huntsville International Airport'),
            ('MOB', 'AL', 'Mobile'),
            ('MGM', 'AL', 'Montgomery'),
            ('ANC', 'AK', 'Ted Stevens Anchorage International Airport'),
            ('FAI', 'AK', 'Fairbanks International Airport'),
            ('JNU', 'AK', 'Juneau International Airport'),
            ('FLG', 'AZ', 'Flagstaff'),
            ('PHX', 'AZ', 'Phoenix Sky Harbor International Airport'),
            ('TUS', 'AZ', 'Tucson International Airport'),
            ('YUM', 'AZ', 'Yuma International Airport'),
            ('FYV', 'AR', 'Fayetteville'),
            ('LIT', 'AR', 'Little Rock National Airport'),
            ('XNA', 'AR', 'Northwest Arkansas Regional Airport'),
            ('BUR', 'CA', 'Burbank'),
            ('FAT', 'CA', 'Fresno'),
            ('LGB', 'CA', 'Long Beach'),
            ('LAX', 'CA', 'Los Angeles International Airport'),
            ('OAK', 'CA', 'Oakland'),
            ('ONT', 'CA', 'Ontario'),
            ('PSP', 'CA', 'Palm Springs'),
            ('SMF', 'CA', 'Sacramento'),
            ('SAN', 'CA', 'San Diego International Airport'),
            ('SFO', 'CA', 'San Francisco International Airport'),
            ('SJC', 'CA', 'San Jose'),
            ('SNA', 'CA', 'Santa Ana'),
            ('ASE', 'CO', 'Aspen'),
            ('COS', 'CO', 'Colorado Springs'),
            ('DEN', 'CO', 'Denver International Airport'),
            ('GJT', 'CO', 'Grand Junction'),
            ('BDL', 'CT', 'Bradley International Airport'),
            ('IAD', 'DC', 'Washington Dulles International Airport'),
            ('DCA', 'DC', 'Washington National Airport'),
            ('PBI', 'FL', 'Palm Beach International Airport'),
            ('FLL', 'FL', 'Fort Lauderdale-Hollywood International Airport'),
            ('RSW', 'FL', 'Southwest Florida International Airport'),
            ('TPA', 'FL', 'Tampa International Airport'),
            ('MCO', 'FL', 'Orlando International Airport'),
            ('MIA', 'FL', 'Miami International Airport'),
            ('JAX', 'FL', 'Jacksonville International Airport'),
            ('ATL', 'GA', 'Hartsfield-Jackson Atlanta International Airport'),
            ('SAV', 'GA', 'Savannah'),
            ('HNL', 'HI', 'Honolulu International Airport'),
            ('LIH', 'HI', 'Lihue'),
            ('OGG', 'HI', 'Kahului'),
            ('KOA', 'HI', 'Kailua/Kona International Airport'),
            ('BOI', 'ID', 'Boise'),
            ('MDW', 'IL', 'Chicago Midway Airport'),
            ('ORD', 'IL', "Chicago O'Hare International Airport"),
            ('IND', 'IN', 'Indianapolis International Airport'),
            ('SBN', 'IN', 'South Bend Regional Airport'),
            ('DSM', 'IA', 'Des Moines International Airport'),
            ('ICT', 'KS', 'Wichita Mid-Continent Airport'),
            ('MCI', 'KS', 'Kansas City International Airport'),
            ('CVG', 'KY', 'Cincinnati/Northern Kentucky International Airport'),
            ('LEX', 'KY', 'Blue Grass Airport'),
            ('SDF', 'KY', 'Louisville International Airport'),
            ('MSY', 'LA', 'Louis Armstrong New Orleans International Airport'),
            ('BTR', 'LA', 'Baton Rouge'),
            ('PWM', 'ME', 'Portland International Jetport'),
            ('BWI', 'MD', 'Baltimore/Washington International Airport'),
            ('BOS', 'MA', 'Boston Logan International Airport'),
            ('DTW', 'MI', 'Detroit Metropolitan Wayne County Airport'),
            ('GRR', 'MI', 'Gerald R. Ford International Airport'),
            ('MSP', 'MN', 'Minneapolis-St Paul International Airport'),
            ('GPT', 'MS', 'Gulfport-Biloxi International Airport'),
            ('JAN', 'MS', 'Jackson-Evers International Airport'),
            ('STL', 'MO', 'Lambert-St. Louis International Airport'),
            ('BIL', 'MT', 'Billings Logan International Airport'),
            ('OMA', 'NE', 'Eppley Airfield'),
            ('LAS', 'NV', 'McCarran International Airport'),
            ('RNO', 'NV', 'Reno/Tahoe International Airport'),
            ('MHT', 'NH', 'Manchester-Boston Regional Airport'),
            ('EWR', 'NJ', 'Newark Liberty International Airport'),
            ('ABQ', 'NM', 'Albuquerque International Sunport'),
            ('ALB', 'NY', 'Albany International Airport'),
            ('BUF', 'NY', 'Buffalo Niagara International Airport'),
            ('ISP', 'NY', 'Long Island MacArthur Airport'),
            ('JFK', 'NY', 'John F. Kennedy International Airport'),
            ('LGA', 'NY', 'LaGuardia Airport'),
            ('ROC', 'NY', 'Greater Rochester International Airport'),
            ('SWF', 'NY', 'Stewart International Airport'),
            ('SYR', 'NY', 'Syracuse Hancock International Airport'),
            ('CLT', 'NC', 'Charlotte Douglas International Airport'),
            ('RDU', 'NC', 'Raleigh-Durham International Airport'),
            ('FAR', 'ND', 'Hector International Airport'),
            ('CLE', 'OH', 'Cleveland Hopkins International Airport'),
            ('CMH', 'OH', 'Port Columbus International Airport'),
            ('DAY', 'OH', 'James M. Cox Dayton International Airport'),
            ('OKC', 'OK', 'Will Rogers World Airport'),
            ('TUL', 'OK', 'Tulsa International Airport'),
            ('PDX', 'OR', 'Portland International Airport'),
            ('ABE', 'PA', 'Lehigh Valley International Airport'),
            ('PHL', 'PA', 'Philadelphia International Airport'),
            ('PIT', 'PA', 'Pittsburgh International Airport'),
            ('AVP', 'PA', 'Wilkes-Barre/Scranton International Airport'),
            ('PVD', 'RI', 'T. F. Green Airport'),
            ('CHS', 'SC', 'Charleston International Airport'),
            ('CAE', 'SC', 'Columbia Metropolitan Airport'),
            ('GSP', 'SC', 'Greenville-Spartanburg International Airport'),
            ('MYR', 'SC', 'Myrtle Beach International Airport'),
            ('FSD', 'SD', 'Sioux Falls Regional Airport'),
            ('BNA', 'TN', 'Nashville International Airport'),
            ('MEM', 'TN', 'Memphis International Airport'),
            ('TRI', 'TN', 'Tri-Cities Regional Airport'),
            ('TYS', 'TN', 'McGhee Tyson Airport'),
            ('AUS', 'TX', 'Austin-Bergstrom International Airport'),
            ('DAL', 'TX', 'Dallas Love Field'),
            ('DFW', 'TX', 'Dallas/Fort Worth International Airport'),
            ('ELP', 'TX', 'El Paso International Airport'),
            ('HOU', 'TX', 'Houston Hobby Airport'),
            ('IAH', 'TX', 'George Bush Intercontinental Airport'),
            ('SAT', 'TX', 'San Antonio International Airport'),
            ('SLC', 'UT', 'Salt Lake City International Airport'),
            ('BTV', 'VT', 'Burlington International Airport'),
            ('ORF', 'VA', 'Norfolk International Airport'),
            ('RIC', 'VA', 'Richmond International Airport'),
            ('SEA', 'WA', 'Seattle-Tacoma International Airport'),
            ('GEG', 'WA', 'Spokane International Airport'),
            ('CRW', 'WV', 'Yeager Airport'),
            ('GRB', 'WI', 'Austin Straubel International Airport'),
            ('MKE', 'WI', 'General Mitchell International Airport'),
            ('MSN', 'WI', 'Dane County Regional Airport'),
            ('JAC', 'WY', 'Jackson Hole Airport'),
        ]

        created = updated = 0
        for code, state, description in data:
            _, c = Airport.objects.update_or_create(
                code=code,
                defaults=dict(state=state, description=description),
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  airport:             {created} created, {updated} updated')

    # -------------------------------------------------------------------------
    # convention
    # -------------------------------------------------------------------------
    def seed_conventions(self):
        from convention.models import Convention

        obj, created = Convention.objects.update_or_create(
            pk=1,
            defaults=dict(
                name='2026 Convention',
                year=2026,
                location='Tucson, AZ',
                start_date=datetime.date(2025, 10, 16),
                end_date=datetime.date(2025, 10, 19),
                registration_open_date=datetime.date(2025, 12, 12),
                registration_close_date=datetime.date(2026, 3, 12),
                is_active=True,
            ),
        )
        self.stdout.write(f'  convention:          {"created" if created else "updated"} (id=1)')
        return obj

    # -------------------------------------------------------------------------
    # expense_report_type
    # -------------------------------------------------------------------------
    def seed_expense_report_types(self):
        from expense_reports.models import ExpenseReportType

        FULL_PAY = dict(
            is_active=True,
            mileage_rate=Decimal('0.25'),
            max_passengers=3,
            passenger_mileage_rate=Decimal('0.05'),
            max_lodging_per_night=Decimal('42.00'),
            max_breakfast_daily=Decimal('6.00'),
            max_lunch_daily=Decimal('8.00'),
            max_dinner_daily=Decimal('10.00'),
            max_breakfast_onsite=Decimal('9.00'),
            max_lunch_onsite=Decimal('15.00'),
        )

        data = [
            dict(
                report_code='A',
                report_name='Collegiate Chapter Voting Delegate, Fully Paid',
                update_board=True,
                description='Full reimbursement for collegiate chapter voting delegates',
                **FULL_PAY,
            ),
            dict(
                report_code='B',
                report_name='Non-Voting Delegate, Fully Paid',
                update_board=False,
                description='Full reimbursement for non-voting delegates',
                **FULL_PAY,
            ),
            dict(
                report_code='D',
                report_name='Alumni Chapter Voting Delegate',
                update_board=False,
                description='Reimbursement for alumni chapter voting delegates',
                **FULL_PAY,
            ),
            dict(
                report_code='E',
                report_name='Convention Awardee (Laureate, Advisor, Mentor, etc.)',
                update_board=False,
                description='Reimbursement for convention award recipients',
                **FULL_PAY,
            ),
            dict(
                report_code='F',
                report_name='Non-Voting Delegate, Air Fare Only (20%, $200 Maximum)',
                update_board=False,
                description='Air fare reimbursement only (20% of ticket, max $200)',
                is_active=True,
                mileage_rate=Decimal('0.00'),
                max_passengers=0,
                passenger_mileage_rate=Decimal('0.00'),
                max_lodging_per_night=Decimal('0.00'),
                max_breakfast_daily=Decimal('0.00'),
                max_lunch_daily=Decimal('0.00'),
                max_dinner_daily=Decimal('0.00'),
                max_breakfast_onsite=Decimal('0.00'),
                max_lunch_onsite=Decimal('0.00'),
            ),
            dict(
                report_code='G',
                report_name='Advisor, Fully Paid',
                update_board=False,
                description='Full reimbursement for chapter advisors',
                **FULL_PAY,
            ),
        ]

        created = updated = 0
        for d in data:
            code = d.pop('report_code')
            _, c = ExpenseReportType.objects.update_or_create(
                report_code=code,
                defaults=d,
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  expense_report_type: {created} created, {updated} updated')

    # -------------------------------------------------------------------------
    # booth_package
    # -------------------------------------------------------------------------
    def seed_booth_packages(self, convention):
        from recruiters.models import BoothPackage

        data = [
            dict(
                name='Silver In-Person Booth + Resume Access',
                description='In-person booth at the convention career fair with full access to attendee resumes.',
                price=Decimal('250.00'),
                is_in_person=True,
                includes_resume_access=True,
                is_active=True,
                sort_order=1,
            ),
            dict(
                name='Silver In-Person Booth',
                description='In-person booth at the convention career fair.',
                price=Decimal('200.00'),
                is_in_person=True,
                includes_resume_access=False,
                is_active=True,
                sort_order=2,
            ),
            dict(
                name='Resume Access Only',
                description='Access to attendee resumes without an in-person booth presence.',
                price=Decimal('150.00'),
                is_in_person=False,
                includes_resume_access=True,
                is_active=True,
                sort_order=3,
            ),
        ]

        created = updated = 0
        for d in data:
            name = d.pop('name')
            _, c = BoothPackage.objects.update_or_create(
                name=name,
                convention=convention,
                defaults=d,
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  booth_package:       {created} created, {updated} updated')

    # -------------------------------------------------------------------------
    # meal_option
    # -------------------------------------------------------------------------
    def seed_meal_options(self, convention):
        from recruiters.models import MealOption

        names = ['Caesar Salad', 'Turkey Wrap', 'Tomato Soup']

        created = updated = 0
        for name in names:
            _, c = MealOption.objects.update_or_create(
                name=name,
                convention=convention,
                defaults={'is_active': True},
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  meal_option:         {created} created, {updated} updated')

    # -------------------------------------------------------------------------
    # convention_meal  (guest meal options with pricing)
    # -------------------------------------------------------------------------
    def seed_convention_meals(self, convention):
        from convention.models import ConventionMeal
        from decimal import Decimal

        data = [
            dict(name='All Meals',               price=Decimal('500.00'), sort_order=1),
            dict(name='Friday Lunch',             price=Decimal('150.00'), sort_order=2),
            dict(name='Friday Banquet',           price=Decimal('200.00'), sort_order=3),
            dict(name='Saturday Awards Banquet',  price=Decimal('200.00'), sort_order=4),
        ]

        created = updated = 0
        for d in data:
            name = d.pop('name')
            _, c = ConventionMeal.objects.update_or_create(
                name=name,
                convention=convention,
                defaults={**d, 'is_active': True},
            )
            if c:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  convention_meal:     {created} created, {updated} updated')

    # -------------------------------------------------------------------------
    # test expense reports + details  (--with-test-data only)
    # -------------------------------------------------------------------------
    def seed_test_expense_reports(self):
        from django.db import transaction
        from accounts.models import User, Person, Address
        from expense_reports.models import ExpenseReportType, ExpenseReport, ExpenseReportDetail

        with transaction.atomic():
            # --- test person / user -------------------------------------------
            person, _ = Person.objects.get_or_create(
                first_name='Test',
                last_name='Member',
                defaults=dict(preferred_first_name='', middle_name=''),
            )
            user, _ = User.objects.get_or_create(
                email='testmember@tbp.org',
                defaults=dict(is_active=True),
            )
            if not user.check_password('testpass123'):
                user.set_password('testpass123')
                user.save()
            if not hasattr(user, 'person') or user.person is None:
                user.person = person
                user.save()

            # --- mailing address ----------------------------------------------
            address, _ = Address.objects.get_or_create(
                person=person,
                add_type='home',
                defaults=dict(
                    street1='123 Test St',
                    city='Tucson',
                    state='AZ',
                    zip_code='85701',
                    country='US',
                    is_primary=True,
                ),
            )

            report_type_a = ExpenseReportType.objects.get(report_code='A')
            report_type_b = ExpenseReportType.objects.get(report_code='B')
            report_type_f = ExpenseReportType.objects.get(report_code='F')

            # --- 3 sample expense reports + details ---------------------------
            reports = [
                dict(
                    report=dict(
                        person=person,
                        report_type=report_type_a,
                        chapter='Beta',
                        mailing_address=address,
                        report_date=datetime.date(2025, 10, 16),
                        status='submitted',
                        total_amount=Decimal('215.50'),
                    ),
                    detail=dict(
                        automobile_miles=Decimal('320.00'),
                        automobile_tolls=Decimal('12.50'),
                        passengers=1,
                        lodging_nights=3,
                        lodging_per_night=Decimal('42.00'),
                        breakfast_enroute=1,
                        lunch_enroute=1,
                        dinner_enroute=1,
                        breakfast_onsite=2,
                        lunch_onsite=2,
                        terminal_cost=Decimal('0.00'),
                        public_carrier_cost=Decimal('0.00'),
                        other_onsite_cost=Decimal('0.00'),
                        billed_to_hq=False,
                        expense_notes='Drove from Phoenix to Tucson for convention.',
                    ),
                ),
                dict(
                    report=dict(
                        person=person,
                        report_type=report_type_f,
                        chapter='Beta',
                        mailing_address=address,
                        report_date=datetime.date(2025, 10, 16),
                        status='approved',
                        total_amount=Decimal('180.00'),
                    ),
                    detail=dict(
                        automobile_miles=Decimal('0.00'),
                        automobile_tolls=Decimal('0.00'),
                        passengers=0,
                        lodging_nights=0,
                        lodging_per_night=Decimal('0.00'),
                        breakfast_enroute=0,
                        lunch_enroute=0,
                        dinner_enroute=0,
                        breakfast_onsite=0,
                        lunch_onsite=0,
                        terminal_cost=Decimal('30.00'),
                        public_carrier_cost=Decimal('900.00'),
                        other_onsite_cost=Decimal('0.00'),
                        billed_to_hq=False,
                        expense_notes='Airfare DFW→TUS. Reimbursement capped at 20% ($200 max).',
                    ),
                ),
                dict(
                    report=dict(
                        person=person,
                        report_type=report_type_b,
                        chapter='Beta',
                        mailing_address=address,
                        report_date=datetime.date(2025, 10, 16),
                        status='paid',
                        total_amount=Decimal('96.00'),
                        payment_method='check',
                        payment_check_number='10042',
                        payment_payer='TBP HQ',
                    ),
                    detail=dict(
                        automobile_miles=Decimal('150.00'),
                        automobile_tolls=Decimal('0.00'),
                        passengers=0,
                        lodging_nights=2,
                        lodging_per_night=Decimal('42.00'),
                        breakfast_enroute=0,
                        lunch_enroute=1,
                        dinner_enroute=1,
                        breakfast_onsite=1,
                        lunch_onsite=1,
                        terminal_cost=Decimal('0.00'),
                        public_carrier_cost=Decimal('0.00'),
                        other_onsite_cost=Decimal('5.00'),
                        billed_to_hq=False,
                        expense_notes='Non-voting delegate, partial reimbursement.',
                    ),
                ),
            ]

            created_r = created_d = 0
            for entry in reports:
                report, c = ExpenseReport.objects.get_or_create(
                    person=person,
                    report_type=entry['report']['report_type'],
                    report_date=entry['report']['report_date'],
                    defaults={k: v for k, v in entry['report'].items()
                               if k not in ('person', 'report_type', 'report_date')},
                )
                if c:
                    created_r += 1
                _, cd = ExpenseReportDetail.objects.get_or_create(
                    expense_report=report,
                    defaults=entry['detail'],
                )
                if cd:
                    created_d += 1

        self.stdout.write(
            f'  expense_report:      {created_r} created  '
            f'(test user: testmember@tbp.org / testpass123)'
        )
        self.stdout.write(f'  expense_report_detail: {created_d} created')
