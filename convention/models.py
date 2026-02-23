from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import Member  # Import Member from your accounts app


class Airport(models.Model):
    """
    US Airports for convention travel.
    """
    code = models.CharField(max_length=3, unique=True, primary_key=True)
    state = models.CharField(max_length=2, db_index=True)
    description = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'airport'
        ordering = ['state', 'description']
        indexes = [
            models.Index(fields=['state']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.description}"


class Convention(models.Model):
    """
    Represents a TBP Convention event.
    """
    name = models.CharField(max_length=200)
    year = models.IntegerField(validators=[MinValueValidator(1900)])
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    registration_open_date = models.DateField(null=True, blank=True)
    registration_close_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'convention'
        ordering = ['-year', '-start_date']
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.year})"


class ConventionRegistration(models.Model):
    """
    Represents a member's registration for a specific convention.
    Can be either a regular member registration or a guest registration.
    """
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('checked_in', 'Checked In'),
        ('waitlisted', 'Waitlisted'),
    ]

    convention = models.ForeignKey(
        Convention, 
        on_delete=models.CASCADE, 
        related_name='registrations'
    )
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='convention_registrations'
    )
    is_guest = models.BooleanField(default=False)
    host_registration = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='guests',
        help_text="Only populated if is_guest=True. References the host's registration."
    )
    status_code = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='registered'
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    credentials_received = models.BooleanField(default=False)
    credentials_received_date = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    at_convention = models.BooleanField(default=False)
    visible_to_recruiters = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'convention_registration'
        constraints = [
            models.UniqueConstraint(
                fields=['convention', 'member'],
                name='unique_convention_member'
            )
        ]
        indexes = [
            models.Index(fields=['convention', 'is_guest']),
            models.Index(fields=['host_registration']),
            models.Index(fields=['status_code']),
        ]

    def __str__(self):
        guest_str = " (Guest)" if self.is_guest else ""
        return f"{self.member} - {self.convention}{guest_str}"


class ConventionCommitteePreference(models.Model):
    """
    Committee preferences for a convention registration.
    One-to-one relationship with ConventionRegistration.
    """
    PREFERENCE_CHOICES = [
        (0, 'No Interest'),
        (1, 'Interested'),
        (2, 'Prefer'),
    ]

    registration = models.OneToOneField(
        ConventionRegistration,
        on_delete=models.CASCADE,
        related_name='committee_preferences'
    )
    
    # Committee preference fields (0=no interest, 1=interest, 2=prefer)
    alumni_affairs = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    awards = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    chapter_operations = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    collegiate_chapters = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    communications = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    constitution = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    engineering_futures = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    membership = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    public_relations = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    resolutions = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    rituals = models.IntegerField(choices=PREFERENCE_CHOICES, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            db_table = 'convention_committee_preference'

    def __str__(self):
        return f"Committee Preferences for {self.registration}"


class ConventionGuest(models.Model):
    """
    Guest information for members bringing guests.
    """
    registration = models.ForeignKey(
        ConventionRegistration,
        on_delete=models.CASCADE,
        related_name='guest_details'
    )
    guest_first_name = models.CharField(max_length=100)
    guest_last_name = models.CharField(max_length=100)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    guest_dietary_restrictions = models.TextField(blank=True)
    guest_special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'convention_guest'

    def __str__(self):
        return f"{self.guest_first_name} {self.guest_last_name} (Guest of {self.registration.member})"


class ConventionTravel(models.Model):
    """
    Travel information for a convention registration.
    One-to-one relationship with ConventionRegistration.
    """
    TRAVEL_METHOD_CHOICES = [
        ('driving', 'Driving'),
        ('self_booking', 'Booking Own Flight'),
        ('need_booking', 'Need Flight Booked'),
    ]
    
    SEAT_PREFERENCE_CHOICES = [
        ('none', 'No Preference'),
        ('window', 'Window'),
        ('aisle', 'Aisle'),
    ]

    registration = models.OneToOneField(
        ConventionRegistration,
        on_delete=models.CASCADE,
        related_name='travel'
    )
    
    travel_method = models.CharField(
        max_length=20,
        choices=TRAVEL_METHOD_CHOICES,
        default='need_booking'
    )
    
    # Flight request information (for need_booking)
    departure_airport = models.CharField(max_length=3, blank=True, help_text="3-letter airport code")
    departure_date = models.DateField(null=True, blank=True)
    departure_time_preference = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Minutes from midnight (0-1410)"
    )
    
    return_airport = models.CharField(max_length=3, blank=True, help_text="3-letter airport code")
    return_date = models.DateField(null=True, blank=True)
    return_time_preference = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minutes from midnight (0-1410)"
    )
    
    seat_preference = models.CharField(
        max_length=10,
        choices=SEAT_PREFERENCE_CHOICES,
        default='none'
    )
    
    needs_ground_transportation = models.BooleanField(
        default=True,
        help_text="Whether member needs transportation to/from convention airport"
    )
    
    # Booked flight information (staff-populated)
    outbound_airline = models.CharField(max_length=100, blank=True)
    outbound_flight_number = models.CharField(max_length=20, blank=True)
    outbound_departure_time = models.DateTimeField(null=True, blank=True)
    outbound_arrival_time = models.DateTimeField(null=True, blank=True)
    outbound_confirmation = models.CharField(max_length=50, blank=True)
    
    return_airline = models.CharField(max_length=100, blank=True)
    return_flight_number = models.CharField(max_length=20, blank=True)
    return_departure_time = models.DateTimeField(null=True, blank=True)
    return_arrival_time = models.DateTimeField(null=True, blank=True)
    return_confirmation = models.CharField(max_length=50, blank=True)
    
    flight_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'convention_travel_plan'

    def __str__(self):
        return f"Travel for {self.registration}"


class ConventionAccommodation(models.Model):
    """
    Hotel and package information for a convention registration.
    One-to-one relationship with ConventionRegistration.
    """
    PACKAGE_CHOICES = [
        ('full', 'Full Package - All meals and events'),
        ('partial', 'Partial Package - Select meals'),
        ('commuter', 'Commuter Package - No hotel'),
        ('custom', 'Custom Package'),
    ]

    ROOMMATE_PREFERENCE_CHOICES = [
        ('single', 'Single Room'),
        ('specific', 'Specific Roommate'),
        ('any', 'Any Roommate'),
    ]

    registration = models.OneToOneField(
        ConventionRegistration,
        on_delete=models.CASCADE,
        related_name='accommodation'
    )
    
    package_choice = models.CharField(
        max_length=20,
        choices=PACKAGE_CHOICES,
        default='full'
    )
    
    needs_hotel = models.BooleanField(default=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    
    roommate_preference = models.CharField(
        max_length=20,
        choices=ROOMMATE_PREFERENCE_CHOICES,
        default='any'
    )
    specific_roommate_name = models.CharField(max_length=200, blank=True)
    specific_roommate_chapter = models.CharField(max_length=100, blank=True)
    
    # Allergies and dietary restrictions
    food_allergies = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)
    other_allergies = models.TextField(blank=True)
    
    # Room assignment (staff-populated)
    room_number = models.CharField(max_length=20, blank=True)
    room_confirmation = models.CharField(max_length=50, blank=True)
    
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'convention_accomodation'

    def __str__(self):
        return f"Accommodation for {self.registration}"
