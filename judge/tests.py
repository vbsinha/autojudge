from django.test import TestCase, utils
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from datetime import timedelta, datetime

from . import models
from . import handler

# Create your tests here.


class IndexViewTests(TestCase):
    def test_no_contests_index_view(self):
        response = self.client.get(reverse('judge:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no contests")
        self.assertQuerysetEqual(response.context['contests'], [])


class ContestProblemTests(TestCase):
    def setUp(self):
        u = User.objects.create_user(
            username='uname', email='admin@admin.org', password='1234')

        models.Person.objects.create(email=u.email)
        # models.Person.objects.create(email='testparticipant@iith.ac.in')
        poster = models.Person.objects.get(email='admin@admin.org')
        # participant = models.Person.objects.get(email='testparticipant@iith.ac.in')

        models.Contest.objects.create(name='Test Contest', start_datetime='2019-04-25T12:30',
                                      soft_end_datetime='2019-04-26T12:30',
                                      hard_end_datetime='2019-04-27T12:30',
                                      penalty=0, public=True)
        c = models.Contest.objects.get(name='Test Contest')

        models.ContestPerson.objects.create(contest=c, person=poster, role=True)

        models.Problem.objects.create(code='testprob1', contest=c, name='Test Problem 1',
                                      statement='Test Problem Statement',
                                      input_format='Test input format',
                                      output_format='Test output format',
                                      difficulty=5, time_limit=timedelta(seconds=10),
                                      memory_limit=10000)

    @utils.skipIf(True, "Not working as expected")
    def test_contest_check(self):
        u = User.objects.get(email='admin@admin.org')
        self.client.force_login(u)
        response = self.client.get(reverse('judge:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].is_authenticated, True)
        c = models.Contest.objects.get(name='Test Contest')
        contest, perm = next(response.context['contests'])
        self.assertEqual(contest.name, 'Test Contest')
        self.assertEqual(contest.public, True)
        self.assertEqual(perm, True)
        self.assertQuerysetEqual(response.context['contests'], zip([c], [False]))


class HandlerTests(TestCase):
    def test_process_and_delete_contest(self):
        status, pk = handler.process_contest(name='Test Contest', start_datetime='2019-04-25T12:30',
                                             soft_end_datetime='2019-04-26T12:30',
                                             hard_end_datetime='2019-04-27T12:30',
                                             penalty=0, public=True)
        self.assertTrue(status)
        c = models.Contest.objects.filter(pk=int(pk))
        self.assertEqual(len(c), 1)
        c = c[0]
        self.assertEqual(c.name, 'Test Contest')
        self.assertEqual(c.start_datetime, datetime(2019, 4, 25, 12, 30, tzinfo=timezone.utc))
        self.assertEqual(c.soft_end_datetime, datetime(2019, 4, 26, 12, 30, tzinfo=timezone.utc))
        self.assertEqual(c.hard_end_datetime, datetime(2019, 4, 27, 12, 30, tzinfo=timezone.utc))
        self.assertEqual(c.penalty, 0)
        self.assertTrue(c.public)
        status, err = handler.delete_contest(contest=int(pk))
        self.assertTrue(status)
        self.assertIsNone(err)
        c = models.Contest.objects.filter(pk=int(pk))
        self.assertEqual(len(c), 0)

    def test_process_update_and_delete_problem(self):
        c = models.Contest.objects.create(name='Test Contest', start_datetime='2019-04-25T12:30',
                                          soft_end_datetime='2019-04-26T12:30',
                                          hard_end_datetime='2019-04-27T12:30',
                                          penalty=0, public=True)
        status, msg = handler.process_problem(
            code='testprob1', contest=c.pk, name='Test Problem 1',
            statement='Test Problem Statement',
            input_format='Test input format',
            output_format='Test output format', difficulty=5,
            time_limit=timedelta(seconds=10),
            memory_limit=10000, file_format='.py', start_code=None,
            max_score=4, compilation_script=None, test_script=None,
            setter_solution=None)
        self.assertTrue(status)
        self.assertIsNone(msg)
        p = models.Problem.objects.filter(pk='testprob1')
        self.assertEqual(len(p), 1)
        p = p[0]
        self.assertEqual(p.code, 'testprob1')
        self.assertEqual(p.name, 'Test Problem 1')
        self.assertEqual(p.statement, 'Test Problem Statement')
        self.assertEqual(p.input_format, 'Test input format')
        self.assertEqual(p.output_format, 'Test output format')
        self.assertEqual(p.difficulty, 5)
        self.assertEqual(p.time_limit, timedelta(seconds=10))
        self.assertEqual(p.memory_limit, 10000)
        self.assertEqual(p.file_format, '.py')
        self.assertEqual(p.max_score, 4)
        status, msg = handler.update_problem(code=p.code, name='Updated Test Problem 1',
                                             statement='Updated Test Problem Statement',
                                             input_format='Updated Test input format',
                                             output_format='Updated Test output format',
                                             difficulty=4)
        self.assertTrue(status)
        p = models.Problem.objects.filter(pk='testprob1')
        self.assertEqual(len(p), 1)
        p = p[0]
        self.assertEqual(p.code, 'testprob1')
        self.assertEqual(p.name, 'Updated Test Problem 1')
        self.assertEqual(p.statement, 'Updated Test Problem Statement')
        self.assertEqual(p.input_format, 'Updated Test input format')
        self.assertEqual(p.output_format, 'Updated Test output format')
        self.assertEqual(p.difficulty, 4)
        status, err = handler.delete_problem(problem='testprob1')
        self.assertTrue(status)
        self.assertIsNone(err)
        p = models.Problem.objects.filter(pk='testprob1')
        self.assertEqual(len(p), 0)

    def test_process_person(self):
        person = models.Person.objects.create(email='testing1@test.com', rank=0)
        status, message = handler.process_person(person.email, 1)
        self.assertTrue(status)
        self.assertIsNone(message)
        all_persons = models.Person.objects.all()
        self.assertEqual(len(all_persons), 1)
        one_person = all_persons[0]
        self.assertEqual(one_person.email, 'testing1@test.com')
        self.assertEqual(one_person.rank, 0)
        status, message = handler.process_person('testing2@test.com', rank=1)
        self.assertTrue(status)
        self.assertIsNone(message)
        all_persons = models.Person.objects.filter(email='testing2@test.com')
        self.assertEqual(len(all_persons), 1)
        one_person = all_persons[0]
        self.assertEqual(one_person.email, 'testing2@test.com')
        self.assertEqual(one_person.rank, 1)
