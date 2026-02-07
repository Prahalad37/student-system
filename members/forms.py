from datetime import date

from django import forms

from .models import Member, Expense, Notice


class FeeCollectionForm(forms.Form):
    """Form for collecting fee payments."""
    student_id = forms.IntegerField(min_value=1)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    mode = forms.CharField(max_length=50, required=True)
    date = forms.DateField(required=False)

    def clean_amount(self):
        val = self.cleaned_data.get('amount')
        if val is not None and val <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return val

    def clean_date(self):
        val = self.cleaned_data.get('date')
        return val or date.today()


class ExpenseForm(forms.ModelForm):
    """Form for adding expenses."""

    class Meta:
        model = Expense
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount', 'step': '0.01'}),
        }

    def clean_amount(self):
        val = self.cleaned_data.get('amount')
        if val is not None and val <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return val


class AddNoticeForm(forms.Form):
    """Form for adding notices."""
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    def clean_title(self):
        val = self.cleaned_data.get('title', '').strip()
        if not val:
            raise forms.ValidationError("Title is required.")
        return val

    def clean_message(self):
        val = self.cleaned_data.get('message', '').strip()
        if not val:
            raise forms.ValidationError("Message is required.")
        return val


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