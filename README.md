# projectDB
# Overview of the Library Managment System
This system is a basic example of a library management system that uses three database tables: Books, Users, Transactions.
To optimize performance, the system uses in-memory hash tables for frequently accessed data, while SQLite is used as the persistent storage system.

First part of the code is the implementation of LibrarySQL class
Second is where I generated the test cases
Third is where I tracked the time of the test cases

# Schema Design

Books Table:

Columns:
book_id: Unique ID of the book (Primary Key).
title: Title of the book.
author: Author of the book.
isbn: ISBN number of the book.
is_available: Boolean indicating whether the book is available for borrowing.

Users Table:

Columns:
user_id: Unique ID of the user (Primary Key).
name: Name of the user.
contact_details: Email of the user.

Transactions Table:

Columns:
transaction_id: Unique transaction ID (Primary Key).
user_id: Foreign key referencing the Users table.
book_id: Foreign key referencing the Books table.
transaction_type: Type of transaction (borrow or return).
transaction_date: Timestamp of when the transaction occurred.
return_date: Expected date for the book to be returned.
status: Status of the transaction (borrowed or returned).

# Hashing Implementation

book_by_id: Stores books indexed by book_id. 
book_by_isbn: Stores books indexed by isbn.
user_by_id: Stores users indexed by user_id. 
loan_by_id: Stores transactions indexed by transaction_id. 

# Supported Operation (CRUD)

Books:
Create: add_book()
Read: search_book_by_id(), search_book_by_isbn()
Update: update_book()
Delete: remove_book()

Users:
Create: add_user()
Read: search_user_by_id()
Update: update_user()
Delete: remove_user()

Transactions:
Create: borrow_book(), return_book()
Read: search_transaction_by_id(), search_transaction_by_user_id()
Update: update_transaction_status()
Delete: remove_transaction()

# Performance Report:

Insertion Time

Hash Tables: The time taken to insert book and user data into in-memory hash tables was approximately 0.0018 seconds. This demonstrates the efficiency of hash tables for insertions due to their constant-time complexity.

SQLite Database: The insertion time for SQLite isn't explicitly measured in the code. However, we can infer its performance from the overall execution time of adding 1000 books. It took approximately 2.54 seconds to generate and store 1000 books in SQLite. This suggests that SQLite insertion time is longer than hash table insertion, but this difference can be considered insignificant when dealing with 1000 books or less.

Query Time

Hash Tables: Hash tables excel in query performance, especially for retrieving data by a unique key.
Average query time for book by ID: 0.000002 seconds
Average query time for book by ISBN: 0.000001 seconds
Average query time for user by ID: 0.000001 seconds

SQLite Database: While SQLite's query time is generally slower than hash tables, it remains reasonably fast for smaller datasets.
Average query time for book by ID: 0.000027 seconds
Average query time for book by ISBN: 0.000015 seconds
Average query time for user by ID: 0.000015 seconds

Range-Based Retrieval

The range-based retrieval performance was observed by querying Transactions table within a date range. This query execution took approximately 0.0001 seconds, indicating efficient range-based filtering.
