from storageManager import StorageManager
from models import Book,User
from datetime import datetime,timedelta


class LibraryService:
    def __init__(self, storage_manager: StorageManager):
        self.storage = storage_manager


    def search(self, filters: dict):
        clean_filters = {k: v for k, v in filters.items() if v}
        if not clean_filters:
            return self.storage.get_all_books()

        results = self.storage.search_books(clean_filters)
        return results


    def borrow(self, email, book_title):
        user = self.storage.get_user_by_email(email)
        if not user:
            print(f"User {email} not found")
            return False
        if user.is_banned:
            print(f"User {email} is banned due to negative scores")
            return False
        
        book = self.storage.get_book_by_title(book_title)
        if not book:
            print(f"Book '{book_title}' not found")
            return False

        real_title = book.title  # use exact title from DB

        if self.storage.has_active_borrow(email, real_title):
            print(f"Book '{real_title}' is already borrowed by you")
            return False
        
        if book.status == "available":
            deadline = datetime.now() + timedelta(minutes=2)
            self.storage.add_borrow_record(email, real_title, deadline)
            self.storage.update_book_status(real_title, "borrowed")
            print(f"Book '{real_title}' borrowed successfully")
            return True
        else:
            if self.storage.is_in_waiting_list(email, real_title):
                print(f"You are already in the waiting list for '{real_title}'")
                return False
            self.storage.add_to_waiting_list(email, real_title)
            print(f"'{real_title}' is currently borrowed. You have been added to the waiting list")
            return True


    def return_book(self, email, book_title):
        book = self.storage.get_book_by_title(book_title)
        if not book:
            print(f"Book '{book_title}' not found")
            return False

        real_title = book.title  # use exact title from DB

        borrow_record = self.storage.get_active_borrow(email, real_title)
        if not borrow_record:
            print(f"No active borrow record found for '{real_title}'")
            return False
        
        now = datetime.now()
        deadline = borrow_record['return_deadline']

        if now > deadline:
            delay = now - deadline
            minutes_late = int(delay.total_seconds() // 60)

            if minutes_late > 0:
                print(f"Book '{real_title}' was returned {minutes_late} minutes late")
                is_banned = self.storage.update_user_score(email, minutes_late)

                if is_banned:
                    print(f"User {email} has been banned due to late return")
                    return True
            else:
                # Less than 1 minute late — still need to close the record
                pass

        self.storage.close_borrow_record(email, real_title)
        next_person = self.storage.get_next_in_waiting_list(real_title)
        if next_person:
            next_user_email = next_person['user_email']
            new_deadline = datetime.now() + timedelta(minutes=2)
            self.storage.add_borrow_record(next_user_email, real_title, new_deadline)
            self.storage.remove_from_waiting_list(next_user_email, real_title)
            print(f"Book '{real_title}' returned and assigned to the next user: {next_user_email}")
        else:
            self.storage.update_book_status(real_title, 'available')
            print(f"Book '{real_title}' returned successfully and is now available.")

        return True


    def donate(self, title, author, publisher, genre, publish_date, donor_email):
        new_book = Book(title, author, publisher, genre, publish_date, donor=donor_email)
        self.storage.add_book(new_book)
        print(f"Success: Book '{title}' was successfully donated by {donor_email}.")
        return True
        

    def get_user_borrowed_books(self, email):
        return self.storage.get_user_active_borrows(email)

    def get_online_users_count(self):
        return self.storage.report_online_users()

    def get_daily_logins(self):
        return self.storage.report_daily_logins()

    def get_negative_users(self):
        return self.storage.report_negative_scores()

    def get_popular_genres(self):
        return self.storage.report_popular_genres()

    def get_top_borrowed_books(self):
        return self.storage.report_top_books()

    def get_top_donor_info(self):
        return self.storage.report_top_donor()