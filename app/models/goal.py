from sqlalchemy.orm import Mapped, mapped_column
from ..db import db

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]

    @classmethod
    def from_dict(cls, data):
        
        return cls(
            title = data['title'],
        )

    def to_dict(self):

        return {
            'id': self.id,
            'title': self.title,
        }
