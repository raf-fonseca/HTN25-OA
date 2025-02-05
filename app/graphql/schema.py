import graphene
from graphene import ObjectType, List
from app.graphql.types import User
from app.database.models import get_all_users

class Query(ObjectType):
    users = List(User)

    def resolve_users(self, info):
        return get_all_users()

schema = graphene.Schema(query=Query) 