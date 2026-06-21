import psycopg2
from psycopg2.extras import RealDictCursor
from models import User, Book
from datetime import datetime,timedelta


class StorageManager:
    def __init__(self):
        self.params = {
            "dbname": "library_db",
            "user": "xxxx",
            "password": "xxxx",
            "host": "localhost"
        }

    def _get_connection(self):
        return psycopg2.connect(**self.params)

    # USER
    
    def get_user_by_email(self, email): # auth.register / auth.login_user / libraryService.borrow
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email.lower(),))
                row = cur.fetchone()
                return User(**dict(row)) if row else None

    def add_user(self, user: User): # auth.register
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                sql = """INSERT INTO users (first_name, last_name, email, password) 
                         VALUES (%s, %s, %s, %s)"""
                cur.execute(sql, (user.first_name, user.last_name, user.email, user.password))
            conn.commit()

    def update_user_status(self, email, negative_score, is_banned, last_login): # auth.login_user
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                sql = """UPDATE users SET negative_score = %s, is_banned = %s, last_login = %s 
                         WHERE email = %s"""
                cur.execute(sql, (negative_score, is_banned, last_login, email.lower()))
            conn.commit()

    def update_user_score(self, email, score_to_add): # libraryService.return_book
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    UPDATE users 
                    SET negative_score = negative_score + %s,
                        is_banned = CASE WHEN (negative_score + %s) >= 10 THEN TRUE ELSE FALSE END
                    WHERE email = %s
                    RETURNING is_banned;
                """, (score_to_add, score_to_add, email.lower()))
                
                result = cur.fetchone()
                if not result or not result['is_banned']:
                    conn.commit()
                    return False

                cur.execute("""
                    UPDATE borrows SET status = 'returned', returned_at = NOW() 
                    WHERE user_email = %s AND status = 'active'
                    RETURNING book_title;
                """, (email.lower(),))
                revoked_books = cur.fetchall()

                for record in revoked_books:
                    title = record['book_title']
                    
                    cur.execute("""
                        SELECT user_email FROM waiting_lists 
                        WHERE book_title = %s ORDER BY joined_at ASC LIMIT 1
                    """, (title,))
                    next_person = cur.fetchone()

                    if next_person:
                        next_user = next_person['user_email']
                        
                        # Check if the next person in waiting list is banned
                        cur.execute("SELECT is_banned FROM users WHERE email = %s", (next_user,))
                        next_user_status = cur.fetchone()
                        if next_user_status and next_user_status['is_banned']:
                            # Remove banned user from waiting list and make book available
                            cur.execute("DELETE FROM waiting_lists WHERE user_email = %s AND book_title = %s",
                                       (next_user, title))
                            cur.execute("UPDATE books SET status = 'available' WHERE title = %s", (title,))
                        else:
                            deadline = datetime.now() + timedelta(minutes=2)
                            cur.execute("""
                                INSERT INTO borrows (user_email, book_title, return_deadline) 
                                VALUES (%s, %s, %s)
                            """, (next_user, title, deadline))
                            cur.execute("DELETE FROM waiting_lists WHERE user_email = %s AND book_title = %s", 
                                       (next_user, title))
                    else:
                        # No one waiting
                        cur.execute("UPDATE books SET status = 'available' WHERE title = %s", (title,))
                
                conn.commit()
                return True


    # BOOK

    def get_book_by_title(self, title): # libraryService.borrow / libraryService.return_book
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM books WHERE LOWER(title) = LOWER(%s)", (title,))
                row = cur.fetchone()
                return Book(**dict(row)) if row else None

    def add_book(self, book: Book): # libraryService.donate
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                sql = """INSERT INTO books (title, author, publisher, genre, publish_date, status, donor) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cur.execute(sql, (book.title, book.author, book.publisher, book.genre, 
                                  book.publish_date, book.status, book.donor))
            conn.commit()

    def update_book_status(self, title, status): # libraryService.borrow / libraryService.return_book
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE books SET status = %s WHERE title = %s", (status, title))
            conn.commit()


    def get_all_books(self): # libraryService.search
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM books ORDER BY title ASC")
                rows = cur.fetchall()
                return [Book(**dict(row)) for row in rows]
            

    def search_books(self, filters): # libraryService.search
        ALLOWED_COLUMNS = {"title", "author", "publisher", "genre", "status"}
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM books WHERE 1=1"
                params = []
                for key, value in filters.items():
                    if key not in ALLOWED_COLUMNS:
                        continue
                    if value:
                        if key == "status":
                            query += f" AND {key} = %s"
                            params.append(value.lower())
                        else:
                            query += f" AND {key} ILIKE %s"
                            params.append(f"%{value}%")
                
                cur.execute(query, tuple(params))
                rows = cur.fetchall()
                return [Book(**dict(row)) for row in rows]
            
            

    # BORROW and WAITING_LIST

    def add_borrow_record(self, email, title, deadline): # libraryService.borrow / libraryService.return_book
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                sql = """INSERT INTO borrows (user_email, book_title, return_deadline) 
                         VALUES (%s, %s, %s)"""
                cur.execute(sql, (email.lower(), title, deadline))
            conn.commit()

    def close_borrow_record(self, email, title): # libraryService.return_book
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                sql = """UPDATE borrows SET returned_at = NOW(), status = 'returned' 
                         WHERE user_email = %s AND book_title = %s AND status = 'active'"""
                cur.execute(sql, (email.lower(), title))
            conn.commit()

    def add_to_waiting_list(self, email, title): # libraryService.borrow
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                sql = "INSERT INTO waiting_lists (user_email, book_title) VALUES (%s, %s)"
                cur.execute(sql, (email.lower(), title))
            conn.commit()

    def has_active_borrow(self, email, title): # libraryService.borrow
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM borrows 
                        WHERE user_email = %s AND book_title = %s AND status = 'active'
                    )
                """, (email.lower(), title))
                return cur.fetchone()[0]

    def is_in_waiting_list(self, email, title): # libraryService.borrow
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM waiting_lists 
                        WHERE user_email = %s AND book_title = %s
                    )
                """, (email.lower(), title))
                return cur.fetchone()[0]
            


    def get_active_borrow(self, email, title): # libraryService.return_book
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM borrows 
                    WHERE user_email = %s AND book_title = %s AND status = 'active'
                """, (email.lower(), title))
                return cur.fetchone()

    def get_next_in_waiting_list(self, title): # libraryService.return_book
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM waiting_lists 
                    WHERE book_title = %s 
                    ORDER BY joined_at ASC LIMIT 1
                """, (title,))
                return cur.fetchone()

    def remove_from_waiting_list(self, email, title): # libraryService.return_book
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM waiting_lists WHERE user_email = %s AND book_title = %s", 
                           (email.lower(), title))
            conn.commit()

            
    
    
            

    def get_user_active_borrows(self, email): # libraryService.get_user_borrowed_books
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                sql = """
                    SELECT b.title, br.return_deadline 
                    FROM books b
                    JOIN borrows br ON b.title = br.book_title
                    WHERE br.user_email = %s AND br.status = 'active'
                """
                cur.execute(sql, (email.lower(),))
                return cur.fetchall()
            

    #REPORTS
    def report_online_users(self): # libraryService.get_online_users_count
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT COUNT(*) as count FROM users WHERE last_login >= NOW() - INTERVAL '30 minutes'")
                return cur.fetchone()['count']
            
    def report_daily_logins(self): # libraryService.get_daily_logins
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT first_name, last_name FROM users WHERE last_login >= NOW() - INTERVAL '1 day'")
                return cur.fetchall()
            
    def report_negative_scores(self): # libraryService.get_negative_users
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                sql = """
                    SELECT DISTINCT u.first_name, u.last_name, u.negative_score 
                    FROM users u
                    JOIN borrows br ON u.email = br.user_email
                    JOIN books b ON br.book_title = b.title
                    WHERE u.negative_score > 0 
                    AND LOWER(b.genre) = 'psychology'
                """
                cur.execute(sql)
                return cur.fetchall()
            
    def report_popular_genres(self): # libraryService.get_popular_genres
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT b.genre, COUNT(*) as borrow_count
                    FROM borrows br
                    JOIN books b ON br.book_title = b.title
                    GROUP BY b.genre
                    HAVING COUNT(*) >= 20
                    ORDER BY borrow_count DESC
                """)
                return cur.fetchall()
            
    def report_top_books(self): # libraryService.get_top_borrowed_books
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT book_title, COUNT(*) as count
                    FROM borrows
                    GROUP BY book_title
                    ORDER BY count DESC
                    LIMIT 5
                """)
                return cur.fetchall()



    def report_top_donor(self): # libraryService.get_top_donor_info
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT donor, COUNT(*) as total_donated
                    FROM books
                    WHERE donor IS NOT NULL
                    GROUP BY donor
                    ORDER BY total_donated DESC
                    LIMIT 1
                """)
                top_donor = cur.fetchone()

                if top_donor:
                    donor_email = top_donor['donor']
                    cur.execute("""
                        SELECT genre, COUNT(*) as count
                        FROM books
                        WHERE donor = %s
                        GROUP BY genre
                        ORDER BY count DESC
                        LIMIT 1
                    """, (donor_email,))
                    fav_genre = cur.fetchone()
                    
                    return {
                        'email': donor_email,
                        'total_donated': top_donor['total_donated'],
                        'fav_genre': fav_genre['genre'] if fav_genre else "Unknown"
                    }
                return None