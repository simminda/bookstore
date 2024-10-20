import os
import sys
import sqlite3
from prettytable import PrettyTable

# Constants
RED = "\033[31m"
GREEN = "\033[1;32m"
WHITE = "\033[0m"


def main():
    """Main function to initialize the database and display the menu."""
    db, cursor = connect_database()

    # Create table
    cursor.execute("DROP TABLE IF EXISTS books")
    cursor.execute('''
        CREATE TABLE books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            qty INTEGER)
    ''')

    # Insert initial records
    book_records = [
        (3001, 'A tale of Two Cities', 'Charles Dickens', 30),
        (3002, 'Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 40),
        (3003, 'The Lion, the Witch and the Wardrobe', 'C.S. Lewis', 25),
        (3004, 'The Lord of the Rings', 'J.R.R Tolkien', 37),
        (3005, 'Alice in Wonderland', 'Lewis Carroll', 12)
    ]

    cursor.executemany('''
            INSERT OR IGNORE INTO books(id, title, author, qty) VALUES(?,?,?,?)
        ''', book_records)
    db.commit()
    print(f"\n{cursor.rowcount} records have been inserted into the table.")

    # Close the connection once all operations are done
    db.close()

    # Call the menu function after setting up the database
    while True:
        menu()


def connect_database():
    """
    Connect to the SQLite database and return the connection and cursor.

    Returns:
        tuple: A tuple containing the database connection and cursor.
    """
    try:
        # Ensure the 'data' directory exists
        os.makedirs('data', exist_ok=True)

        db = sqlite3.connect('data/ebookstore.db')
        cursor = db.cursor()

        return db, cursor  # Return both to control when to close connection
    except sqlite3.Error as e:
        print(f"✘ An error occurred: {e}")


def menu():
    """Display the main menu and handle user selection."""
    clear_console()

    print("\033[1;32m╔════════════════════════════╗ ")
    print(" ══════   eBookStore   ══════ ")
    print("╚════════════════════════════╝ \n\033[0m")
    print("1. Add book")
    print("2. Update book")
    print("3. Delete book")
    print("4. Search books")
    print("5. View all books")
    print("0. Exit")

    try:
        selection = int(input("\nEnter selection: "))

        match selection:
            case 1:
                add_book()
            case 2:
                update_books()
            case 3:
                delete_book()
            case 4:
                search()
            case 5:
                db, cursor = connect_database()
                print(view_books(cursor, "SELECT * FROM Books"))
                db.close()
                pause_with_key_press()
            case 0:
                sys.exit("\nGoodbye\n")
            case _:
                print("Invalid selection")
    except ValueError:
        print("{RED}✘ Error: Please enter a number only{WHITE}")


def clear_console():
    """Clear the console screen based on the operating system."""
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For macOS and Linux
    else:
        os.system('clear')


def add_book():
    """
    Add a new book to the database.

    Prompts the user for book details and inserts them into the database.
    """
    try:
        print("\nAdd Book")
        print("---------")
        title = input("Enter book title: ")
        author = input("Enter book author: ")
        qty = int(input("Enter book qty: "))
    except ValueError:
        print(f"{RED}✘ Invalid book data entered{WHITE}")
        return False

    try:
        db, cursor = connect_database()
        cursor.execute('''
            INSERT INTO Books(title, author, qty) VALUES(?, ?, ?)
        ''', (title, author, qty))
        db.commit()

        print(f"\n{qty} units of {title} by {author} added to Books")
        pause_with_key_press()
    except sqlite3.Error as e:
        print(f"{RED}✘ An error occurred: {e}{WHITE}")
    finally:
        db.close()


def update_books():
    """
    Update the details of an existing book.

    Prompts the user for the book ID and new details, and updates the record in the database.
    """
    print("\nUpdate Book")

    try:
        book_id = int(input("Enter Book ID to update: "))
    except ValueError:
        print(f"{RED}✘ Invalid ID entered. Please enter a valid number.{WHITE}")
        return False

    try:
        # Connect to the database
        db, cursor = connect_database()

        # Check if the book exists
        cursor.execute('''
            SELECT * FROM Books WHERE id = ?
        ''', (book_id,))
        result = cursor.fetchone()

        if result:
            # Show the current book details
            print(f"\nCurrent details of book ID {book_id}:")
            print(f'''ID: {result[0]} \nTitle: {result[1]} \nAuthor: {
                  result[2]} \nQuantity: {result[3]}''')

            # Prompt the user for new values (leave blank to keep the same value)
            new_title = input(
                f"\nEnter new title (or press Enter to keep '{result[1]}'): ").strip()
            new_author = input(
                f"Enter new author (or press Enter to keep '{result[2]}'): ").strip()
            new_qty = input(
                f"Enter new quantity (or press Enter to keep '{result[3]}'): ").strip()

            # Use the existing values if the user didn't provide new ones
            updated_title = new_title if new_title else result[1]
            updated_author = new_author if new_author else result[2]
            updated_qty = int(new_qty) if new_qty else result[3]

            # Perform the update in the database
            cursor.execute('''
                UPDATE Books
                SET title = ?, author = ?, qty = ?
                WHERE id = ?
            ''', (updated_title, updated_author, updated_qty, book_id))
            db.commit()

            print(f'''{GREEN}\n✔ Book with ID {
                  book_id} has been updated.{WHITE}''')
        else:
            print(f"{RED}✘ No book found with ID: {book_id}{WHITE}")

    except ValueError:
        print("{RED}✘ Quantity must be a valid number.{WHITE}")
    except sqlite3.Error as e:
        print(f"{RED}✘ An error occurred: {e}{WHITE}")

    finally:
        db.close()

    # Pause before returning to the menu
    pause_with_key_press()


def delete_book():
    """
    Delete a book from the database.

    Prompts the user for the book ID, confirms deletion, and removes the record from the database if confirmed.
    """
    print("\nDelete Book")
    try:
        book_to_delete = int(input("Enter Book ID: "))
    except ValueError:
        print("{RED}✘ Invalid ID entered{WHITE}")
        return False

    try:
        # Connect to the database
        db, cursor = connect_database()

        # Check if the book exists
        cursor.execute('''
            SELECT * FROM Books WHERE id = ?
        ''', (book_to_delete,))
        result = cursor.fetchone()

        if result:
            # Show the book details
            print(f'''\nBook found: \nID: {result[0]} \nTitle: {
                  result[1]} \nAuthor: {result[2]} \nQuantity: {result[3]}''')

            # Confirm deletion
            confirm = input(
                "\nAre you sure you want to delete this book? (y/n): ").lower()
            if confirm == 'y':
                cursor.execute('''
                    DELETE FROM Books WHERE id = ?
                ''', (book_to_delete,))
                db.commit()
                print(f'''{GREEN}\n✔ Book with ID {
                      book_to_delete} has been deleted.{WHITE}''')
            else:
                print("\nDeletion cancelled.")
        else:
            print(f"{RED}\n✘ No book found with ID: {book_to_delete}{WHITE}")
    except sqlite3.Error as e:
        print(f"{RED}✘ An error occurred: {e}{WHITE}")
    finally:
        db.close()

    # Pause before returning to the menu
    pause_with_key_press()


def search():
    """
    Search for books in the database.

    Allows the user to search for books by name or ID, displaying results if found.
    """
    print("\nSearch Book")
    print("1. Search by name")
    print("2. Search by ID")
    print("0. Cancel")

    # Prompt until valid selection
    while True:
        option = int(input("\nEnter selection: "))
        if 0 <= option <= 2:
            break
        else:
            print("✘ Invalid option number entered")

    # Search by book name
    if option == 1:
        try:
            title = input("\nEnter book name: ").strip()
            db, cursor = connect_database()
            cursor.execute('''
                SELECT * FROM Books WHERE title = ?
            ''', (title,))
            result = cursor.fetchall()

            # Print results
            if result:
                print(f"{GREEN}\nBooks found with title '{title}':{WHITE}")
                for book in result:
                    print(f'''ID: {book[0]} \nTitle: {book[1]} \nAuthor: {
                        book[2]} \nQuantity: {book[3]}''')
            else:
                print(f"{RED}\n✘ No books found with title '{title}'.{WHITE}")
        except sqlite3.Error as e:
            print(f"{RED}✘ An error occurred: {e}{WHITE}")
        finally:
            db.close()

    # Search by book id
    elif option == 2:
        try:
            book_id = int(input("Enter book ID: "))
            db, cursor = connect_database()
            cursor.execute('''
                SELECT * FROM Books WHERE id = ?
            ''', (book_id,))
            result = cursor.fetchone()

            # Print results
            if result:
                print(f"{GREEN}\nBook found with ID '{book_id}':{WHITE}")
                print(f'''ID: {result[0]} \nTitle: {result[1]} \nAuthor: {
                    result[2]} \nQuantity: {result[3]}''')
            else:
                print(f'''{RED}\n✘ No books found with an ID: '{
                      book_id}'.{WHITE}''')
        except ValueError:
            print("{RED}✘ Error: ID must be a number{WHITE}")
        except sqlite3.Error as e:
            print(f"{RED}✘ An error occurred: {e}{WHITE}")
        finally:
            db.close()

    # Pause before returning to the menu
    pause_with_key_press()


def view_books(cursor, query):
    """
    Retrieve and format books for display.

    Args:
        cursor (sqlite3.Cursor): The database cursor for executing queries.
        query (str): The SQL query to execute.

    Returns:
        str: A formatted string of books for display.
    """
    sql_table = PrettyTable()
    sql_table.field_names = ["id", "title", "author", "qty"]

    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        sql_table.add_row(row)

    return sql_table


def pause_with_key_press():
    """Pause the execution and wait for the user to press any key."""
    input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
