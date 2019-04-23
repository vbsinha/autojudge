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
    contest_soft_end = forms.DateTimeField(
        label='Soft End Date for contest', input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Enter soft end date of the contest'
        }))
    contest_hard_end = forms.DateTimeField(
        label='Hard End Date for contest', input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Enter hard end date of the contest'
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


class NewProblemForm(forms.Form):
    code = forms.CharField(label='Code', max_length=10, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    name = forms.CharField(label='Title', max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    statement = forms.CharField(label='Statement', widget=forms.HiddenInput())
    input_format = forms.CharField(
        label='Input Format', widget=forms.HiddenInput())
    output_format = forms.CharField(
        label='Output Format', widget=forms.HiddenInput())
    difficulty = forms.IntegerField(
        label='Difficulty', widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='0 - Unknown, 1 - Least, ..., 5 - Highest', initial=0)
    time_limit = forms.DurationField(
        label='Time Limit', widget=forms.NumberInput(attrs={'class': 'form-control'}),
        initial=0)
    memory_limit = forms.IntegerField(
        label='Memory Limit', widget=forms.NumberInput(attrs={'class': 'form-control'}),
        initial=0)
    file_exts = forms.CharField(
        label='File extensions', max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False, help_text='Comma separated extensions')
    starting_code = forms.FileField(label='Starting code', widget=forms.FileInput(
        attrs={'class': 'form-control-file'}), required=False)
    max_score = forms.IntegerField(
        label='Maximum score', widget=forms.NumberInput(attrs={'class': 'form-control'}),
        initial=100)
    compilation_script = forms.FileField(
        label='Compilation script', widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        required=False)
    testing_script = forms.FileField(label='Testing script', widget=forms.FileInput(
        attrs={'class': 'form-control-file'}), required=False)
    setter_soln = forms.FileField(label='Setter solution', widget=forms.FileInput(
        attrs={'class': 'form-control-file'}), required=False)


class EditProblemForm(forms.Form):
    name = forms.CharField(label='Title', max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    statement = forms.CharField(label='Statement', widget=forms.HiddenInput())
    input_format = forms.CharField(
        label='Input Format', widget=forms.HiddenInput())
    output_format = forms.CharField(
        label='Output Format', widget=forms.HiddenInput())
    difficulty = forms.IntegerField(
        label='Difficulty', widget=forms.NumberInput(attrs={'class': 'form-control'}))


class NewSubmissionForm(forms.Form):
    submission_file = forms.FileField(label='Choose file', widget=forms.FileInput(
        attrs={'class': 'form-control-file'}
    ))


class AddTestCaseForm(forms.Form):
    test_type = forms.ChoiceField(label='Test type', choices=[
        ('public', 'Public'),
        ('private', 'Private')
    ])
    input_file = forms.FileField(label='Input file')
    output_file = forms.FileField(label='Output file')
