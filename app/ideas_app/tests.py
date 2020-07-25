import json

from django.contrib.auth import get_user_model
from graphene_django.utils import GraphQLTestCase
from graphql_auth.models import UserStatus
from graphql_jwt.testcases import JSONWebTokenTestCase

from ideas_app.schema import schema
from ideas_app.users.models import AppUser

login_query = """
    mutation tokenAuth($username: String!, $password: String!){
      tokenAuth(username: $username, password: $password) {
        success,
        errors,
        token,
        user {
          id,
          username,
        }
      }
    }
"""


class BaseTestCase(GraphQLTestCase, JSONWebTokenTestCase):
    GRAPHQL_URL = '/api/'
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        logged_user_name = 'user'
        logged_user_password = 'superultrafakepassword1'
        self.logged_user = get_user_model().objects.create(
            username=logged_user_name,
            email='fake1@email.com'
        )
        self.extra_user = get_user_model().objects.create(
            username='author',
            email='fake2@email.com'
        )
        self.logged_user.set_password(logged_user_password)
        self.logged_user.save()
        user_status = UserStatus._default_manager.get(user=self.logged_user)
        user_status.verified = True
        user_status.save()

        self.client.authenticate(self.logged_user)
