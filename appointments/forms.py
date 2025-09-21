from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from matplotlib import widgets
from .models import Appointment, AdminProfile

class AppointmentForm(forms.ModelForm):
    def clean_fullname(self):
        fullname = self.cleaned_data.get('fullname', '')
        if not fullname or len(fullname) < 2 or len(fullname) > 100:
            raise forms.ValidationError('Full name must be 2-100 characters.')
        return fullname

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None or age < 17 or age > 100:
            raise forms.ValidationError('Age must be between 17 and 100.')
        return age

    def clean_enroll_no(self):
        enroll_no = self.cleaned_data.get('enroll_no', '')
        if not enroll_no or len(enroll_no) < 5 or len(enroll_no) > 50:
            raise forms.ValidationError('Enrollment number must be 5-50 characters.')
        return enroll_no

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError('Phone must be exactly 10 digits.')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if not email or '@' not in email or '.' not in email:
            raise forms.ValidationError('Enter a valid email address.')
        return email
    def clean_date(self):
        import datetime
        from django.utils import timezone
        date = self.cleaned_data['date']
        now = timezone.localtime(timezone.now())
        today = now.date()
        # If after 3:00pm, only allow next day or later
        if now.hour >= 15:
            min_date = today + datetime.timedelta(days=1)
        else:
            min_date = today
        max_date = min_date + datetime.timedelta(days=90)  # 3 months
        if date < min_date:
            raise forms.ValidationError(f"You can only book from {min_date.strftime('%Y-%m-%d')} onwards.")
        if date > max_date:
            raise forms.ValidationError(f"You can only book up to {max_date.strftime('%Y-%m-%d')}.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        slot = cleaned_data.get('slot')
        if date and slot:
            # Check if slot is already occupied
            from .models import Appointment
            exists = Appointment.objects.filter(date=date, slot=slot).exists()
            if exists:
                self.add_error('slot', 'This slot is already booked for the selected date. Please choose another slot.')
        return cleaned_data
    
    class Meta:
        model = Appointment
        fields = ['fullname', 'age', 'enroll_no', 'department', 'phone', 'email', 'reason', 'date', 'slot']
        exclude = ['created_at', 'updated_at']
        widgets = {
            'fullname': forms.TextInput(attrs={
                'class': 'form-input', 'id': 'name', 'placeholder': 'Enter your full name', 'maxlength': 100, 'required': True
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-input', 'min': 17, 'max': 100, 'id': 'age', 'placeholder': '25', 'required': True
            }),
            'enroll_no': forms.TextInput(attrs={
                'class': 'form-input', 'id': 'enrollment', 'placeholder': '12345678901234', 'maxlength': 50, 'required': True
            }),
            'department': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'phone': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': '9429872313', 'pattern': '[0-9]{10}', 'maxlength': 10, 'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input', 'placeholder': 'your@email.com', 'maxlength': 254, 'required': True
            }),
            'reason': forms.RadioSelect(attrs={'class': 'checkbox-input', 'required': True}),
            'date': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Select Date', 
                'required': True,
                'data-behavior': 'show-date',
                'min': '',
            }),
            'slot': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set 'Select Department' as the default option
        choices = list(self.fields['department'].choices)
        # Remove any empty label if present
        if choices and choices[0][0] == '':
            choices = choices[1:]
        self.fields['department'].choices = [('', 'Select Department')] + choices


        slots = list(self.fields['slot'].choices)
        if slots and slots[0][0] == '':
            slots = slots[1:]
        self.fields['slot'].choices = [('', 'Select Slot')] + slots

        # Remove empty option from reason radio choices
        reason_choices = list(self.fields['reason'].choices)
        if reason_choices and reason_choices[0][0] == '':
            reason_choices = reason_choices[1:]
        self.fields['reason'].choices = reason_choices


class AdminAppointmentForm(AppointmentForm):
    class Meta(AppointmentForm.Meta):
        model = Appointment
        fields = '__all__'
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your full name'}),
            'age': forms.NumberInput(attrs={'class': 'form-input', 'min':0, 'max':100, 'placeholder': '25'}),
            'enroll_no': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '12345678901234'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '9429872313'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}),
            'reason': forms.RadioSelect(attrs={'class': 'checkbox-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'slot': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Enter remarks here...'}),
        }

    def clean_date(self):
        """Skip the date validation for admin edit form (no min/max checks)."""
        return self.cleaned_data.get('date')

    def clean(self):
        """Minimal admin clean: don't enforce date/slot uniqueness here."""
        # Use ModelForm.clean to avoid running AppointmentForm.clean()
        return forms.ModelForm.clean(self)

    def validate_unique(self):
        """Skip model-level unique_together validation for admin edits."""
        return


class AdminCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    qualification = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    image = forms.ImageField(required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-input image-upload-input'}))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'qualification', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input'})

    def save(self, commit=True):
        from django.db import transaction
        
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Create username from firstname, lastname and last 3 digits of phone
        phone = self.cleaned_data.get('phone', '')
        last_three = phone[-3:] if len(phone) >= 3 else ''
        username = f"{user.first_name.lower()}{user.last_name.lower()}{last_three}"
        # Remove any spaces and special characters
        username = ''.join(e for e in username if e.isalnum())
        user.username = username
        
        user.is_staff = True
        if commit:
            try:
                with transaction.atomic():
                    user.save()
                    AdminProfile.objects.create(
                        user=user,
                        phone=self.cleaned_data.get('phone', ''),
                        qualification=self.cleaned_data.get('qualification', ''),
                        image=self.cleaned_data.get('image'),
                    )
            except Exception as e:
                # If there's any error, make sure both operations fail
                if user.pk:
                    user.delete()
                raise e
        return user

class AdminProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = AdminProfile
        fields = ['phone', 'qualification', 'image']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
            profile.save()
        return profile
    

