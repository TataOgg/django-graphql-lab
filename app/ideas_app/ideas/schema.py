import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError
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
        return Idea.objects.filter(
            author=info.context.user
        ).order_by('-created_on')

    @login_required
    def resolve_user_ideas(self, info, author):
        available_ideas = [Idea.VisibilityOptions.PUBLIC]
        try:
            follow = Follow.objects.get(
                user=author, follower=info.context.user)
        except ObjectDoesNotExist:
            follow = None
        if follow and follow.approved:
            available_ideas.append(Idea.VisibilityOptions.PROTECTED)

        return Idea.objects.filter(
            author=author, visibility__in=available_ideas
        ).order_by('-created_on')


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
        idea = Idea.objects.get(id=idea_id)
        if idea.author == info.context.user:
            idea.visibility = visibility
            idea.save()
        else:
            raise GraphQLError("User not allowed to perform this action")

        return ChangeVisibilityMutation(idea=idea)


class DeleteIdeaMutation(graphene.Mutation):
    class Arguments:
        idea_id = graphene.String()

    status = graphene.Field(SuccessType)

    @login_required
    def mutate(self, info, idea_id):
        idea = Idea.objects.get(id=idea_id)
        if idea.author == info.context.user:
            idea.delete()
            return DeleteIdeaMutation(success=True)
        else:
            raise GraphQLError("User not allowed to perform this action")


class IdeaMutation(graphene.ObjectType):
    create_idea = CreationMutation.Field()
    change_idea_visibility = ChangeVisibilityMutation.Field()
    delete_idea = DeleteIdeaMutation.Field()
