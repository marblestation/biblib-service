"""
Functional test

Anonymous Epic

Storyboard is defined within the comments of the program itself
"""

import sys
import os

PROJECT_HOME = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_HOME)

import app
import json
import unittest
from views import USER_ID_KEYWORD, NO_PERMISSION_ERROR
from models import db
from flask import url_for
from tests.stubdata.stub_data import UserShop, LibraryShop
from tests.base import TestCaseDatabase

class TestAnonymousEpic(TestCaseDatabase):
    """
    Base class used to test the Big Share Admin Epic
    """

    def test_anonymous_epic(self):
        """
        Carries out the epic 'Anonymous', where a user tries to access a
        private library and also a public library. The user also (artificial)
        tries to access any other endpoints that do not have any scopes set

        :return: no return
        """

        # Define two sets of stub data
        # user: who makes a library (e.g., Dave the librarian)
        # anon: someone using the BBB client
        user_anonymous = UserShop()
        user_dave = UserShop()
        library_dave_private = LibraryShop(public=False)
        library_dave_public = LibraryShop(public=True)

        # Dave makes two libraries
        # One private library
        # One public library
        url = url_for('userview')
        response = self.client.post(
            url,
            data=library_dave_private.user_view_post_data_json,
            headers=user_dave.headers
        )
        library_id_private = response.json['id']
        self.assertEqual(response.status_code, 200, response)

        response = self.client.post(
            url,
            data=library_dave_public.user_view_post_data_json,
            headers=user_dave.headers
        )
        library_id_public = response.json['id']
        self.assertEqual(response.status_code, 200, response)

        # Anonymous user tries to access the private library. But cannot.
        url = url_for('libraryview', library=library_id_private)
        response = self.client.get(
            url,
            headers=user_anonymous.headers
        )
        self.assertEqual(response.status_code, NO_PERMISSION_ERROR['number'])
        self.assertEqual(response.json['error'], NO_PERMISSION_ERROR['body'])

        # Anonymous user tries to access the public library. And can.
        url = url_for('libraryview', library=library_id_public)
        response = self.client.get(
            url,
            headers=user_anonymous.headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('documents', response.json)

        number_of_scopeless = 0
        response = self.client.get('/resources')
        for end_point in response.json.keys():

            if len(response.json[end_point]['scopes']) == 0:
                number_of_scopeless += 1
                endpoint = end_point

        self.assertEqual(1, number_of_scopeless)
        self.assertEqual('/libraries/<string:library>', endpoint)

if __name__ == '__main__':
    unittest.main(verbosity=2)