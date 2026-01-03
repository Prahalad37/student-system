from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['firstname', 'lastname']
        
        # Bootstrap styling
        widgets = {
            'firstname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
        }