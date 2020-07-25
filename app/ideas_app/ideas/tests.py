from ideas_app.tests import BaseTestCase
from ideas_app.users.models import Follow, AppUser
from ideas_app.ideas.models import Idea


class BaseLoggedUserWithFollowsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.follow = Follow.objects.create(
            user=self.extra_user,
            follower=self.logged_user,
            approved=True
        )


my_ideas_query = """
    query myIdeas{
      myIdeas{
        text
      }
    }
"""


class MyIdeasTestCase(BaseTestCase):

    def test_no_own_ideas(self):
        response = self.client.execute(my_ideas_query)
        content = response.data['myIdeas']
        self.assertEqual(len(content), 0)

    def test_has_own_idea(self):
        Idea.objects.create(text='hola', author=self.logged_user)
        response = self.client.execute(my_ideas_query)
        content = response.data['myIdeas']
        self.assertEqual(len(content), 1)

    def other_user_idea_not_shown(self):
        Idea.objects.create(text='hola', author=self.extra_user)
        response = self.client.execute(my_ideas_query)
        content = response.data['myIdeas']
        self.assertEqual(len(content), 0)


user_ideas_query = """
    query userIdeas($author:String!){
      userIdeas(author:$author){
        text
      }
    }
"""


class UserIdeasTestCase(BaseLoggedUserWithFollowsTestCase):

    def test_user_has_no_ideas(self):
        response = self.client.execute(user_ideas_query,
                                       {'author': self.extra_user.id})
        content = response.data['userIdeas']
        self.assertEqual(len(content), 0)

    def test_has_public_idea(self):
        Idea.objects.create(text='hola',
                            author=self.extra_user,
                            visibility=Idea.VisibilityOptions.PUBLIC)
        response = self.client.execute(user_ideas_query,
                                       {'author': self.extra_user.id})
        content = response.data['userIdeas']
        self.assertEqual(len(content), 1)

    def test_has_protected_idea_and_is_followed(self):
        Idea.objects.create(text='hola',
                            author=self.extra_user,
                            visibility=Idea.VisibilityOptions.PROTECTED)
        response = self.client.execute(user_ideas_query,
                                       {'author': self.extra_user.id})
        content = response.data['userIdeas']
        self.assertEqual(len(content), 1)

    def test_has_protected_idea_and_is_not_approved(self):
        Idea.objects.create(text='hola',
                            author=self.extra_user,
                            visibility=Idea.VisibilityOptions.PROTECTED)
        self.follow.approved = False
        self.follow.save()
        response = self.client.execute(user_ideas_query,
                                       {'author': self.extra_user.id})
        content = response.data['userIdeas']
        self.assertEqual(len(content), 0)

    def test_has_protected_idea_and_is_not_followed(self):
        Idea.objects.create(text='hola',
                            author=self.extra_user,
                            visibility=Idea.VisibilityOptions.PROTECTED)
        self.follow.delete()
        response = self.client.execute(user_ideas_query,
                                       {'author': self.extra_user.id})
        content = response.data['userIdeas']
        self.assertEqual(len(content), 0)

    def test_has_private_idea(self):
        Idea.objects.create(text='hola',
                            author=self.extra_user,
                            visibility=Idea.VisibilityOptions.PRIVATE)
        self.follow.delete()
        response = self.client.execute(user_ideas_query,
                                       {'author': self.extra_user.id})
        content = response.data['userIdeas']
        self.assertEqual(len(content), 0)


timeline_query = """
    query timeline{
      timeline{
        text
      }
    }
"""


