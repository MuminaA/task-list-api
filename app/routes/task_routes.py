from flask import Blueprint, request, Response
from app.models.task import Task
from app.routes.route_utilities import validate_model, create_model
from app.db import db
from datetime import datetime, timezone
import os
import requests

tasks_bp = Blueprint('tasks_bp', __name__, url_prefix='/tasks')

@tasks_bp.post('')
def create_task():
    request_body = request.get_json()
    return create_model(Task, request_body)

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
    task = validate_model(Task, task_id)

    return task.to_dict()

@tasks_bp.put('/<task_id>')
def update_one_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body['title']
    task.description = request_body['description']
    task.completed_at = request_body.get('completed_at')
    db.session.commit()

    return Response(status=204, mimetype='application/json')

@tasks_bp.delete('/<task_id>')
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()
    
    return Response(status=204, mimetype='application/json')

@tasks_bp.patch('<task_id>/mark_complete')
def mark_complete_task(task_id):
    task = validate_model(Task, task_id)
    url = 'https://slack.com/api/chat.postMessage' # Slack API endpoint

    task.completed_at = datetime.now(timezone.utc) # Mark task as completed

    db.session.commit()

    # Set headers for the Slack API request
    headers = {
        "Authorization": f"Bearer {os.environ.get('SLACK_API')}", # Slack token
        "Content-Type": "application/json" # Sending JSON data
    }

    # Prepare the data payload for Slack
    data = {
        "channel": "task-notifications", # Slack channel to post message
        "text": f"Someone just completed the task {task.title}" # Message content
    }
    
    requests.post(url, headers=headers, json=data) # Send notification to Slack

    return Response(status=204, mimetype='application/json')

@tasks_bp.patch('<task_id>/mark_incomplete')
def mark_incomplete_task(task_id):
    task= validate_model(Task, task_id)
    
    task.completed_at = None

    db.session.commit()

    return Response(status=204, mimetype='application/json')