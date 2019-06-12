from .shared import db
from sqlalchemy import Column, String, Integer, event

class UserIdentity(db.Model):
    __tablename__ = 'user_identity'
    username = Column(String, primary_key=True)
    type_id = Column(String, nullable=False)
    __mapper_args__ = {
        'polymorphic_on': type_id,
        'with_polymorphic': '*'
    }
# This is some magic we need to automatically update UserIdentity's identity dictionary.
@event.listens_for(UserIdentity, 'mapper_configured')
def receive_mapper_configured(mapper, class_):
    print("UPDATE!!!!!")
    print(mapper)
    print("MAP:")
    print(mapper.polymorphic_map)
    print("")
    class FallbackToParentPolymorphicMap(dict):
        def __missing__(self, key):
            # return parent UserIdentity mapper for undefined polymorphic_identity
            return mapper

    new_polymorphic_map = FallbackToParentPolymorphicMap()
    new_polymorphic_map.update(mapper.polymorphic_map)
    mapper.polymorphic_map = new_polymorphic_map

    # for prevent 'incompatible polymorphic identity' warning, not necessarily
    mapper._validate_polymorphic_identity = None