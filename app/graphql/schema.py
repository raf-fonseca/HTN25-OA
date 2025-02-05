import graphene
from graphene import ObjectType, List, String
from app.graphql.types import User
from app.database.models import get_all_users, get_user_by_email

class Query(ObjectType):
    users = List(User)
    user = graphene.Field(User, email=String(required=True))

    def resolve_users(self, info):
        return get_all_users()
    
    def resolve_user(self, info, email):
        return get_user_by_email(email)

schema = graphene.Schema(query=Query) 