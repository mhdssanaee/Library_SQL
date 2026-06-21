class User:
    def __init__(self, first_name, last_name, email, password, negative_score=0, is_banned=False, last_login=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.negative_score = negative_score
        self.is_banned = is_banned
        self.last_login = last_login


class Book:
    def __init__(self, title, author, publisher, genre, publish_date, status="available",donor=None):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.genre = genre
        self.publish_date = publish_date
        self.status = status
        self.donor = donor
