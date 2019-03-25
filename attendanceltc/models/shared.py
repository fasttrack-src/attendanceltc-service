from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

def get_one_or_create(session,
                      model,
                      create_method='',
                      create_method_kwargs=None,
                      **kwargs):
    try:
        return session.query(model).filter_by(**kwargs).one(), True
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        try:
            created = getattr(model, create_method, model)(**kwargs)
            return created, False
        except IntegrityError as e:
            print(e)
            return session.query(model).filter_by(**kwargs).one(), True

db = SQLAlchemy()