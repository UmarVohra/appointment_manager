from django.db import models
from django.contrib.auth.models import User

# Placeholder for appointments app models
class Appointment(models.Model):
	STATUS_CHOICES = [
		('completed', 'Completed'),
		('pending', 'Pending')
	]

	REASON_CHOICES = [
		('personal', 'Personal'),
		('professional', 'Professional'),
		('other', 'Other')
	]
	SLOT_CHOICES = [
		('11:00-12:00', '11:00 AM - 12:00 PM'),
		('12:00-1:00', '12:00 PM - 1:00 PM'),
		('1:00-2:00', '1:00 PM - 2:00 PM'),
		('2:00-3:00', '2:00 PM - 3:00 PM')
	]
	DEPARTMENT_CHOICES = [
    # Computers & Science
    ("bca", "BCA – General"),
    ("bsc_applied", "B.Sc – Applied Sciences (Chem/Microbio/Biotech)"),

    # Commerce & Business
    ("bcom_ifma", "B.Com (Int. Finance & Mgmt. Accounting)"),
    ("bcom", "B.Com – General"),
    ("bba", "BBA – General"),
    ("bba_sports", "BBA – Sports Mgmt."),
    ("bba_event", "BBA – Event Mgmt."),

    # Engineering & Law
    ("be", "B.E – Engineering"),
    ("llb", "LLB – Law (General)"),
    ("gnm", "GNM – Nursing & Midwifery"),

    # Masters
    ("mba", "MBA – General"),
    ("mca", "MCA – General"),
    ("msc_it_cyber", "MSc-IT – Cyber Security"),
    ("msc_applied", "MSc – Applied Sciences (Chem/Microbio/Biotech/MLT)"),
    ("m_media_comm", "Media & Communication (Masters)"),
    ("m_design", "Design (Masters)"),
    ("m_planning", "Planning (Masters)"),
    ("mpharm", "M.Pharm – Pharmacy"),
    ("mpt", "MPT – Physiotherapy"),
    ("me", "M.E – Engineering"),

    # Diplomas & Integrated Programs
    ("diploma_engineering", "Diploma Engineering"),
    ("integrated_bachelors", "Integrated Bachelor’s (10th + B.Com/BBA/BCA)"),
    ("radio_programming", "Radio Programming"),
    ("medical_lab_tech", "Medical Lab Technology"),
    ("vedic_foretelling", "Vedic Foretelling"),
    ("holistic_early_ed", "Holistic Early Childhood Ed."),
    ("integrated_mba", "Integrated MBA (BBA → MBA)"),
    ("integrated_mca", "Integrated MCA (BCA → MCA)"),
    ("integrated_msc_it", "Integrated MSc-IT (BSc-IT → MSc-IT)"),
    ("integrated_llb", "Integrated LLB (BBA + LLB)"),
    ("integrated_mba_entre", "Integrated MBA – Entrepreneurship & Family Business"),

    # Media & Design
    ("b_media_comm", "Media & Communication (Bachelors)"),
    ("b_design", "Design (Bachelors)"),


    # Health Sciences
    ("bsc_nursing", "B.Sc – Nursing"),
    ("bpt", "BPT – Physiotherapy"),
    ("b_arch", "B.Arch – Architecture"),
    ("bpharm", "B.Pharm – Pharmacy"),


    # Doctorate
    ("phd", "PhD – Doctorate"),
]

	fullname = models.CharField(max_length=100)
	age = models.IntegerField()
	enroll_no = models.CharField(max_length=50)
	department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
	phone = models.CharField(max_length=15)
	email = models.EmailField()
	reason = models.CharField(max_length=15, choices=REASON_CHOICES)
	date = models.DateField()
	slot = models.CharField(max_length=20, choices=SLOT_CHOICES)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
	remarks = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']
		db_table = 'appointments'
	
class AdminProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	phone = models.CharField(max_length=15)
	qualification = models.CharField(max_length=100)
	image = models.ImageField(upload_to='admin_profiles/', blank=True, null=True)
	is_doctor = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.user.get_full_name() or self.user.username}'s Profile"
