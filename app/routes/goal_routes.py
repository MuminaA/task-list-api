from flask import Blueprint, request, Response
from .route_utilities import create_model, validate_model
from app.models.goal import Goal
from app.db import db
from app.models.task import Task

goals_bp = Blueprint('goal_bp', __name__, url_prefix='/goals')

@goals_bp.post('')
def create_goal():
    request_body = request.get_json()
    return create_model(Goal, request_body)

@goals_bp.get('')
def get_all_goals():
    query = db.select(Goal)

    query = query.order_by(Goal.id)

    goals = db.session.scalars(query)

    goal_response = []

    for goal in goals:
        goal_response.append(goal.to_dict())

    return goal_response

@goals_bp.get("/<goal_id>")
def get_goal_by_id(goal_id):
    goal = validate_model(Goal, goal_id)
    return goal.to_dict()

@goals_bp.put('/<goal_id>')
def update_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body['title']

    db.session.commit()

    return Response(status=204, mimetype='application/json')

@goals_bp.delete('/<goal_id>')
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype='application/json')

@goals_bp.post('/<goal_id>/tasks')
def create_task_with_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    # Get the list of task IDs from the request body
    task_ids = request_body.get("task_ids")

    if not task_ids or not isinstance(task_ids, list):
        return {"details": "Invalid data"}, 400

    # remove all current tasks from this goal
    for task in goal.tasks:
        task.goal_id = None

    # For each task ID, find the task and associate it with the goal
    for task_id in task_ids:
        task = validate_model(Task, task_id)
        task.goal_id = goal.id

    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": task_ids
    }, 200

@goals_bp.get('/<goal_id>/tasks')
def get_task_with_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    # convert each task into a JSON-friendly dict
    tasks = [task.to_dict() for task in goal.tasks]

    response = goal.to_dict()
    response["tasks"] = tasks

    return response
