from asyncio import tasks
from flask import Blueprint
from flask import abort, make_response, request, Response
from app.models import task
from app.models.task import Task
from app.db import db

tasks_bp = Blueprint('tasks_bp', __name__, url_prefix='/tasks')

@tasks_bp.post('')
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)
    except KeyError as error:
        response = {"details": f"Invalid data"}
        abort(make_response(response, 400))
    
    db.session.add(new_task)
    db.session.commit()

    return new_task.to_dict(), 201

@tasks_bp.get('')
def get_all_tasks():
    query = db.select(Task)
    
    title_param = request.args.get('title')
    description_param = request.args.get('description')
    completed_param = request.args.get('completed_at')
    sort = request.args.get('sort')

    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))
    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))
    if completed_param:
        pass
    if sort == 'desc':
        query = query.order_by(Task.title.desc())
    elif sort == 'asc':
        query = query.order_by(Task.title.asc())
    else:
        query = query.order_by(Task.id)

    tasks = db.session.scalars(query)


    task_response = []

    for task in tasks:
        task_response.append(task.to_dict())

    return task_response

@tasks_bp.get('/<task_id>')
def get_one_task(task_id):
    task = validate_task(task_id)

    return task.to_dict()

@tasks_bp.put('/<task_id>')
def update_one_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body['title']
    task.description = request_body['description']
    task.completed_at = request_body.get('completed_at')
    db.session.commit()

    return Response(status=204, mimetype='application/json')

@tasks_bp.delete('/<task_id>')
def delete_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()
    
    return Response(status=204, mimetype='application/json')

# Get a Task by ID, validate the ID, and return 404 if not found
def validate_task(id):
        try:
            id = int(id)
        except ValueError:
            response = {'message': f'Task {id} not found'}
            abort(make_response(response, 404))

        query = db.select(Task).where(Task.id==id)
        task = db.session.scalar(query)

        if not task:
            not_found = {'message': f'Task {id} not found'}
            abort(make_response(not_found, 404))

        return task

# Create a new Task from a dictionary (like JSON data)
def create_task_from_dic(data):
    try:
        task = Task.from_dict(data)
    except KeyError as e:
        abort(make_response({'message': f'Missing field: {e.args[0]}'}, 400))

    # Save the Task to the database
    db.session.add(task)
    db.session.commit()

    return task