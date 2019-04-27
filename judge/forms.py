from django import forms
from django.core.validators import RegexValidator


class NewContestForm(forms.Form):
    """
    Form for creating a new Contest.
    """
    # Contest Name
    contest_name = forms.CharField(label='Contest name', max_length=50, strip=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   help_text='Enter the name of the contest.')

    # Contest Start Timestamp
    contest_start = forms.DateTimeField(label='Start Date',
                                        widget=forms.DateTimeInput(attrs={'class': 'form-control'}),
                                        help_text='Specify when the contest begins.')

    # Contest Soft End Timestamp
    contest_soft_end = forms.DateTimeField(label='Soft End Date for contest',
                                           widget=forms.DateTimeInput(
                                            attrs={'class': 'form-control'}),
                                           help_text='Specify after when would you like to \
                                                      penalize submissions.')

    # Contest Hard End Timestamp
    contest_hard_end = forms.DateTimeField(label='Hard End Date for contest',
                                           widget=forms.DateTimeInput(
                                            attrs={'class': 'form-control'}),
                                           help_text='Specify when the contest completely ends.')

    # Contest Penalty factor
    penalty = forms.DecimalField(label='Penalty', min_value=0.0, max_value=1.0,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                 help_text='Enter a penalty factor between 0 and 1.')

    # Contest is_public property
    is_public = forms.BooleanField(label='Is this contest public?', required=False)

    def clean(self):
        cleaned_data = super().clean()
        cont_start = cleaned_data.get("contest_start")
        cont_soft_end = cleaned_data.get("contest_soft_end")
        cont_hard_end = cleaned_data.get("contest_hard_end")
        if cont_start > cont_soft_end:
            raise forms.ValidationError("Contest cannot end before it contest starts!")
        if cont_soft_end > cont_hard_end:
            raise forms.ValidationError("The final deadline cannot be before the soft deadline")


class AddPersonToContestForm(forms.Form):
    """
    Form to add a Person to a Contest.
    """
    # Email ID of the person
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control'}),
                             help_text='Enter the e-mail of the person you would like to add.')


class DeletePersonFromContest(forms.Form):
    """
    Form to remove a Person from a Contest.
    """
    # Email ID of the person
    email = forms.EmailField(label='Email', widget=forms.HiddenInput())


