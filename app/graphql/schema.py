import graphene
from graphene import ObjectType, List, String, Field
from app.graphql.types import User, UpdateUserInput
from app.database.models import get_all_users, get_user_by_email, update_user

class Query(ObjectType):
    users = List(User)
    user = graphene.Field(User, email=String(required=True))

    def resolve_users(self, info):
        return get_all_users()
    
    def resolve_user(self, info, email):
        return get_user_by_email(email)

class UpdateUser(graphene.Mutation):
    class Arguments:
        email = String(required=True)
        data = UpdateUserInput(required=True)

    user = Field(User)

    def mutate(root, info, email, data):
        updated_user = update_user(email, data)
        return UpdateUser(user=updated_user)

class Mutation(ObjectType):
    update_user = UpdateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation) 