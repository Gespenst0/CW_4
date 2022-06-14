from typing import List

from flask import current_app
from sqlalchemy import desc
from sqlalchemy.orm.scoping import scoped_session


class BaseDAO:

    def __init__(self, session: scoped_session, model):

        self.session = session
        self.model = model

    def get_one(self, uid: int) -> object:
        """Получить объект по его айдишнику"""
        item = self.session.query(self.model).get(uid)
        return item

    def get_all(self, page: str = None, sort: bool = False) -> List[object]:
        """Получить все объекты из БД"""

        items = self.session.query(self.model)

        if sort:
            items = items.order_by(desc(self.model.year))
        if page:
            items = items\
                .limit(current_app.config.get('ITEMS_PER_PAGE'))\
                .offset(page * current_app.config.get('ITEMS_PER_PAGE') - current_app.config.get('ITEMS_PER_PAGE'))

        return items.all()
