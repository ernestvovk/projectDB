import sqlite3
from datetime import datetime, timedelta


class Library:
    def __init__(self, db_name="library.db"):
        # Connect to SQLite database (or create it)
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Books (
                book_id INTEGER PRIMARY KEY,
                title TEXT,
                author TEXT,
                isbn TEXT,
                is_available BOOLEAN
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                contact_details TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                transaction_type TEXT,
                transaction_date TIMESTAMP,
                return_date TIMESTAMP,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id),
                FOREIGN KEY (book_id) REFERENCES Books(book_id)
            )
        ''')

        # Create indexes for efficient querying
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_isbn ON Books(isbn)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_available ON Books(is_available)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_id ON Users(user_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_id ON Transactions(transaction_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON Transactions(user_id)')
        self.conn.commit()

        # In-memory hash tables for fast lookups
        self.book_by_id = {}
        self.book_by_isbn = {}
        self.user_by_id = {}
        self.loan_by_id = {}

    def add_book(self, book_id, title, author, isbn):
        self.cursor.execute('''
            INSERT INTO Books (book_id, title, author, isbn, is_available)
            VALUES (?, ?, ?, ?, ?)
        ''', (book_id, title, author, isbn, True))
        self.conn.commit()

        # Update the in-memory hash tables
        self.book_by_id[book_id] = {'title': title, 'author': author, 'isbn': isbn, 'is_available': True}
        self.book_by_isbn[isbn] = {'book_id': book_id, 'title': title, 'author': author, 'is_available': True}

    def remove_book(self, book_id):
        self.cursor.execute('DELETE FROM Books WHERE book_id = ?', (book_id,))
        self.conn.commit()

        # Remove from the in-memory hash tables
        if book_id in self.book_by_id:
            del self.book_by_id[book_id]
            book = self.book_by_id[book_id]
            del self.book_by_isbn[book['isbn']]

    def update_book(self, book_id, title=None, author=None, isbn=None):
        book = self.book_by_id.get(book_id)
        if title:
            self.cursor.execute('UPDATE Books SET title = ? WHERE book_id = ?', (title, book_id))
            book['title'] = title
        if author:
            self.cursor.execute('UPDATE Books SET author = ? WHERE book_id = ?', (author, book_id))
            book['author'] = author
        if isbn:
            self.cursor.execute('UPDATE Books SET isbn = ? WHERE book_id = ?', (isbn, book_id))
            self.book_by_isbn.pop(book['isbn'], None)  # Remove old ISBN from hash table
            book['isbn'] = isbn
            self.book_by_isbn[isbn] = book

        self.conn.commit()

    def search_book_by_id(self, book_id):
        return self.book_by_id.get(book_id)

    def search_book_by_isbn(self, isbn):
        return self.book_by_isbn.get(isbn)

    def add_user(self, user_id, name, contact_details):
        self.cursor.execute('''
            INSERT INTO Users (user_id, name, contact_details)
            VALUES (?, ?, ?)
        ''', (user_id, name, contact_details))
        self.conn.commit()

        # Update in-memory hash table
        self.user_by_id[user_id] = {'name': name, 'contact_details': contact_details}

    def remove_user(self, user_id):
        self.cursor.execute('DELETE FROM Users WHERE user_id = ?', (user_id,))
        self.conn.commit()

        # Remove from in-memory hash table
        if user_id in self.user_by_id:
            del self.user_by_id[user_id]

    def search_user_by_id(self, user_id):
        return self.user_by_id.get(user_id)

    def borrow_book(self, user_id, book_id):
        # Check if book is available
        book = self.book_by_id.get(book_id)
        if not book or not book['is_available']:
            print(f"Book with ID {book_id} is not available.")
            return

        # Mark book as unavailable
        self.cursor.execute('''
            UPDATE Books SET is_available = ? WHERE book_id = ?
        ''', (False, book_id))
        self.conn.commit()
        book['is_available'] = False

        # Record the transaction
        transaction_date = datetime.now()
        return_date = transaction_date + timedelta(days=14)  # Assuming 14 days loan period
        self.cursor.execute('''
            INSERT INTO Transactions (user_id, book_id, transaction_type, transaction_date, return_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, book_id, 'borrow', transaction_date, return_date, 'borrowed'))
        self.conn.commit()

        # Update in-memory hash table for loans
        transaction_id = self.cursor.lastrowid
        self.loan_by_id[transaction_id] = {'user_id': user_id, 'book_id': book_id, 'status': 'borrowed', 'transaction_date': transaction_date, 'return_date': return_date}

    def return_book(self, transaction_id):
        # Retrieve transaction details
        transaction = self.loan_by_id.get(transaction_id)
        if not transaction:
            print(f"Transaction with ID {transaction_id} not found.")
            return

        # Mark book as available again
        book_id = transaction['book_id']
        self.cursor.execute('''
            UPDATE Books SET is_available = ? WHERE book_id = ?
        ''', (True, book_id))
        self.conn.commit()

        # Update transaction status to 'returned'
        self.cursor.execute('''
            UPDATE Transactions SET status = ? WHERE transaction_id = ?
        ''', ('returned', transaction_id))
        self.conn.commit()

        # Update in-memory hash table for loan
        transaction['status'] = 'returned'

    def search_transaction_by_id(self, transaction_id):
        return self.loan_by_id.get(transaction_id)

    def search_transaction_by_user_id(self, user_id):
        transactions = []
        for trans_id, trans in self.loan_by_id.items():
            if trans['user_id'] == user_id:
                transactions.append(trans)
        return transactions

    def close(self):
        # Close the database connection
        self.conn.close()


