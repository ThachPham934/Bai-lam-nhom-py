import sqlite3

# Kết nối tới cơ sở dữ liệu SQLite (nó sẽ được tạo nếu chưa tồn tại)
conn = sqlite3.connect('library-system.db')
c = conn.cursor()

# Tạo bảng `author`
c.execute('''CREATE TABLE IF NOT EXISTS author (
  authorid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL
)''')

# Chèn dữ liệu vào bảng `author`
c.executemany('INSERT INTO author (authorid, name, status) VALUES (?, ?, ?)', [
  (1, 'Phạm Chí Thạch', 'Enable'),
  (2, 'Đinh Văn Phúc', 'Enable'),
  (3, 'Nguyễn Quốc Dân An', 'Enable')
])

# Tạo bảng `book`
c.execute('''CREATE TABLE IF NOT EXISTS book (
  bookid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  categoryid INTEGER NOT NULL,
  authorid INTEGER NOT NULL,
  rackid INTEGER NOT NULL,
  name TEXT NOT NULL,
  picture TEXT NOT NULL,
  publisherid INTEGER NOT NULL,
  isbn TEXT NOT NULL,
  no_of_copy INTEGER NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL,
  added_on TEXT NOT NULL DEFAULT (datetime('now')),
  updated_on TEXT NOT NULL DEFAULT (datetime('now'))
)''')

# Chèn dữ liệu vào bảng `book`
c.executemany('''INSERT INTO book (bookid, categoryid, authorid, rackid, name, picture, publisherid, isbn, no_of_copy, status, added_on, updated_on) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [
  (1, 2, 2, 2, 'The Joy of PHP Programming', 'joy-php.jpg', 8, 'B00BALXN70', 10, 'Enable', '2022-06-12 11:12:48', '2022-06-12 11:13:27'),
  (2, 2, 3, 2, 'Head First PHP & MySQL', 'header-first-php.jpg', 9, '0596006306', 10, 'Enable', '2022-06-12 11:16:01', '2022-06-12 11:16:01'),
  (3, 2, 2, 1, 'dsgsdgsd', '', 7, 'sdfsd2334', 23, 'Enable', '2022-06-12 13:29:14', '2022-06-12 13:29:14'),
  (7, 1, 2, 0, 'eeeeeebook', '', 2, 'hfdfhdfhd', 2, 'Enable', '2023-03-19 16:27:17', '2023-03-19 16:27:17'),
  (8, 1, 2, 0, 'aaaaaaaaaaaaaa', '', 2, 'bbbbbbbbbbbbbbbbbb', 2, 'Enable', '2023-03-19 17:37:56', '2023-03-19 17:37:56'),
  (9, 1, 2, 1, 'bbbbbbbbbbbbbb', '', 2, '4346436463463', 2, 'Enable', '2023-03-25 14:44:18', '2023-03-25 14:44:18')
])

# Tạo bảng `category`
c.execute('''CREATE TABLE IF NOT EXISTS category (
  categoryid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL
)''')

# Chèn dữ liệu vào bảng `category`
c.executemany('INSERT INTO category (categoryid, name, status) VALUES (?, ?, ?)', [
  (1, 'Web Design', 'Enable'),
  (2, 'Programming', 'Enable'),
  (3, 'Commerce', 'Enable'),
  (4, 'Math', 'Enable'),
  (6, 'Web Development', 'Enable')
])

# Tạo bảng `issued_book`
c.execute('''CREATE TABLE IF NOT EXISTS issued_book (
  issuebookid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  bookid INTEGER NOT NULL,
  userid INTEGER NOT NULL,
  issue_date_time TEXT NOT NULL DEFAULT (datetime('now')),
  expected_return_date TEXT NOT NULL,
  return_date_time TEXT NOT NULL,
  status TEXT CHECK(status IN ('Issued', 'Returned', 'Not Return')) NOT NULL
)''')

# Chèn dữ liệu vào bảng `issued_book`
c.executemany('INSERT INTO issued_book (issuebookid, bookid, userid, issue_date_time, expected_return_date, return_date_time, status) VALUES (?, ?, ?, ?, ?, ?, ?)', [
  (1, 2, 2, '2022-06-12 15:33:45', '2022-06-15 16:27:59', '2022-06-16 16:27:59', 'Not Return'),
  (3, 1, 2, '2022-06-12 18:46:07', '2022-06-30 18:46:02', '2022-06-12 18:46:14', 'Returned'),
  (4, 7, 2, '2023-03-25 14:32:57', '2023-03-25 14:32:47', '2023-03-26 14:32:51', 'Issued')
])

# Tạo bảng `publisher`
c.execute('''CREATE TABLE IF NOT EXISTS publisher (
  publisherid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL
)''')

# Chèn dữ liệu vào bảng `publisher`
c.executemany('INSERT INTO publisher (publisherid, name, status) VALUES (?, ?, ?)', [
  (2, 'Amazon publishing', 'Enable'),
  (3, 'Penguin books ltd.', 'Enable'),
  (4, 'Vintage Publishing', 'Enable'),
  (5, 'Macmillan Publishers', 'Enable'),
  (6, 'Simon & Schuster', 'Enable'),
  (7, 'HarperCollins', 'Enable'),
  (8, 'Plum Island', 'Enable'),
  (9, 'O’Reilly', 'Enable')
])

# Tạo bảng `rack`
c.execute('''CREATE TABLE IF NOT EXISTS rack (
  rackid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL DEFAULT 'Enable'
)''')

# Chèn dữ liệu vào bảng `rack`
c.executemany('INSERT INTO rack (rackid, name, status) VALUES (?, ?, ?)', [
  (1, 'R1', 'Enable'),
  (2, 'R2', 'Enable')
])

# Tạo bảng `user`
c.execute('''CREATE TABLE IF NOT EXISTS user (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  first_name TEXT,
  last_name TEXT,
  email TEXT UNIQUE,
  password TEXT,
  role TEXT CHECK(role IN ('admin', 'user')) DEFAULT 'admin'
)''')

# Chèn dữ liệu vào bảng `user`
c.executemany('INSERT INTO user (id, first_name, last_name, email, password, role) VALUES (?, ?, ?, ?, ?, ?)', [
  (2, 'Mark', 'Wood', 'mark@webdamn.com', '123', 'user'),
  (3, 'George', 'Smith', 'george@webdamn.com', '123', 'admin'),
  (4, 'Adam', None, 'adam@webdamn.com', '123', 'admin'),
  (6, 'aaa', 'bbbbb', 'ab@webdamn.com', '123', 'user')
])

# Lưu các thay đổi và đóng kết nối
conn.commit()
conn.close()
