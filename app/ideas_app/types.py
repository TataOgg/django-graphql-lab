import graphene


class SuccessType(graphene.Scalar):
    @staticmethod
    def serialize(success):
        return {"success": success}
