from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    """
    Form for creating and updating Member (Student) records.
    Automatically generates form fields based on the Member model.
    """
    
    class Meta:
        model = Member
        fields = '__all__'  # Include all fields (firstname, lastname, profile_pic)
        
        # Widgets to add Bootstrap classes for styling
        widgets = {
            'firstname': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter First Name'
            }),
            'lastname': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Last Name'
            }),
            'profile_pic': forms.ClearableFileInput(attrs={
                'class': 'form-control'  # Makes the file input look modern
            }),
        }