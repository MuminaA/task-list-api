from flask import Blueprint, request, Response
from .route_utilities import create_model, validate_model
from app.models.goal import Goal
from app.db import db

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