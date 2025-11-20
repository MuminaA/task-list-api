from flask import Blueprint, request, Response
from app.models.task import Task
from app.routes.route_utilities import validate_model, create_model, get_model_with_filters
from app.db import db
from datetime import datetime, timezone
import os
import requests

bp = Blueprint('tasks_bp', __name__, url_prefix='/tasks')

@bp.post('')
def create_task():
    request_body = request.get_json()
    return create_model(Task, request_body)

@bp.get('')
def get_all_tasks():
    title_param = request.args.get('title')
    description_param = request.args.get('description')
    sort = request.args.get('sort')

    filters = {
        "title": title_param,
        "description": description_param
    }

    sort_by = "title" if sort in ["asc", "desc"] else "id"
    sort_order = sort if sort in ["asc", "desc"] else "asc"

    tasks = get_model_with_filters(Task, filters=filters, sort_by=sort_by, sort_order=sort_order)

    return [task.to_dict() for task in tasks]

@bp.get('/<task_id>')
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return task.to_dict()

@bp.put('/<task_id>')
def update_one_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body['title']
    task.description = request_body['description']
    task.completed_at = request_body.get('completed_at')
    db.session.commit()

    return Response(status=204, mimetype='application/json')

@bp.delete('/<task_id>')
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()
    
    return Response(status=204, mimetype='application/json')

@bp.patch('/<task_id>/mark_complete')
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

@bp.patch('/<task_id>/mark_incomplete')
def mark_incomplete_task(task_id):
    task = validate_model(Task, task_id)
    
    task.completed_at = None

    db.session.commit()

    return Response(status=204, mimetype='application/json')