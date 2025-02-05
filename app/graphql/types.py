from graphene import ObjectType, String, List, InputObjectType, Mutation

class Scan(ObjectType):
    activity_name = String()
    activity_category = String()
    scanned_at = String()

class User(ObjectType):
    name = String()
    email = String()
    phone = String()
    badge_code = String()
    updated_at = String()
    scans = List(Scan)

    def resolve_scans(self, info):
        from app.database.models import get_user_scans
        return get_user_scans(self.email)

class UpdateUserInput(InputObjectType):
    name = String()
    phone = String() 