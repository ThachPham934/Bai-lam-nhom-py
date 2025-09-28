import re
import sqlite3
import datetime
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your secret key'


def get_db_connection():
    conn = sqlite3.connect('library-system.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['id']
            session['name'] = user['first_name']
            session['email'] = user['email']
            session['role'] = user['role']
            message = 'Logged in successfully !'
            return redirect(url_for('dashboard'))
        else:
            message = 'Please enter correct email / password !'
        conn.close()
    return render_template('login.html', message=message)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        return render_template("dashboard.html")
    return redirect(url_for('login'))


@app.route("/users", methods=['GET', 'POST'])
def users():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        conn.close()
        return render_template("users.html", users=users)
    return redirect(url_for('login'))


@app.route("/save_user", methods=['GET', 'POST'])
def save_user():
    msg = ''
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST' and 'role' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            role = request.form['role']
            action = request.form['action']

            if action == 'updateUser':
                userId = request.form['userid']
                cursor.execute('UPDATE user SET first_name= ?, last_name= ?, email= ?, role= ? WHERE id = ?',
                               (first_name, last_name, email, role, userId))
                conn.commit()
            else:
                password = request.form['password']
                cursor.execute('INSERT INTO user (first_name, last_name, email, password, role) VALUES (?, ?, ?, ?, ?)',
                               (first_name, last_name, email, password, role))
                conn.commit()
            conn.close()
            return redirect(url_for('users'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        conn.close()
        return redirect(url_for('users'))
    return redirect(url_for('login'))


@app.route("/edit_user", methods=['GET', 'POST'])
def edit_user():
    msg = ''
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE id = ?', (editUserId,))
        users = cursor.fetchall()
        conn.close()
        return render_template("edit_user.html", users=users)
    return redirect(url_for('login'))


@app.route("/view_user", methods=['GET', 'POST'])
def view_user():
    if 'loggedin' in session:
        viewUserId = request.args.get('userid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE id = ?', (viewUserId,))
        user = cursor.fetchone()
        conn.close()
        return render_template("view_user.html", user=user)
    return redirect(url_for('login'))


@app.route("/password_change", methods=['GET', 'POST'])
def password_change():
    message = ''
    if 'loggedin' in session:
        changePassUserId = request.args.get('userid')
        if request.method == 'POST' and 'password' in request.form and 'confirm_pass' in request.form and 'userid' in request.form:
            password = request.form['password']
            confirm_pass = request.form['confirm_pass']
            userId = request.form['userid']
            if not password or not confirm_pass:
                message = 'Please fill out the form !'
            elif password != confirm_pass:
                message = 'Confirm password is not equal!'
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE user SET password = ? WHERE id = ?', (password, userId))
                conn.commit()
                conn.close()
                message = 'Password updated !'
        elif request.method == 'POST':
            message = 'Please fill out the form !'
        return render_template("password_change.html", message=message, changePassUserId=changePassUserId)
    return redirect(url_for('login'))


@app.route("/delete_user", methods=['GET'])
def delete_user():
    if 'loggedin' in session:
        deleteUserId = request.args.get('userid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user WHERE id=?', (deleteUserId,))
        conn.commit()
        conn.close()
        return redirect(url_for('users'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ?', (email,))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user (first_name, email, password) VALUES (?, ?, ?)', (userName, email, password))
            conn.commit()
            mesage = 'You have successfully registered !'
        conn.close()
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage=mesage)

# Manage Books
@app.route("/books", methods=['GET', 'POST'])
def books():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT book.bookid, book.picture, book.name, book.status, book.isbn, book.no_of_copy, book.updated_on, author.name AS author_name, category.name AS category_name, rack.name AS rack_name, publisher.name AS publisher_name FROM book LEFT JOIN author ON author.authorid = book.authorid LEFT JOIN category ON category.categoryid = book.categoryid LEFT JOIN rack ON rack.rackid = book.rackid LEFT JOIN publisher ON publisher.publisherid = book.publisherid")
        books = cursor.fetchall()

        cursor.execute("SELECT authorid, name FROM author")
        authors = cursor.fetchall()

        cursor.execute("SELECT publisherid, name FROM publisher")
        publishers = cursor.fetchall()

        cursor.execute("SELECT categoryid, name FROM category")
        categories = cursor.fetchall()

        cursor.execute("SELECT rackid, name FROM rack")
        racks = cursor.fetchall()

        conn.close()
        return render_template("books.html", books=books, authors=authors, publishers=publishers, categories=categories, racks=racks)
    return redirect(url_for('login'))

@app.route("/edit_book", methods=['GET', 'POST'])
def edit_book():
    msg = ''
    if 'loggedin' in session:
        editBookId = request.args.get('bookid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT book.bookid, book.picture, book.name, book.status, book.isbn, book.no_of_copy, book.updated_on, book.authorid, book.categoryid, book.rackid, book.publisherid, author.name AS author_name, category.name AS category_name, rack.name AS rack_name, publisher.name AS publisher_name FROM book LEFT JOIN author ON author.authorid = book.authorid LEFT JOIN category ON category.categoryid = book.categoryid LEFT JOIN rack ON rack.rackid = book.rackid LEFT JOIN publisher ON publisher.publisherid = book.publisherid WHERE book.bookid = ?', (editBookId,))
        books = cursor.fetchall()

        cursor.execute("SELECT authorid, name FROM author")
        authors = cursor.fetchall()

        cursor.execute("SELECT publisherid, name FROM publisher")
        publishers = cursor.fetchall()

        cursor.execute("SELECT categoryid, name FROM category")
        categories = cursor.fetchall()

        cursor.execute("SELECT rackid, name FROM rack")
        racks = cursor.fetchall()

        conn.close()
        return render_template("edit_books.html", books=books, authors=authors, publishers=publishers, categories=categories, racks=racks)
    return redirect(url_for('login'))

@app.route("/save_book", methods=['GET', 'POST'])
def save_book():
    msg = ''
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT book.bookid, book.picture, book.name, book.status, book.isbn, book.no_of_copy, book.updated_on, author.name AS author_name, category.name AS category_name, rack.name AS rack_name, publisher.name AS publisher_name FROM book LEFT JOIN author ON author.authorid = book.authorid LEFT JOIN category ON category.categoryid = book.categoryid LEFT JOIN rack ON rack.rackid = book.rackid LEFT JOIN publisher ON publisher.publisherid = book.publisherid")
        books = cursor.fetchall()
        if request.method == 'POST' and 'name' in request.form and 'author' in request.form and 'publisher' in request.form and 'category' in request.form and 'rack' in request.form:
            bookName = request.form['name']
            isbn = request.form['isbn']
            no_of_copy = request.form['no_of_copy']
            author = request.form['author']
            publisher = request.form['publisher']
            category = request.form['category']
            rack = request.form['rack']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateBook':
                bookId = request.form['bookid']
                cursor.execute('UPDATE book SET name=?, status=?, isbn=?, no_of_copy=?, categoryid=?, authorid=?, rackid=?, publisherid=? WHERE bookid=?', (bookName, status, isbn, no_of_copy, category, author, rack, publisher, bookId))
                conn.commit()
            else:
                picture = ''  # hoặc 'default.jpg' nếu bạn có ảnh mặc định
                cursor.execute(
                    'INSERT INTO book (name, picture, status, isbn, no_of_copy, categoryid, authorid, rackid, publisherid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (bookName, picture, status, isbn, no_of_copy, category, author, rack, publisher)
                )
                conn.commit()
            conn.close()
            return redirect(url_for('books'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        conn.close()
        return render_template("books.html", msg=msg, books=books)
    return redirect(url_for('login'))

@app.route("/delete_book", methods=['GET'])
def delete_book():
    if 'loggedin' in session:
        deleteBookId = request.args.get('bookid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM book WHERE bookid=?', (deleteBookId,))
        conn.commit()
        conn.close()
        return redirect(url_for('books'))
    return redirect(url_for('login'))

@app.route("/list_issue_book", methods=['GET', 'POST'])
def list_issue_book():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT issued_book.issuebookid, issued_book.issue_date_time, issued_book.expected_return_date, issued_book.return_date_time, issued_book.status, book.name AS book_name, book.isbn, user.first_name, user.last_name FROM issued_book LEFT JOIN book ON book.bookid = issued_book.bookid LEFT JOIN user ON user.id = issued_book.userid")
        issue_books = cursor.fetchall()

        cursor.execute("SELECT bookid, name FROM book")
        books = cursor.fetchall()

        cursor.execute("SELECT id, first_name, last_name FROM user")
        users = cursor.fetchall()

        conn.close()
        return render_template("issue_book.html", issue_books=issue_books, books=books, users=users)
    return redirect(url_for('login'))


@app.route("/save_issue_book", methods=['GET', 'POST'])
def save_issue_book():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT issued_book.issuebookid, issued_book.issue_date_time, issued_book.expected_return_date, issued_book.return_date_time, issued_book.status, book.name AS book_name, book.isbn, user.first_name, user.last_name FROM issued_book LEFT JOIN book ON book.bookid = issued_book.bookid LEFT JOIN user ON user.id = issued_book.userid")
        issue_books = cursor.fetchall()

        if request.method == 'POST' and 'book' in request.form and 'users' in request.form and 'expected_return_date' in request.form and 'return_date' in request.form and 'status' in request.form:
            bookId = request.form['book']
            userId = request.form['users']
            expected_return_date = request.form['expected_return_date']
            return_date = request.form['return_date']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateIssueBook':
                issuebookid = request.form['issueBookId']
                cursor.execute('UPDATE issued_book SET bookid=?, userid=?, expected_return_date=?, return_date_time=?, status=? WHERE issuebookid=?', (bookId, userId, expected_return_date, return_date, status, issuebookid))
                conn.commit()
            else:
                issue_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    'INSERT INTO issued_book (bookid, userid, issue_date_time, expected_return_date, return_date_time, status) VALUES (?, ?, ?, ?, ?, ?)',
                    (bookId, userId, issue_date_time, expected_return_date, return_date, status)
                )
                conn.commit()
            conn.close()
            return redirect(url_for('list_issue_book'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return redirect(url_for('list_issue_book'))
    return redirect(url_for('login'))

@app.route("/edit_issue_book", methods=['GET', 'POST'])
def edit_issue_book():
    msg = ''
    if 'loggedin' in session:
        issuebookid = request.args.get('issuebookid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT issued_book.issuebookid, issued_book.issue_date_time, issued_book.expected_return_date, issued_book.return_date_time, issued_book.bookid, issued_book.userid, issued_book.status, book.name AS book_name, book.isbn, user.first_name, user.last_name FROM issued_book LEFT JOIN book ON book.bookid = issued_book.bookid LEFT JOIN user ON user.id = issued_book.userid WHERE issued_book.issuebookid=?', (issuebookid,))
        issue_books = cursor.fetchall()

        cursor.execute("SELECT bookid, name FROM book")
        books = cursor.fetchall()

        cursor.execute("SELECT id, first_name, last_name FROM user")
        users = cursor.fetchall()

        conn.close()
        return render_template("edit_issue_book.html", issue_books=issue_books, books=books, users=users)
    return redirect(url_for('login'))

@app.route("/delete_issue_book", methods=['GET'])
def delete_issue_book():
    if 'loggedin' in session:
        issuebookid = request.args.get('issuebookid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM issued_book WHERE issuebookid=?', (issuebookid,))
        conn.commit()
        conn.close()
        return redirect(url_for('list_issue_book'))
    return redirect(url_for('login'))

# Manage Category
@app.route("/category", methods=['GET', 'POST'])
def category():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT categoryid, name, status FROM category")
        categories = cursor.fetchall()
        conn.close()
        return render_template("category.html", categories=categories, addCategoryForm=0)
    return redirect(url_for('login'))

@app.route("/saveCategory", methods=['GET', 'POST'])
def saveCategory():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST' and 'name' in request.form and 'status' in request.form:
            name = request.form['name']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateCategory':
                categoryId = request.form['categoryid']
                cursor.execute('UPDATE category SET name=?, status=? WHERE categoryid=?', (name, status, categoryId))
                conn.commit()
            else:
                cursor.execute('INSERT INTO category (name, status) VALUES (?, ?)', (name, status))
                conn.commit()
            conn.close()
            return redirect(url_for('category'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return redirect(url_for('category'))

    return redirect(url_for('login'))

@app.route("/editCategory", methods=['GET', 'POST'])
def editCategory():
    if 'loggedin' in session:
        categoryid = request.args.get('categoryid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT categoryid, name, status FROM category WHERE categoryid=?', (categoryid,))
        categories = cursor.fetchall()
        conn.close()
        return render_template("edit_category.html", categories=categories)
    return redirect(url_for('login'))

@app.route("/delete_category", methods=['GET'])
def delete_category():
    if 'loggedin' in session:
        categoryid = request.args.get('categoryid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM category WHERE categoryid=?', (categoryid,))
        conn.commit()
        conn.close()
        return redirect(url_for('category'))
    return redirect(url_for('login'))


# Manage Author   
@app.route("/author", methods=['GET', 'POST'])
def author():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT authorid, name, status FROM author")
        authors = cursor.fetchall()
        conn.close()
        return render_template("author.html", authors=authors)
    return redirect(url_for('login'))

@app.route("/saveAuthor", methods=['GET', 'POST'])
def saveAuthor():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST' and 'name' in request.form and 'status' in request.form:
            name = request.form['name']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateAuthor':
                authorId = request.form['authorid']
                cursor.execute('UPDATE author SET name=?, status=? WHERE authorid=?', (name, status, authorId))
                conn.commit()
            else:
                cursor.execute('INSERT INTO author (name, status) VALUES (?, ?)', (name, status))
                conn.commit()
            conn.close()
            return redirect(url_for('author'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        conn.close()
        return redirect(url_for('author'))

    return redirect(url_for('login'))

@app.route("/editAuthor", methods=['GET', 'POST'])
def editAuthor():
    if 'loggedin' in session:
        authorid = request.args.get('authorid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT authorid, name, status FROM author WHERE authorid=?', (authorid,))
        authors = cursor.fetchall()
        conn.close()
        return render_template("edit_author.html", authors=authors)
    return redirect(url_for('login'))

@app.route("/delete_author", methods=['GET'])
def delete_author():
    if 'loggedin' in session:
        authorid = request.args.get('authorid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM author WHERE authorid=?', (authorid,))
        conn.commit()
        conn.close()
        return redirect(url_for('author'))
    return redirect(url_for('login'))

# Manage publishers
@app.route("/publisher", methods=['GET', 'POST'])
def publisher():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT publisherid, name, status FROM publisher")
        publishers = cursor.fetchall()
        conn.close()
        return render_template("publisher.html", publishers=publishers)
    return redirect(url_for('login'))

@app.route("/savePublisher", methods=['GET', 'POST'])
def savePublisher():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST' and 'name' in request.form and 'status' in request.form:
            name = request.form['name']
            status = request.form['status']
            action = request.form['action']

            if action == 'updatePublisher':
                publisherid = request.form['publisherid']
                cursor.execute('UPDATE publisher SET name=?, status=? WHERE publisherid=?', (name, status, publisherid))
                conn.commit()
            else:
                cursor.execute('INSERT INTO publisher (name, status) VALUES (?, ?)', (name, status))
                conn.commit()
            conn.close()
            return redirect(url_for('publisher'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        conn.close()
        return redirect(url_for('publisher'))

    return redirect(url_for('login'))

@app.route("/editPublisher", methods=['GET', 'POST'])
def editPublisher():
    if 'loggedin' in session:
        publisherid = request.args.get('publisherid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT publisherid, name, status FROM publisher WHERE publisherid=?', (publisherid,))
        publishers = cursor.fetchall()
        conn.close()
        return render_template("edit_publisher.html", publishers=publishers)
    return redirect(url_for('login'))

@app.route("/delete_publisher", methods=['GET'])
def delete_publisher():
    if 'loggedin' in session:
        publisherid = request.args.get('publisherid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM publisher WHERE publisherid=?', (publisherid,))
        conn.commit()
        conn.close()
        return redirect(url_for('publisher'))
    return redirect(url_for('login'))

# Manage Rack
@app.route("/rack", methods=['GET', 'POST'])
def rack():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT rackid, name, status FROM rack")
        racks = cursor.fetchall()
        conn.close()
        return render_template("rack.html", racks=racks)
    return redirect(url_for('login'))

@app.route("/saveRack", methods=['GET', 'POST'])
def saveRack():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST' and 'name' in request.form and 'status' in request.form:
            name = request.form['name']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateRack':
                rackid = request.form['rackid']
                cursor.execute('UPDATE rack SET name=?, status=? WHERE rackid=?', (name, status, rackid))
                conn.commit()
            else:
                cursor.execute('INSERT INTO rack (name, status) VALUES (?, ?)', (name, status))
                conn.commit()
            conn.close()
            return redirect(url_for('rack'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        conn.close()
        return redirect(url_for('rack'))

    return redirect(url_for('login'))

@app.route("/editRack", methods=['GET', 'POST'])
def editRack():
    if 'loggedin' in session:
        rackid = request.args.get('rackid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT rackid, name, status FROM rack WHERE rackid=?', (rackid,))
        racks = cursor.fetchall()
        conn.close()
        return render_template("edit_rack.html", racks=racks)
    return redirect(url_for('login'))

@app.route("/delete_rack", methods=['GET'])
def delete_rack():
    if 'loggedin' in session:
        rackid = request.args.get('rackid')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM rack WHERE rackid=?', (rackid,))
        conn.commit()
        conn.close()
        return redirect(url_for('rack'))
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

