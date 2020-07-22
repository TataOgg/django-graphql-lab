import graphene

from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations

from ideas_app.ideas.schema import IdeaQuery, IdeaMutation
from ideas_app.users.schema import FollowQuery, FollowMutation, AppUserQuery


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    update_account = mutations.UpdateAccount.Field()
    password_change = mutations.PasswordChange.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field()


class Query(AppUserQuery, UserQuery, MeQuery, FollowQuery,
            IdeaQuery, graphene.ObjectType):
    pass


class Mutation(AuthMutation, FollowMutation, IdeaMutation,
               graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

