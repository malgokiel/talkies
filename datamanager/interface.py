from abc import ABC, abstractmethod

class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        pass
    
    @abstractmethod
    def get_all_movies(self):
        pass

    @abstractmethod 
    def get_matching_user(self, user_login):
        pass

    @abstractmethod
    def get_matching_movies(self, find_match, user_id):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        pass

    @abstractmethod
    def add_user(self, user):
        pass

    @abstractmethod
    def add_movie(self, movie):
        pass

    @abstractmethod
    def manage_user_review(self,user_id, movie_id, review):
        pass

    @abstractmethod
    def manage_user_rating(self,user_id, movie_id, rating):
        pass

    @abstractmethod
    def add_user_movie(self, user_movie):
        pass

    @abstractmethod
    def delete_movie(self, user_id, movie_id):
        pass



    