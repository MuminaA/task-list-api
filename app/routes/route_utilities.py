from flask import abort, make_response
from ..db import db

# Get a Task by ID, validate the ID, and return 404 if not found
def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        response = {"message": f"{cls.__name__} {model_id} invalid"}
        abort(make_response(response, 400))
    
    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)
    
    if not model:
        response = {"message": f"{cls.__name__} {model_id} not found"}
        abort(make_response(response, 404))
    
    return model

# Create a new Task from a dictionary (like JSON data)
def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
        
    except KeyError as error:
        response = {"details": f"Invalid data"}
        abort(make_response(response, 400))
    
    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201

def get_model_with_filters(model, filters=None, sort_by=None, sort_order=None):
    query = db.select(model)

    # Apply filters (partial match using ilike)
    if filters:
        for attr, value in filters.items():
            if value is not None:
                column = getattr(model, attr)
                query = query.where(column.ilike(f"%{value}%"))

    # Apply sorting
    sort_by = sort_by or "id"
    column = getattr(model, sort_by)
    if sort_order == "desc":
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())

    return db.session.scalars(query)