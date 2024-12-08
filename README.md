# projectDB
# Overview of the Library Managment System
This system is a basic example of a library management system that uses three database tables: Books, Users, Transactions.
To optimize performance, the system uses in-memory hash tables for frequently accessed data, while SQLite is used as the persistent storage system.

First part of the code is the implementation of LibrarySQL class<br />
Second is where I generated the test cases<br />
Third is where I tracked the time of the test cases

# Schema Design

Books Table:

Columns:<br />
book_id - Unique ID of the book (Primary Key).<br />
title: Title of the book.<br />
author: Author of the book.<br />
isbn: ISBN number of the book.<br />
is_available: Boolean indicating whether the book is available for borrowing.<br />

Users Table:

Columns:<br />
user_id: Unique ID of the user (Primary Key).<br />
name: Name of the user.<br />
contact_details: Email of the user.<br />

Transactions Table:

Columns:<br />
transaction_id: Unique transaction ID (Primary Key).<br />
user_id: Foreign key referencing the Users table.<br />
book_id: Foreign key referencing the Books table.<br />
transaction_type: Type of transaction (borrow or return).<br />
transaction_date: Timestamp of when the transaction occurred.<br />
return_date: Expected date for the book to be returned.<br />
status: Status of the transaction (borrowed or returned).<br />

# Hashing Implementation

book_by_id: Stores books indexed by book_id. <br />
book_by_isbn: Stores books indexed by isbn.<br />
user_by_id: Stores users indexed by user_id. <br />
loan_by_id: Stores transactions indexed by transaction_id. <br />

# Supported Operation (CRUD)

Books:<br />
Create: add_book()<br />
Read: search_book_by_id(), search_book_by_isbn()<br />
Update: update_book()<br />
Delete: remove_book()<br />

Users:<br />
Create: add_user()<br />
Read: search_user_by_id()<br />
Update: update_user()<br />
Delete: remove_user()<br />

Transactions:<br />
Create: borrow_book(), return_book()<br />
Read: search_transaction_by_id(), search_transaction_by_user_id()<br />
Update: update_transaction_status()<br />
Delete: remove_transaction()<br />

# Performance Report:

Insertion Time<br />

Hash Tables: The time taken to insert book and user data into in-memory hash tables was approximately 0.0018 seconds. This demonstrates the efficiency of hash tables for insertions due to their constant-time complexity.

SQLite Database: The insertion time for SQLite isn't explicitly measured in the code. However, we can infer its performance from the overall execution time of adding 1000 books. It took approximately 2.54 seconds to generate and store 1000 books in SQLite. This suggests that SQLite insertion time is longer than hash table insertion, but this difference can be considered insignificant when dealing with 1000 books or less.<br />

Query Time<br />

Hash Tables: Hash tables excel in query performance, especially for retrieving data by a unique key.<br />
Average query time for book by ID: 0.000002 seconds<br />
Average query time for book by ISBN: 0.000001 seconds<br />
Average query time for user by ID: 0.000001 seconds<br />

SQLite Database: While SQLite's query time is generally slower than hash tables, it remains reasonably fast for smaller datasets.<br />
Average query time for book by ID: 0.000027 seconds<br />
Average query time for book by ISBN: 0.000015 seconds<br />
Average query time for user by ID: 0.000015 seconds<br />

Range-Based Retrieval<br />

The range-based retrieval performance was observed by querying Transactions table within a date range. This query execution took approximately 0.0001 seconds, indicating efficient range-based filtering.
