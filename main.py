from storageManager import StorageManager
from auth import AuthService
from libraryService import LibraryService
import os

storage = StorageManager()
auth_service = AuthService(storage)
library_service = LibraryService(storage)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    while True:
        clear_screen()
        print("Welcome to the library system")
        print("1. Register\n2. Login\n3. Exit")
        choice = input("Enter your choice: ")
        match choice:
            case "1":
                first_name = input("First name: ")
                last_name = input("Last name: ")
                email = input("Email: ")
                password = input("Password: ")
                auth_service.register(first_name, last_name, email, password)
                input("Press Enter to go to Login menu...")
            case "2":
                email = input("Email: ")
                password = input("Password: ")
                user = auth_service.login_user(email, password)
                if user:
                    library_menu(user)
                else:
                    input("Press Enter to try again...")
            case "3":
                print("Goodbye")
                break
            case _:
                input("Invalid choice! Press Enter...")




def library_menu(user):
    while True:
        clear_screen()
        print(f"Welcome {user.first_name} {user.last_name}")
        print("1. Search\n2. Borrow\n3. Return\n4. My Books\n5. Donate\n6. Logout\n7. Reports")
        choice = input("Enter your choice: ")
        match choice:
            case "1":
                print("--- Search Books (Fill only what you need, leave others empty) ---")
                title = input("Title: ").strip()
                author = input("Author: ").strip()
                publisher = input("Publisher: ").strip()
                genre = input("Genre: ").strip()
                status = input("Status (available/borrowed): ").strip()

                filters = {}
                if title: filters["title"] = title
                if author: filters["author"] = author
                if publisher: filters["publisher"] = publisher
                if genre: filters["genre"] = genre
                if status: filters["status"] = status

                results=library_service.search(filters)
                print("\n" + "="*70)
                if not results:
                    print("No books found")
                else:
                    for book in results:
                        print(f"{book.title[:19]:<20} | {book.author[:14]:<15} | {book.publisher[:14]:<15} | {book.status:<10}")

                print("="*70)
                input("\nPress Enter to return to menu...")

            case "2":
                title = input("Enter the title of the book to borrow: ")
                library_service.borrow(user.email, title)
                input("\nPress Enter...")

            case "3":
                title = input("Enter the title of the book to return: ")
                library_service.return_book(user.email, title)
                input("\nPress Enter...")

            case "4":
                my_books = library_service.get_user_borrowed_books(user.email)
                print("\n" + "="*40)
                print(f"{'Title':<25} | {'Deadline':<15}")
                print("-" * 40)
                if not my_books:
                    print("You don't have any books currently.")
                else:
                    for b in my_books:
                        deadline_str = b['return_deadline'].strftime("%H:%M:%S")
                        print(f"{b['title'][:24]:<25} | {deadline_str:<15}")
                print("="*40)
                input("\nPress Enter...")

            case "5":
                print("--- Donate a Book ---")
                t = input("Title: ")
                a = input("Author: ")
                p = input("Publisher: ")
                g = input("Genre: ")
                d = input("Publish Date (e.g. 2023): ")
                library_service.donate(t, a, p, g, d, user.email)
                input("\nPress Enter...")

            case "6":
                print("Logging out...")
                break
            
            case "7":
                while True:
                    clear_screen()
                    print("--- ADMIN REPORTS MENU ---")
                    print("1. Online Users (Last 30 mins)")
                    print("2. Recent Logins (Last 24h)")
                    print("3. Negative Scores (Psychology Readers)")
                    print("4. Popular Genres (20+ borrows)")
                    print("5. Top 5 Most Borrowed Books")
                    print("6. Top Donor Champion")
                    print("7. Back to Main Menu")
                    
                    r_choice = input("\nSelect a report to view: ")
                    
                    print("\n" + "-"*50)
                    
                    match r_choice:
                        
                        case "1":
                            count = library_service.get_online_users_count()
                            print(f"[*] Online Users Now: {count}")

                        case "2":
                            users = library_service.get_daily_logins()
                            print("[*] Logins in Last 24h:")
                            if users:
                                for u in users:
                                    print(f"   - {u['first_name']} {u['last_name']}")
                            else:
                                print("   None")

                        case "3":
                            users = library_service.get_negative_users()
                            print("[*] Negative Scores & Psychology Readers:")
                            if users:
                                for u in users:
                                    print(f"   - {u['first_name']} {u['last_name']} (Score: {u['negative_score']})")
                            else:
                                print("   No matching users found.")

                        case "4":
                            genres = library_service.get_popular_genres()
                            print("[*] Popular Genres:")
                            if genres:
                                for g in genres:
                                    print(f"   - {g['genre']} ({g['borrow_count']} borrows)")
                            else:
                                print("   No genre has reached 20 borrows yet.")

                        case "5":
                            books = library_service.get_top_borrowed_books()
                            print("[*] Top 5 Books:")
                            if books:
                                for i, b in enumerate(books, 1):
                                    print(f"   {i}. {b['book_title']} ({b['count']} borrows)")
                            else:
                                print("   No stats available.")

                        case "6":
                            donor = library_service.get_top_donor_info()
                            print("[*] Top Donor Info:")
                            if donor:
                                print(f"   User: {donor['email']}")
                                print(f"   Total Donated: {donor['total_donated']} books")
                                print(f"   Favorite Genre: {donor['fav_genre']}")
                            else:
                                print("   No donations yet.")

                        case "7":
                            break

                        case _:
                            print("Invalid selection. Please choose a valid number.")

                    print("-" * 50)
                    input("Press Enter to return to reports menu...")
                
            case _:
                input("Invalid choice! Press Enter...")

if __name__ == "__main__":
    main()