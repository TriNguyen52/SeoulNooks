from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Application(models.Model):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

    CHOICES_PRIORITY = (
        (LOW, 'Low'),
        (MEDIUM, 'Medium'), 
        (HIGH, 'High'),
    )

    priority = models.CharField(max_length=10, choices=CHOICES_PRIORITY, default=MEDIUM)

    NEW = 'new member'
    RETURNING = 'returning member'

    MEMBER_TYPE = (
        (NEW, 'new member'),
        (RETURNING, 'returning member'),
    )

    member_type = models.CharField(max_length=20, choices=MEMBER_TYPE, default=NEW)

    COUPLE = '1'
    INDIVIDUAL = '2'

    GUESTS = (
        (COUPLE, '1'),
        (INDIVIDUAL, '2'),
    )

    guests = models.CharField(max_length=2, choices=GUESTS, default=INDIVIDUAL)

    created_by = models.ForeignKey(User, related_name='applications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    question_1 = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Question 1: Please tell us about yourself and your interest in Seoul Nooks"
    )
    question_2 = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Question 2: What skills or contributions would you bring to our community?"
    )
    question_3 = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Question 3: What are your expectations for your stay?"
    )

    date_join = models.DateField(null=True, blank=True, verbose_name='Arrival Date')
    date_leave = models.DateField(null=True, blank=True, verbose_name='Departure Date')
    
    STATUS_DRAFT = 'Draft'
    STATUS_SUBMITTED = 'Submitted'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
    ]

    # Add status field
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )

    STATUS_APPROVED_INTERVIEW = 'Approved for interview'
    STATUS_SCHEDULED_INTERVIEW = 'Scheduled interview'
    STATUS_INTERVIEW_PASSED = 'Interview passed'
    STATUS_REJECTED = 'Rejected'
    STATUS_ACCEPTED = 'Accepted'
    STATUS_WAITING_LIST = 'Waiting list'

    APPLICATION_STATUS_CHOICES = [
        (STATUS_APPROVED_INTERVIEW, 'Approved for interview'),
        (STATUS_SCHEDULED_INTERVIEW, 'Scheduled interview'),
        (STATUS_INTERVIEW_PASSED, 'Interview passed'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_WAITING_LIST, 'Waiting list'),
        (STATUS_DRAFT, 'Application in progress'),
        (STATUS_SUBMITTED, 'Submitted'),
    ]

    application_status = models.CharField(
        max_length=40,
        choices=APPLICATION_STATUS_CHOICES,
        default=STATUS_DRAFT
    )

    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    is_hidden = models.BooleanField(default=False)

    def calculate_cost(self):
        if self.chapter:
            nights = (self.date_leave - self.date_join).days
            print(f"Debug - Number of nights: {nights}")
            print(f"Debug - Cost per night: {self.chapter.cost_per_night}")
            print(f"Debug - Cost per night type: {type(self.chapter.cost_per_night)}")
            # Convert nights to Decimal for proper multiplication
            nights_decimal = Decimal(str(nights))
            print(f"Debug - Nights as Decimal: {nights_decimal}")
            total_cost = self.chapter.cost_per_night * nights_decimal
            print(f"Debug - Total cost before discount: {total_cost}")
            print(f"Debug - Discount amount: {self.discount_amount}")
            # Convert discount_amount to Decimal
            discount_decimal = Decimal(str(self.discount_amount))
            final_cost = total_cost - discount_decimal
            print(f"Debug - Final cost: {final_cost}")
            return final_cost
        return Decimal('0.00')

    chapter = models.ForeignKey(
        'chapters.Chapter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.application_status}"
    
    @property
    def is_editable(self):
        return self.status == self.STATUS_DRAFT
    
    