class NewProblemForm(forms.Form):
    """
    Form for adding a new Problem.
    """
    # Problem Code Field
    code = forms.CharField(label='Code', max_length=10, widget=forms.TextInput(
                           attrs={'class': 'form-control'}),
                           validators=[RegexValidator(r'^[a-z0-9]+$')],
                           help_text='Enter a alphanumeric code in lowercase letters as a \
                                      unique identifier for the problem.')

    # Problem Name Field
    name = forms.CharField(label='Title', max_length=50, strip=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),
                           help_text='Give a catchy problem name.')

    # Problem Statement Field
    statement = forms.CharField(label='Statement', strip=True, widget=forms.HiddenInput(),
                                help_text='Provide a descriptive statement of the problem.')

    # Problem Input Format Field
    input_format = forms.CharField(label='Input Format', strip=True, widget=forms.HiddenInput(),
                                   help_text='Give a lucid format for the input that a \
                                              participant should expect.')

    # Problem Output Format Field
    output_format = forms.CharField(label='Output Format', strip=True, widget=forms.HiddenInput(),
                                    help_text='Give a lucid format for the output that a \
                                               participant should follow.')

    # Problem Difficulty Field
    difficulty = forms.IntegerField(label='Difficulty',
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                    min_value=0, max_value=5, initial=0,
                                    help_text='Specify a difficulty level between 1 and 5 for \
                                               the problem. If this is unknown, leave it as 0.')

    # Problem Time limit
    time_limit = forms.DurationField(label='Time Limit (in seconds)',
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                     initial=0, help_text='Specify a time limit in seconds \
                                                           for the execution of the program.')

    # Problem Memory limit
    memory_limit = forms.IntegerField(label='Memory Limit (in MB)',
                                      widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                      initial=0, min_value=0,
                                      help_text='Specify a memory limit in MB for the execution \
                                                 of the program.')

    # Problem File Extensions
    file_exts = forms.CharField(label='Permitted File extensions for submissions',
                                widget=forms.TextInput(attrs={'class': 'form-control'}),
                                max_length=100, required=False,
                                validators=[RegexValidator(r'^\.[a-zA-Z0-9]+(,\.[a-zA-Z0-9]+)*$')],
                                empty_value='.py,.cpp',
                                help_text='Give a comma separated list of extensions accepted \
                                           for submissions.')

    # Problem Starting code
    starting_code = forms.FileField(label='Starting code',
                                    widget=forms.FileInput(attrs={'class': 'form-control-file'}),
                                    allow_empty_file=False, required=False,
                                    help_text='Upload some starting code to help participants \
                                               get started.')

    # Problem Max Score
    max_score = forms.IntegerField(label='Maximum score',
                                   widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   initial=10, min_value=0,
                                   help_text='Specify the maximum score that passing testcase \
                                              for this problem would award.')

    # Problem Compilation Script
    compilation_script = forms.FileField(label='Compilation script',
                                         widget=forms.FileInput(
                                          attrs={'class': 'form-control-file'}),
                                         allow_empty_file=False, required=False,
                                         help_text='Upload a custom compilation script.')

    # Problem Test Script
    testing_script = forms.FileField(label='Testing script',
                                     widget=forms.FileInput(attrs={'class': 'form-control-file'}),
                                     allow_empty_file=False, required=False,
                                     help_text='Upload a custom testing script.')


class EditProblemForm(forms.Form):
    """
    Form for editing an existing problem.
    """
    # Problem Name Field
    name = forms.CharField(label='Title', max_length=50, strip=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),
                           help_text='Give a catchy problem name.')

    # Problem Statement Field
    statement = forms.CharField(label='Statement', strip=True, widget=forms.HiddenInput(),
                                help_text='Provide a descriptive statement of the problem.')

    # Problem Input Format Field
    input_format = forms.CharField(label='Input Format', strip=True, widget=forms.HiddenInput(),
                                   help_text='Give a lucid format for the input that a \
                                              participant should expect.')

    # Problem Output Format Field
    output_format = forms.CharField(label='Output Format', strip=True, widget=forms.HiddenInput(),
                                    help_text='Give a lucid format for the output that a \
                                               participant should follow.')

    # Problem Difficulty Field
    difficulty = forms.IntegerField(label='Difficulty',
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                    initial=0, min_value=0, max_value=5,
                                    help_text='Specify a difficulty level between 1 and 5 for \
                                               the problem. If this is unknown, leave it as 0.')


class NewSubmissionForm(forms.Form):
    """
    Form to create a new Submission.
    """
    # TODO For now choices are hard coded
    # Choices of file type
    file_type = forms.ChoiceField(label='File type', choices=[
        ('.cpp', 'C++'),
        ('.c', 'C'),
        ('.py', 'Python'),
    ])

    # Submission File
    submission_file = forms.FileField(label='Choose file', required=True, allow_empty_file=False,
                                      widget=forms.FileInput(attrs={'class': 'custom-file-input'}),
                                      help_text='Upload your submission.')


class AddTestCaseForm(forms.Form):
    """
    Form to create a new TestCase
    """
    # TestCase Type
    test_type = forms.ChoiceField(label='Test type', choices=[
        ('public', 'Public'),
        ('private', 'Private')
    ])

    # TestCase Input
    input_file = forms.FileField(label='Input file', allow_empty_file=False, required=True,
                                 help_text='Upload input for test case.')

    # TestCase Output
    output_file = forms.FileField(label='Output file', allow_empty_file=False, required=True,
                                  help_text='Upload output for test case.')
