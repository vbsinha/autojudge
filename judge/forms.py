from django import forms


class NewContestForm(forms.Form):
    contest_name = forms.CharField(
        label='Contest name', max_length=50, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the name of the contest'
        }))
    contest_start = forms.DateTimeField(
        label='Start Date', input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Enter start date of the contest'
        }))
    contest_end = forms.DateTimeField(
        label='End Date', input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Enter end date of the contest'
        }))
    penalty = forms.DecimalField(label='Penalty', widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter penalty'
    }), help_text='Value should be between 0 and 1.')
    is_public = forms.BooleanField(
        label='Is this contest public?', required=False)


class AddPersonToContestForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter email'
    }))


class DeletePersonFromContest(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.HiddenInput())
