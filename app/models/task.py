from sqlalchemy.orm import Mapped, mapped_column
from ..db import db
from datetime import datetime, timezone

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    # completed_at: Mapped[Optional[datetime]] = mapped_column()

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
            completed_at = data.get('completed_at')
        )

    # Turn this Task object into a dictionary so we can send it as JSON in a response
    def to_dict(self):

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_complete': bool(self.completed_at)
        }


# tasks = [
#     Task(id=1, title='assignment', description='complete assignment for wave 1'),
#     Task(id=2, title='gym', description='go to the gym'),
#     Task(id=3, title='errands', description='run errands'),
#     Task(id=4, title='groceries', description='buy groceries'),
# ]


