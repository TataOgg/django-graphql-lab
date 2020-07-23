import graphene
from django.db.models import Q
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType

from ideas_app.ideas.models import Idea
from ideas_app.users.models import AppUser, Follow
from ideas_app.types import SuccessType


class IdeaType(DjangoObjectType):
    class Meta:
        model = Idea


class IdeaQuery:
    my_ideas = graphene.List(IdeaType)
    user_ideas = graphene.List(IdeaType, author=graphene.String())

    @login_required
    def resolve_my_ideas(self, info):
        return info.context.user.idea_set.all().order_by('-created_on')

    @login_required
    def resolve_user_ideas(self, info, author):
        return Idea.objects.select_related('author').filter(
            Q(author_id=author)
            & (Q(visibility=Idea.VisibilityOptions.PUBLIC)
               | (Q(visibility=Idea.VisibilityOptions.PROTECTED)
                  & Q(author__follower__follower=info.context.user,
                      author__follower__approved=True)
                  )
               )
        ).distinct().order_by('-created_on')


class VisibilityArg:
    visibility = graphene.Argument(
        graphene.Enum.from_enum(
            Idea.VisibilityOptions,
            description='Idea visibility'
        )
    )


class CreationMutation(graphene.Mutation):
    class Arguments(VisibilityArg):
        text = graphene.String(required=True, description="Idea content")

    idea = graphene.Field(IdeaType)

    @login_required
    def mutate(self, info, text, visibility):
        new_idea = Idea(
            text=text,
            visibility=visibility,
            author=info.context.user
        )
        new_idea.save()
        return CreationMutation(idea=new_idea)


class ChangeVisibilityMutation(graphene.Mutation):
    class Arguments(VisibilityArg):
        idea_id = graphene.String()

    idea = graphene.Field(IdeaType)

    @login_required
    def mutate(self, info, idea_id, visibility):
        idea = Idea.objects.get(id=idea_id, author=info.context.user)
        idea.visibility = visibility
        idea.save()
        return ChangeVisibilityMutation(idea=idea)


class DeleteIdeaMutation(graphene.Mutation):
    class Arguments:
        idea_id = graphene.String()

    status = graphene.Field(SuccessType)

    @login_required
    def mutate(self, info, idea_id):
        idea = Idea.objects.get(id=idea_id, author=info.context.user)
        idea.delete()
        return DeleteIdeaMutation(success=True)


class IdeaMutation(graphene.ObjectType):
    create_idea = CreationMutation.Field()
    change_idea_visibility = ChangeVisibilityMutation.Field()
    delete_idea = DeleteIdeaMutation.Field()
