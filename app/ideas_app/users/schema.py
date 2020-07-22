import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType

from ideas_app.users.models import AppUser, Follow
from ideas_app.types import SuccessType


class AppUserType(DjangoObjectType):
    class Meta:
        model = AppUser
        fields = ['username']
    user_id = graphene.String()

    def resolve_user_id(self, info):
        return self.pk


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow


class FollowQuery:
    my_followers = graphene.List(FollowType)
    my_follows = graphene.List(FollowType)
    my_pending_followers = graphene.List(FollowType)

    @login_required
    def resolve_my_followers(self, info):
        return Follow.objects.filter(user=info.context.user,
                                     approved=True)

    @login_required
    def resolve_my_follows(self, info):
        return Follow.objects.filter(follower=info.context.user,
                                     approved=True)

    @login_required
    def resolve_my_pending_followers(self, info):
        return Follow.objects.filter(user=info.context.user,
                                     approved=False)


class AppUserQuery:
    search_by_username = graphene.List(
        AppUserType, search=graphene.String())

    @login_required
    def resolve_search_by_username(self, info, search):
        return AppUser.objects.filter(username__contains=search)


class FollowUserMutation(graphene.Mutation):
    class Arguments:
        user_id = graphene.String(required=True,
                                  description="User to follow")

    follow = graphene.Field(FollowType)

    @login_required
    def mutate(self, info, user_id):
        existent_follow = Follow.objects.filter(
            user=user_id, follower=info.context.user
        )
        if not existent_follow:
            user_to_follow = AppUser.objects.get(id=user_id)
            new_follow = Follow(
                user=user_to_follow,
                follower=info.context.user
            )
            new_follow.save()
            return FollowUserMutation(follow=new_follow)
        else:
            raise GraphQLError(
                f"You already have a pending follow request "
                f"with {user_id}"
            )


class ApproveFollowerMutation(graphene.Mutation):
    class Arguments:
        follow_request_id = graphene.String(
            required=True, description="Follow request identifier"
        )
        approved = graphene.Boolean(description="Approve or reject follow")

    follow = graphene.Field(FollowType)

    @login_required
    def mutate(self, info, follow_request_id, approved):
        follow = Follow.objects.get(
            id=follow_request_id
        )
        follow.approved = approved
        follow.save()
        return ApproveFollowerMutation(follow=follow)


class UnfollowMutation(graphene.Mutation):
    class Arguments:
        user_id = graphene.String(required=True,
                                   description="User to unfollow")

    success = graphene.Field(SuccessType)

    @login_required
    def mutate(self, info, user_id):
        follow = Follow.objects.get(
            user=user_id,
            follower=info.context.user
        )
        follow.delete()
        return UnfollowMutation(success=True)


class DeleteFollowerMutation(graphene.Mutation):
    class Arguments:
        follower_id = graphene.String(
            required=True, description="Delete follower")

    success = graphene.Field(SuccessType)

    @login_required
    def mutate(self, info, follower_id):
        follow = Follow.objects.get(
            user=info.context.user,
            follower=follower_id
        )
        follow.delete()
        return UnfollowMutation(success=True)


class FollowMutation(graphene.ObjectType):
    follow_user = FollowUserMutation.Field()
    approve_follower = ApproveFollowerMutation.Field()
    unfollow_user = UnfollowMutation.Field()
    delete_follower = DeleteFollowerMutation.Field()
