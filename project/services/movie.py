from typing import List

from project.dao.models import Movie
from project.exceptions import ItemNotFound
from project.services.base import BaseService


class MovieService(BaseService):

    def get_all(self, page: str = None, status: str = None) -> List[Movie]:
        """
        Получить все из БД
        """
        # Check parameter
        check_status = status == 'new'
        if not check_status:
            movies = self.dao.get_all(page, sort=False)

        # Get results
        movies = self.dao.get_all(page, sort=True)
        if not movies:
            raise ItemNotFound

        return movies
