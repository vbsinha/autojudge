import datetime

from django.db import migrations, models
import django.db.models.deletion
import judge.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Unnamed Contest', max_length=50)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('penalty', models.DecimalField(decimal_places=2, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('rank', models.PositiveIntegerField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('code', models.CharField(default='UNSET', max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(default='Name not set', max_length=50)),
                ('statement', models.TextField(default='The problem statement is empty. Good luck solving it!', max_length=2500)),
                ('input_format', models.CharField(default='No input format specified. Figure it out yourself Sherlock!', max_length=1000)),
                ('output_format', models.CharField(default='No output format specified. Figure it out yourself Sherlock!', max_length=500)),
                ('difficulty', models.PositiveSmallIntegerField(default=0)),
                ('time_limit', models.DurationField(default=datetime.timedelta(seconds=10))),
                ('memory_limit', models.PositiveIntegerField(default=200000)),
                ('file_format', models.CharField(default='.py,.cpp,.c', max_length=100)),
                ('start_code', models.FileField(null=True, upload_to='content/<django.db.models.fields.CharField>/start_code.zip')),
                ('max_score', models.PositiveSmallIntegerField(default=0)),
                ('comp_script', models.FileField(default='./default/default_compilation_script.sh', upload_to='content/<django.db.models.fields.CharField>/comp_script.sh')),
                ('test_script', models.FileField(default='./default/default_test_script.sh', upload_to='content/<django.db.models.fields.CharField>/test_script.sh')),
                ('setter_solution', models.FileField(null=True, upload_to=judge.models.setter_sol_name)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_type', models.CharField(choices=[('.none', 'NOT_SELECTED'), ('.py', 'PYTHON'), ('.c', 'C'), ('.cpp', 'CPP')], default='.none', max_length=5)),
                ('submission_file', models.FileField(upload_to='content/submissions/submission_14dfec2d1f514714856ebc34935fa70c<django.db.models.fields.CharField>')),
                ('timestamp', models.DateTimeField()),
                ('judge_score', models.PositiveSmallIntegerField(default=0)),
                ('ta_score', models.PositiveSmallIntegerField(default=0)),
                ('final_score', models.FloatField(default=0.0)),
                ('linter_score', models.FloatField(default=0.0)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Person')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('public', models.BooleanField()),
                ('testcase_id', models.CharField(default='422a61340eb5425fb994cac3c21bf4bb', max_length=32, primary_key=True, serialize=False)),
                ('inputfile', models.FileField(default='./default/default_inputfile.yml', upload_to='content/testcase/inputfile_422a61340eb5425fb994cac3c21bf4bb.txt')),
                ('outputfile', models.FileField(default='./default/default_outputfile.yml', upload_to='content/testcase/outputfile_422a61340eb5425fb994cac3c21bf4bb.txt')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='SubmissionTestCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verdict', models.CharField(choices=[('P', 'Pass'), ('F', 'Fail'), ('TE', 'TLE'), ('ME', 'OOM'), ('CE', 'COMPILATION_ERROR'), ('RE', 'RUNTIME_ERROR'), ('NA', 'NOT_AVAILABLE')], default='NA', max_length=2)),
                ('memory_taken', models.PositiveIntegerField()),
                ('time_taken', models.DurationField()),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Submission')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.TestCase')),
            ],
        ),
        migrations.CreateModel(
            name='ContestProblem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Contest')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='ContestPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.BooleanField()),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Contest')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.CharField(default='3aef968e90604d6bbe48b8bab0ecf392', max_length=32, primary_key=True, serialize=False)),
                ('comment', models.FileField(default='./default/default_comment.yml', upload_to='content/comment/3aef968e90604d6bbe48b8bab0ecf392.yml')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Person')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem')),
            ],
        ),
    ]