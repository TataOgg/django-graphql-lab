import json

from ideas_app.tests import BaseTestCase
from ideas_app.users.models import Follow

search_by_username_query = """
    query searchByUsername($search: String!){
      searchByUsername(search: $search){
        username
      }
    }
"""


class SearchTestCase(BaseTestCase):

    def test_search_by_username_results(self):
        response = self.client.execute(
            search_by_username_query,
            variables={'search': 'use'}
        )
        content = response.data['searchByUsername']
        self.assertNotEqual(len(content), 0)

    def test_search_by_username_no_results(self):
        response = self.client.execute(
            search_by_username_query,
            variables={'search': 'userrrrrrr'}
        )
        content = response.data['searchByUsername']
        self.assertEqual(len(content), 0)

    def test_search_by_username_contains_search(self):
        search = 'use'
        response = self.client.execute(
            search_by_username_query,
            variables={'search': search}
        )
        content = response.data['searchByUsername']
        for user in content:
            self.assertIn(search, user['username'])


my_followers_query = """
    query myFollowers{
      myFollowers{
        follower{
        username
        }
      }
    }
"""


class MyFollowersTestCase(BaseTestCase):
    def test_no_followers(self):
        response = self.client.execute(
            my_followers_query
        )
        content = response.data['myFollowers']
        self.assertEqual(len(content), 0)

    def test_no_followers_if_pending(self):
        follow = Follow(follower=self.extra_user,
                        user=self.logged_user,
                        approved=False)
        follow.save()

        response = self.client.execute(
            my_followers_query
        )

        content = response.data['myFollowers']
        self.assertEqual(len(content), 0)

    def test_followers_exists(self):
        follow = Follow(follower=self.extra_user,
                        user=self.logged_user,
                        approved=True)
        follow.save()

        response = self.client.execute(
            my_followers_query
        )

        content = response.data['myFollowers']
        self.assertNotEqual(len(content), 0)


my_pending_followers_query = """
    query myPendingFollowers{
      myPendingFollowers{
        follower{
        username
        }
      }
    }
"""


class MyPendingFollowersTestCase(BaseTestCase):
    def test_no_followers(self):
        response = self.client.execute(
            my_pending_followers_query
        )
        content = response.data['myPendingFollowers']
        self.assertEqual(len(content), 0)

    def test_result_if_pending(self):
        follow = Follow(follower=self.extra_user,
                        user=self.logged_user,
                        approved=False)
        follow.save()

        response = self.client.execute(
            my_pending_followers_query
        )

        content = response.data['myPendingFollowers']
        self.assertNotEqual(len(content), 0)

    def test_no_pending_followers_if_approved(self):
        follow = Follow(follower=self.extra_user,
                        user=self.logged_user,
                        approved=True)
        follow.save()

        response = self.client.execute(
            my_pending_followers_query
        )

        content = response.data['myPendingFollowers']
        self.assertEqual(len(content), 0)


my_follows_query = """
    query myFollows{
      myFollows{
        follower{
        username
        }
      }
    }
"""


class MyFollowsTestCase(BaseTestCase):
    def test_no_follows(self):
        response = self.client.execute(
            my_follows_query
        )
        content = response.data['myFollows']
        self.assertEqual(len(content), 0)

    def test_no_follows_if_pending(self):
        follow = Follow(follower=self.logged_user,
                        user=self.extra_user,
                        approved=False)
        follow.save()

        response = self.client.execute(
            my_follows_query
        )

        content = response.data['myFollows']
        self.assertEqual(len(content), 0)

    def test_follows_if_approved(self):
        follow = Follow(follower=self.logged_user,
                        user=self.extra_user,
                        approved=True)
        follow.save()

        response = self.client.execute(
            my_follows_query
        )

        content = response.data['myFollows']
        self.assertNotEqual(len(content), 0)


follow_user_mutation = """
    mutation followUser($userId:String!){
      followUser(userId:$userId){
        follow{
            approved
        }
      }
    }
"""

unfollow_user_mutation = """
    mutation unfollowUser($userId:String!){
      unfollowUser(userId:$userId){
        success
      }
    }
"""


delete_follower_mutation = """
    mutation deleteFollower($followerId:String!){
      deleteFollower(followerId:$followerId){
        success
      }
    }
"""

approve_follower_mutation = """
    mutation approveFollower($followRequestId:String!, $approved: Boolean!){
      approveFollower(followRequestId:$followRequestId, approved: $approved){
        follow{approved}
      }
    }
"""


class FollowUserTestCase(BaseTestCase):
    def test_follow_user(self):
        follow_user_id = self.extra_user.id
        self.client.execute(
            follow_user_mutation,
            variables={'userId': follow_user_id}
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.extra_user,
                follower=self.logged_user,
                approved=False).exists()
        )

    def test_cannot_follow_user_twice(self):
        follow_user_id = self.extra_user.id
        Follow.objects.create(user=self.extra_user,
                              follower=self.logged_user)
        response = self.client.execute(
            follow_user_mutation,
            variables={'userId': follow_user_id}
        )
        self.assertNotEqual(
            len(response.errors), 0
        )

    def test_unfollow_user(self):
        unfollow_user_id = self.extra_user.id
        Follow.objects.create(user=self.extra_user,
                              follower=self.logged_user)
        self.client.execute(
            unfollow_user_mutation,
            variables={'userId': unfollow_user_id}
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.extra_user,
                follower=self.logged_user,
                approved=False).exists()
        )

    def test_delete_follower(self):
        delete_follower_id = self.extra_user.id
        Follow.objects.create(user=self.logged_user,
                              follower=self.extra_user)
        result = self.client.execute(
            delete_follower_mutation,
            variables={'followerId': delete_follower_id}
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.logged_user,
                follower=self.extra_user).exists()
        )

    def test_approve_follower(self):
        follow = Follow.objects.create(user=self.logged_user,
                                       follower=self.extra_user,
                                       approved=False)
        self.client.execute(
            approve_follower_mutation,
            variables={'followRequestId': follow.id, 'approved': True}
        )
        self.assertTrue(
            Follow.objects.get(
                id=follow.id).approved
        )


