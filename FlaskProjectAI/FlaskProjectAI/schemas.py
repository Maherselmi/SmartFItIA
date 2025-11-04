from marshmallow import Schema, fields

class CoachSchema(Schema):
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True)
    specialite = fields.Str()
    email = fields.Email(required=True)

class PlanningSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.DateTime(required=True)
    session = fields.Str(required=True)
    coach_id = fields.Int(required=True)

class PerformanceSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.DateTime()
    client_count = fields.Int(required=True)
    rating = fields.Float()
    coach_id = fields.Int(required=True)
