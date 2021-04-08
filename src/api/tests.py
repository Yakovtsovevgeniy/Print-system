from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Plotter, Pattern


class TestAPI(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser('joe', 'joe@doe.com', 'doe')
        self.user2 = get_user_model().objects.create_user('joe2', 'joe@doe.com', 'doe')

        # self.client.login(username='joe', password='doe')

    def test_user_CRUD(self):
        # Unauthorized check
        url = reverse('api:user-list')
        data = {
            "username": "evgen",
            "password": "1234",
            "parent": 2,
            "administrator": False,
            "dealer": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, msg=response.data)
        # SuperUser create admin
        self.client.login(username='joe', password='doe')
        data = {
            "username": "admin",
            "password": "1234",
            "parent": 2,
            "administrator": True,
            "dealer": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        # SuperUser create dealer
        data_2 = {
            "username": "dealer",
            "password": "1234",
            "parent": 2,
            "administrator": False,
            "dealer": True
        }
        response = self.client.post(url, data_2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        # SuperUser create user
        data = {
            "username": "evgen",
            "password": "1234",
            "parent": 2,
            "administrator": False,
            "dealer": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()
        # Admin create admin
        self.client.login(username='admin', password='1234')
        data = {
            "username": "admin2",
            "password": "1234",
            "parent": 4,
            "administrator": True,
            "dealer": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        response = self.client.get(url, format='json')

        len_resp = len(response.data)
        numb_us = get_user_model().objects.all().count()
        len_resp == numb_us
        len(response.data) == get_user_model().objects.all().count()

        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.client.logout()
        # Dealer create child_user
        self.client.login(username='dealer', password='1234')
        data_3 = {
            "username": "dealers_user",
            "password": "1234",
            "parent": 5,
            "administrator": False,
            "dealer": False
        }
        response = self.client.post(url, data_3, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)

        response = self.client.get(url, format='json')

        len_resp = len(response.data)
        numb_us = get_user_model().objects.all().count()
        len_resp == numb_us
        len(response.data) == get_user_model().objects.all().count()

        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        # Dealer can't create no_parent_user

        data_4 = {
            "username": "no_parent_user",
            "password": "1234",
            "parent": 4,
            "administrator": False,
            "dealer": False
        }
        response = self.client.post(url, data_4, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)

        # Dealer delete/update child user
        url = reverse('api:user-detail', kwargs={
            'pk': get_user_model().objects.filter(username=data_3['username']).values_list('pk', flat=True)[0]})

        data_3_upd = {
            "username": "dealers_user_upd"
        }
        response = self.client.patch(url, data_3_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Dealer can't delete/update admin user
        url = reverse('api:user-detail', kwargs={
            'pk': get_user_model().objects.filter(username=data['username']).values_list('pk', flat=True)[0]})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.logout()
        # Admin update/delete dealer
        self.client.login(username='admin2', password='1234')
        url = reverse('api:user-detail', kwargs={
            'pk': get_user_model().objects.filter(username=data_2['username']).values_list('pk', flat=True)[0]})
        data_3_upd = {
            "username": "dealer_upd"
        }
        response = self.client.patch(url, data_3_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()
        # User create users
        self.client.login(username='evgen', password='1234')
        url = reverse('api:user-list')
        data_5 = {
            "username": "users_user",
            "password": "1234",
            "parent": 3,
            "administrator": False,
            "dealer": False
        }
        response = self.client.post(url, data_5, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(url, format='json')

        len_resp = len(response.data)
        numb_us = get_user_model().objects.all().count()
        len_resp == numb_us
        len(response.data) == get_user_model().objects.all().count()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        # User can't update/delete users
        url = reverse('api:user-detail', kwargs={
            'pk': get_user_model().objects.filter(username=data['username']).values_list('pk', flat=True)[0]})
        data_3_upd = {
            "username": "dealer_upd"
        }
        response = self.client.patch(url, data_3_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, msg=response.data)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)

    def test_plotter_CRUD(self):
        # Creation of admin and dealer user
        self.client.login(username='joe', password='doe')
        url = reverse('api:user-list')
        data = {
            "username": "admin",
            "password": "1234",
            "parent": 2,
            "administrator": True,
            "dealer": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        data_2 = {
            "username": "dealer",
            "password": "1234",
            "parent": 2,
            "administrator": False,
            "dealer": True
        }
        response = self.client.post(url, data_2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        self.client.logout()
        # Unauthorized user can't create plotter
        url = reverse('api:plotter-list')
        data = {
            "title": "plotter",
            "creator": 'null',
            "users": []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, msg=response.data)
        # SuperUser create plotter
        self.client.login(username='joe', password='doe')
        data1 = {
            "title": "plotter",
            "creator": 2,
            "users": []
        }
        response = self.client.post(url, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        self.client.logout()
        # Admin create/update/delete plotter
        self.client.login(username='admin', password='1234')
        data2 = {
            "title": "plotter2",
            "creator": 4,
            "users": []
        }
        response = self.client.post(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        url2 = reverse('api:plotter-detail',
                       kwargs={'pk': Plotter.objects.filter(title=data2['title']).values('pk')[0]['pk']})
        data2u = {
            "title": "plotter3_upd",
            "users": [3]
        }
        response = self.client.patch(url2, data2u, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        response = self.client.delete(url2, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg=response.data)
        self.client.logout()
        # Dealer can create/update plotter
        self.client.login(username='dealer', password='1234')
        data3 = {
            "title": "plotter3",
            "creator": 5,
            "users": []
        }
        response = self.client.post(url, data3, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        url2 = reverse('api:plotter-detail',
                       kwargs={'pk': Plotter.objects.filter(title=data3['title']).values('pk')[0]['pk']})
        data3u = {
            "title": "plotter3_upd",
            "users": [3]
        }
        response = self.client.patch(url2, data3u, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        # can't delete
        response = self.client.delete(url2, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        # creator must be current user
        data = {
            "title": "plotter3",
            "creator": 4,
            "users": []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)
        self.client.logout()
        # User can't create/update/delete plotter
        self.client.login(username='joe2', password='doe')
        data = {
            "title": "plotter4",
            "creator": 3,
            "users": []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, msg=response.data)

    def test_pattern_CRUD(self):
        # creation of admin, dealer and user
        self.client.login(username='joe', password='doe')
        url = reverse('api:user-list')
        data_admin = {
            "username": "admin",
            "password": "1234",
            "parent": 2,
            "administrator": True,
            "dealer": False
        }
        response = self.client.post(url, data_admin, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        data_dealer = {
            "username": "dealer",
            "password": "1234",
            "parent": 2,
            "administrator": False,
            "dealer": True
        }
        response = self.client.post(url, data_dealer, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        data_3 = {
            "username": "1234",
            "password": "1234",
            "parent": 2,
            "administrator": False,
            "dealer": False
        }
        response = self.client.post(url, data_3, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        response = self.client.get(url, format='json')
        len_resp = len(response.data)
        numb_us = get_user_model().objects.all().count()
        len_resp == numb_us
        len(response.data) == get_user_model().objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.client.logout()
        # Admin CRUD patterns
        self.client.login(username='admin', password='1234')
        url = reverse('api:pattern-list')
        data = {
            "title": "admin pattern",
            "allowed_amount": 322,
            "user": 3
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        data2 = {
            "title": "admin pattern2",
            "allowed_amount": 322,
            "user": 3
        }
        response = self.client.post(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        url_upd = reverse('api:pattern-detail',
                          kwargs={'pk': Pattern.objects.filter(title=data2['title']).values('pk')[0]['pk']})
        data_upd = {
            "title": "admin pattern upd",
            "allowed_amount": 412,
            'user': 2
        }
        response = self.client.patch(url_upd, data_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        data_upd = {
            "title": "admin pattern upd",
            "allowed_amount": 412
        }
        response = self.client.patch(url_upd, data_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        response = self.client.delete(url_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg=response.data)
        self.client.logout()
        # Dealer has no perms for CRUD patterns
        self.client.login(username='dealer', password='1234')
        data_d = {
            "title": "admin pattern",
            "allowed_amount": 322,
            "user": 3
        }
        response = self.client.post(url, data_d, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        url_upd2 = reverse('api:pattern-detail',
                           kwargs={'pk': Pattern.objects.filter(title=data['title']).values('pk')[0]['pk']})
        data_upd = {
            "title": "pattern upd",
            "allowed_amount": 412
        }
        response = self.client.patch(url_upd2, data_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        response = self.client.delete(url_upd, format='json')
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, msg=response.data)
        self.client.logout()
        # User CRUD patterns
        self.client.login(username='1234', password='1234')
        data_u = {
            "title": "user2 pattern",
            "allowed_amount": 322,
            "user": 2
        }
        response = self.client.post(url, data_u, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        url_upd3 = reverse('api:pattern-detail',
                           kwargs={'pk': Pattern.objects.filter(title=data['title']).values('pk')[0]['pk']})
        data_upd = {
            "title": "pattern upd",
            "allowed_amount": 412
        }
        response = self.client.patch(url_upd3, data_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        response = self.client.delete(url_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)

    def test_plotterpattern_CRUD(self):
        # creation of admin, dealer and user
        self.client.login(username='joe', password='doe')
        url = reverse('api:user-list')
        data_admin = {
            "username": "admin",
            "password": "1234",
            "parent": 2,
            "administrator": True,
            "dealer": False
        }
        response = self.client.post(url, data_admin, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        data_dealer = {
            "username": "dealer",
            "password": "1234",
            "parent": 2,
            "administrator": False,
            "dealer": True
        }
        response = self.client.post(url, data_dealer, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        data_3 = {
            "username": "1234",
            "password": "1234",
            "parent": 2,
            "administrator": False,
            "dealer": False
        }
        response = self.client.post(url, data_3, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        # creation of pattern for test
        url = reverse('api:pattern-list')
        data = {
            "title": "admin pattern",
            "allowed_amount": 322,
            "user": 6
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        # creation of plotter for test
        url = reverse('api:plotter-list')
        data1 = {
            "title": "plotter",
            "creator": 2,
            "users": [6]
        }
        response = self.client.post(url, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        self.client.logout()
        # dealer can't create plotterpattern
        self.client.login(username='dealer', password='1234')
        url = reverse('api:plotter_pattern-list')
        data_pp = {
            "stats": 0,
            "plotter": 2,
            "pattern": 1
        }
        response = self.client.post(url, data_pp, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        # Admin create plotterpattern
        self.client.login(username='admin', password='1234')
        url = reverse('api:plotter_pattern-list')
        data_pp = {
            "stats": 0,
            "plotter": 1,
            "pattern": 1
        }
        response = self.client.post(url, data_pp, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        # Admin update plotterpattern
        url_detail = reverse('api:plotter_pattern-detail', kwargs={'pk': 1})
        data_pp_upd = {
            "stats": 4
        }
        response = self.client.patch(url_detail, data_pp_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.client.logout()
        # dealer can't update/delete
        self.client.login(username='dealer', password='1234')
        url_detail = reverse('api:plotter_pattern-detail', kwargs={'pk': 1})
        data_pp_upd = {
            "stats": 20
        }
        response = self.client.patch(url_detail, data_pp_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, msg=response.data)
        response = self.client.delete(url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        self.client.logout()
        # user can't create/delete plotterpattern
        self.client.login(username='1234', password='1234')
        data_plot_user = {
            "title": "plotter2",
            "creator": 6,
            "users": [6]
        }
        response = self.client.post(url, data_plot_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        # user can put a number of prints
        url_detail = reverse('api:plotter_pattern-detail', kwargs={'pk': 1})
        data_pp_upd = {
            "stats": 20
        }
        response = self.client.patch(url_detail, data_pp_upd, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        response = self.client.delete(url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        self.client.logout()
        # Admin delete plotterpattern
        self.client.login(username='admin', password='1234')
        url_detail = reverse('api:plotter_pattern-detail', kwargs={'pk': 1})
        response = self.client.delete(url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg=response.data)