class TimelineTestCase(BaseLoggedUserWithFollowsTestCase):

    def test_timeline_has_no_ideas(self):
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 0)

    def test_has_logged_user_private_idea(self):
        Idea.objects.create(text='hola',
                            author=self.logged_user,
                            visibility=Idea.VisibilityOptions.PRIVATE)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 1)

    def test_has_logged_user_protected_idea(self):
        Idea.objects.create(text='hola',
                            author=self.logged_user,
                            visibility=Idea.VisibilityOptions.PROTECTED)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 1)

    def test_has_logged_user_public_idea(self):
        Idea.objects.create(text='hola',
                            author=self.logged_user,
                            visibility=Idea.VisibilityOptions.PUBLIC)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 1)

    def test_has_not_follow_user_private_idea(self):
        Idea.objects.create(text='hola',
                            author=self.extra_user,
                            visibility=Idea.VisibilityOptions.PRIVATE)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 0)

    def test_has_follow_user_protected_idea(self):
        Idea.objects.create(text='hola',
                            author=self.extra_user,
                            visibility=Idea.VisibilityOptions.PROTECTED)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 1)

    def test_has_follow_user_public_idea(self):
        Idea.objects.create(text='hola',
                            author=self.extra_user,
                            visibility=Idea.VisibilityOptions.PUBLIC)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 1)

    def test_has_not_unfollowed_user_private_idea(self):
        unfollowed_user = AppUser.objects.create(username='new_user')
        Idea.objects.create(text='hola',
                            author=unfollowed_user,
                            visibility=Idea.VisibilityOptions.PRIVATE)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 0)

    def test_has_not_unfollowed_user_protected_idea(self):
        unfollowed_user = AppUser.objects.create(username='new_user')
        Idea.objects.create(text='hola',
                            author=unfollowed_user,
                            visibility=Idea.VisibilityOptions.PROTECTED)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 0)

    def test_has_not_unfollowed_user_public_idea(self):
        unfollowed_user = AppUser.objects.create(username='new_user')
        Idea.objects.create(text='hola',
                            author=unfollowed_user,
                            visibility=Idea.VisibilityOptions.PUBLIC)
        response = self.client.execute(timeline_query)
        content = response.data['timeline']
        self.assertEqual(len(content), 0)


create_idea_mutation = """
    mutation createIdea($text:String!, $visibility: VisibilityOptions!){
      createIdea(text: $text, visibility: $visibility){
        idea{text}
      }
    }
"""

delete_idea_mutation = """
    mutation deleteIdea($ideaId:String!){
      deleteIdea(ideaId: $ideaId){
        status
      }
    }
"""

change_idea_visibility_mutation = """
    mutation changeIdeaVisibility($ideaId:String!, $visibility: VisibilityOptions!){  # NOQA
      changeIdeaVisibility(ideaId: $ideaId, visibility: $visibility){
        idea{text}
      }
    }
"""


class IdeasMutationsTestCase(BaseTestCase):
    def test_create_idea(self):
        self.client.execute(create_idea_mutation,
                            variables={'text': 'TEXT',
                                       'visibility': 'PROTECTED'})
        self.assertTrue(Idea.objects.filter(text='TEXT').exists())

    def test_create_idea_author(self):
        self.client.execute(create_idea_mutation,
                            variables={'text': 'TEXT',
                                       'visibility': 'PROTECTED'})
        self.assertEqual(Idea.objects.get(text='TEXT').author,
                         self.logged_user)

    def test_delete_idea(self):
        idea = Idea.objects.create(text='text',
                                   visibility=Idea.VisibilityOptions.PROTECTED,
                                   author=self.logged_user)
        self.client.execute(delete_idea_mutation, {'ideaId': idea.id})
        self.assertFalse(Idea.objects.filter(id=idea.id).exists())

    def test_change_idea_visibility(self):
        idea = Idea.objects.create(text='text',
                                   visibility=Idea.VisibilityOptions.PROTECTED,
                                   author=self.logged_user)
        self.client.execute(change_idea_visibility_mutation,
                            {'ideaId': idea.id, 'visibility': 'PRIVATE'})
        self.assertEqual(Idea.objects.get(id=idea.id).visibility,
                         Idea.VisibilityOptions.PRIVATE)

    def test_cannot_delete_idea_from_other_author(self):
        idea = Idea.objects.create(text='text',
                                   visibility=Idea.VisibilityOptions.PROTECTED,
                                   author=self.extra_user)
        self.client.execute(delete_idea_mutation, {'ideaId': idea.id})
        self.assertTrue(Idea.objects.filter(id=idea.id).exists())

    def test_cannot_change_visibility_of_idea_from_other_author(self):
        idea = Idea.objects.create(text='text',
                                   visibility=Idea.VisibilityOptions.PROTECTED,
                                   author=self.extra_user)
        self.client.execute(change_idea_visibility_mutation,
                            {'ideaId': idea.id, 'visibility': 'PRIVATE'})
        self.assertEqual(Idea.objects.get(id=idea.id).visibility,
                         Idea.VisibilityOptions.PROTECTED)