# Example usage of the Library Management System with SQL and Hashing
library = Library()

# Adding books
books = [
    (1, "1984", "George Orwell", "9780451524935"),
    (2, "To Kill a Mockingbird", "Harper Lee", "9780061120084"),
    (3, "Pride and Prejudice", "Jane Austen", "9781503290563"),
    (4, "The Great Gatsby", "F. Scott Fitzgerald", "9780743273565"),
    (5, "Moby-Dick", "Herman Melville", "9781503280786"),
    (6, "War and Peace", "Leo Tolstoy", "9780143039990"),
    (7, "The Catcher in the Rye", "J.D. Salinger", "9780316769488"),
    (8, "The Hobbit", "J.R.R. Tolkien", "9780547928227"),
    (9, "Fahrenheit 451", "Ray Bradbury", "9781451673319"),
    (10, "The Odyssey", "Homer", "9780140268867"),
    (11, "Crime and Punishment", "Fyodor Dostoevsky", "9780486454115"),
    (12, "The Brothers Karamazov", "Fyodor Dostoevsky", "9780374528379"),
    (13, "Jane Eyre", "Charlotte Brontë", "9780141441146"),
    (14, "Brave New World", "Aldous Huxley", "9780060850524"),
    (15, "The Divine Comedy", "Dante Alighieri", "9780142437223"),
    (16, "Les Misérables", "Victor Hugo", "9780451419439"),
    (17, "Wuthering Heights", "Emily Brontë", "9780141439556"),
    (18, "Anna Karenina", "Leo Tolstoy", "9781400079988"),
    (19, "The Catcher in the Rye", "J.D. Salinger", "9780316769488"),
    (20, "The Picture of Dorian Gray", "Oscar Wilde", "9780141439570"),
    (21, "Dracula", "Bram Stoker", "9780486411097"),
    (22, "Frankenstein", "Mary Shelley", "9780486282114"),
    (23, "The Stranger", "Albert Camus", "9780679736376"),
    (24, "The Scarlet Letter", "Nathaniel Hawthorne", "9780142437261"),
    (25, "A Tale of Two Cities", "Charles Dickens", "9780486406512"),
    (26, "The Sun Also Rises", "Ernest Hemingway", "9780743297332"),
    (27, "The Grapes of Wrath", "John Steinbeck", "9780143039433"),
    (28, "The Road", "Cormac McCarthy", "9780307387899"),
    (29, "One Hundred Years of Solitude", "Gabriel García Márquez", "9780060883287"),
    (30, "Slaughterhouse-Five", "Kurt Vonnegut", "9780440180296"),
    (31, "The Shining", "Stephen King", "9780307743657"),
    (32, "The Color Purple", "Alice Walker", "9780156031820"),
    (33, "The Alchemist", "Paulo Coelho", "9780062315007"),
    (34, "Catch-22", "Joseph Heller", "9781451626683"),
    (35, "The Godfather", "Mario Puzo", "9780451205766"),
    (36, "The Lord of the Rings", "J.R.R. Tolkien", "9780544003415"),
    (37, "The Hunger Games", "Suzanne Collins", "9780439023481"),
    (38, "The Twilight Saga", "Stephenie Meyer", "9780316015844"),
    (39, "Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "9780590353427"),
    (40, "The Chronicles of Narnia", "C.S. Lewis", "9780066238500"),
    (41, "The Maze Runner", "James Dashner", "9780385737951"),
    (42, "The Outsiders", "S.E. Hinton", "9780142407332"),
    (43, "The Hitchhiker's Guide to the Galaxy", "Douglas Adams", "9780345391803"),
    (44, "Ender's Game", "Orson Scott Card", "9780812550702"),
    (45, "Dune", "Frank Herbert", "9780441013593"),
    (46, "The Handmaid's Tale", "Margaret Atwood", "9780385490818"),
    (47, "The Secret Garden", "Frances Hodgson Burnett", "9780141321042"),
    (48, "The Wind in the Willows", "Kenneth Grahame", "9780486283661"),
    (49, "The Little Prince", "Antoine de Saint-Exupéry", "9780156012195"),
    (50, "The Art of War", "Sun Tzu", "9781590302255")
]
#adding books to library
for book in books:
    library.add_book(*book)

users = [
    (101, "Alice", "alice@gmail.com"),
    (102, "Bob", "bob@gmail.com"),
    (103, "Charlie", "charlie@gmail.com"),
    (104, "David", "david@gmail.com"),
    (105, "Eva", "eva@gmail.com"),
    (106, "Frank", "frank@gmail.com"),
    (107, "Grace", "grace@gmail.com"),
    (108, "Hannah", "hannah@gmail.com"),
    (109, "Ivy", "ivy@gmail.com"),
    (110, "Jack", "jack@gmail.com"),
    (111, "Kathy", "kathy@gmail.com"),
    (112, "Liam", "liam@gmail.com"),
    (113, "Mona", "mona@gmail.com"),
    (114, "Nathan", "nathan@gmail.com"),
    (115, "Olivia", "olivia@gmail.com"),
    (116, "Peter", "peter@gmail.com"),
    (117, "Quincy", "quincy@gmail.com"),
    (118, "Rachel", "rachel@gmail.com"),
    (119, "Sam", "sam@gmail.com"),
    (120, "Tina", "tina@gmail.com"),
    (121, "Ursula", "ursula@gmail.com"),
    (122, "Victor", "victor@gmail.com"),
    (123, "Wendy", "wendy@gmail.com"),
    (124, "Xander", "xander@gmail.com"),
    (125, "Yara", "yara@gmail.com"),
    (126, "Zane", "zane@gmail.com"),
    (127, "Amy", "amy@gmail.com"),
    (128, "Brian", "brian@gmail.com"),
    (129, "Catherine", "catherine@gmail.com"),
    (130, "Daniel", "daniel@gmail.com")
]

# adding users to library
for user in users:
    library.add_user(*user)

# Searching books by Book ID and ISBN
print()
print(library.search_book_by_id(1))
print(library.search_book_by_id(49))
print(library.search_book_by_id(22))
print(library.search_book_by_id(32))
print(library.search_book_by_id(41))
print(library.search_book_by_id(20))
print(library.search_book_by_id(3))
print(library.search_book_by_isbn("9780061120084"))
print(library.search_book_by_isbn("9780156012195"))
print(library.search_book_by_isbn("9780142437223"))
print(library.search_book_by_isbn("9780451205766"))


# Searching users by User ID
print()
print(library.search_user_by_id(101))
print(library.search_user_by_id(105))
print(library.search_user_by_id(103))
print(library.search_user_by_id(108))
print(library.search_user_by_id(106))
print(library.search_user_by_id(111))
print(library.search_user_by_id(120))
print()

# Borrowing and returning books
library.borrow_book(101, 1)
library.borrow_book(102, 2)
library.borrow_book(104, 31)
library.borrow_book(108, 22)
library.borrow_book(112, 23)
library.borrow_book(113, 11)
library.borrow_book(103, 44)
library.borrow_book(102, 32)
library.borrow_book(101, 21)
library.borrow_book(104, 47)
library.return_book(1)
library.return_book(5)
library.return_book(3)

# Searching transactions
print()
print(library.search_transaction_by_id(1))
print(library.search_transaction_by_id(6))
print(library.search_transaction_by_id(2))
print(library.search_transaction_by_id(3))
print(library.search_transaction_by_id(5))
print(library.search_transaction_by_user_id(102))
print(library.search_transaction_by_user_id(101))
print(library.search_transaction_by_user_id(112))
print(library.search_transaction_by_user_id(104))
print(library.search_transaction_by_user_id(113))
print()

#####################################################
!pip install Faker
from faker import Faker
import random
import time


def generate_and_store_books(library, num_books=1000):

    fake = Faker()

    start_time = time.time()  # Record the start time

    for i in range(51, num_books + 1):
        title = fake.sentence(nb_words=random.randint(2, 5)).capitalize().replace(".", "")
        author = fake.name()
        isbn = fake.isbn13()  # Use Faker's built-in generator
        library.add_book(i, title, author, isbn)  # Store in database

    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate elapsed time

    print(f"Generated and stored {num_books} books in {elapsed_time:.2f} seconds.")



generate_and_store_books(library)  # Call the function to generate and store books
print()

#####################################################

# Measuring insertion time for in-memory hash tables
start_time = time.time()
for book in books:
    library.book_by_id[book[0]] = {'title': book[1], 'author': book[2], 'isbn': book[3], 'is_available': True}
    library.book_by_isbn[book[3]] = {'book_id': book[0], 'title': book[1], 'author': book[2], 'is_available': True}
    # Also add users to the hash table
for user in users:
    library.user_by_id[user[0]] = {'name': user[1], 'contact_details': user[2]}
hash_insert_time = time.time() - start_time


# Querying a book by ID from SQLite database
start_time = time.time()
library.search_book_by_id(1000)
db_query_time_book_id = time.time() - start_time

# Querying a book by ISBN from SQLite database
start_time = time.time()
library.search_book_by_isbn("9780061120084")
db_query_time_isbn = time.time() - start_time

# Querying a user by ID from SQLite database
start_time = time.time()
library.search_user_by_id(115)
db_query_time_user = time.time() - start_time

# Querying the book by ID from the in-memory hash table
start_time = time.time()
library.book_by_id.get(1000)
hash_query_time_book_id = time.time() - start_time

# Querying the book by ISBN from the in-memory hash table
start_time = time.time()
library.book_by_isbn.get("9780061120084")
hash_query_time_isbn = time.time() - start_time

# Querying the user by ID from the in-memory hash table
start_time = time.time()
library.user_by_id.get(115)
hash_query_time_user = time.time() - start_time

# Output the results
print(f"Insertion time (Hash Tables): {hash_insert_time:.4f} seconds")
print(f"Query time (SQLite DB - Book ID): {db_query_time_book_id:.4f} seconds")
print(f"Query time (SQLite DB - ISBN): {db_query_time_isbn:.4f} seconds")
print(f"Query time (SQLite DB - User ID): {db_query_time_user:.4f} seconds")
print(f"Query time (Hash Tables - Book ID): {hash_query_time_book_id:.4f} seconds")
print(f"Query time (Hash Tables - ISBN): {hash_query_time_isbn:.4f} seconds")
print(f"Query time (Hash Tables - User ID): {hash_query_time_user:.4f} seconds")


###############################
db_query_times_book_id = []
for _ in range(100):  # Repeat query 100 times
    library.cursor.execute("PRAGMA cache_size = 0") # Clear cache
    start_time = time.perf_counter()
    library.cursor.execute("SELECT * FROM Books WHERE book_id = ?", (1,))
    library.cursor.fetchone()  # Fetch the result
    db_query_times_book_id.append(time.perf_counter() - start_time)
avg_db_query_time_book_id = sum(db_query_times_book_id) / len(db_query_times_book_id)

# Querying the book by ID from the in-memory hash table
hash_query_times_book_id = []
for _ in range(100):  # Repeat query 100 times
    start_time = time.perf_counter()
    library.book_by_id.get(1)  # Book ID 1
    hash_query_times_book_id.append(time.perf_counter() - start_time)
avg_hash_query_time_book_id = sum(hash_query_times_book_id) / len(hash_query_times_book_id)

print()
print(f"Average Query time (SQLite DB - Book ID): {avg_db_query_time_book_id:.6f} seconds")
print(f"Average Query time (Hash Tables - Book ID): {avg_hash_query_time_book_id:.6f} seconds")
print()

start_date = datetime(2023, 1, 1)  # Example: January 1, 2023
end_date = datetime(2023, 12, 31)  # Example: December 31, 2023

start_time = time.time()
library.cursor.execute("SELECT * FROM Transactions WHERE transaction_date BETWEEN ? AND ?", (start_date, end_date))
transactions_in_range = library.cursor.fetchall()
range_query_time = time.time() - start_time
print(f"Query time for range-based retrieval: {range_query_time:.4f} seconds")

library.close()
