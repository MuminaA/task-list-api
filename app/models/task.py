from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from typing import Optional

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    # completed_at: Mapped[Optional[datetime]] = mapped_column()
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from .goal import Goal

    # Create a new Task object from data we received in a JSON request
    @classmethod
    def from_dict(cls, data):
        title = data["title"]
        description = data["description"]

        # is_complete may or may not be in data
        is_complete = data.get("is_complete", False)

        completed_at = (
        datetime.now(timezone.utc) if is_complete else None
    )

        return cls(
            title = data['title'],
            description = data['description'],
            completed_at = data.get('completed_at'),
            goal_id=data.get("goal_id", None)
        )

    # Turn this Task object into a dictionary so we can send it as JSON in a response
    def to_dict(self, include_goal: Optional[bool] = None):
        """Return a dict representation of the Task.

        By default (include_goal is None) this will include the task's
        `goal_id` when the task belongs to a goal. Callers can override
        this by passing True/False explicitly for include_goal.
        """

        # If caller didn't specify, include goal_id when it's present on the task
        if include_goal is None:
            include_goal = self.goal_id is not None

        base = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_complete': bool(self.completed_at),
        }

        if include_goal:
            base['goal_id'] = self.goal_id

        return base


# tasks = [
#     Task(id=1, title='assignment', description='complete assignment for wave 1'),
#     Task(id=2, title='gym', description='go to the gym'),
#     Task(id=3, title='errands', description='run errands'),
#     Task(id=4, title='groceries', description='buy groceries'),
# ]


