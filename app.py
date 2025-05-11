from flask import Flask, render_template, request, redirect, session, make_response
from auth import signup, login, reset_password
from transactions import (
    add_transaction, get_user_transactions, delete_transaction
)
from reports import get_summary
from lend import (
    request_lend, get_lend_requests, mark_as_paid,
    get_friend_usernames, respond_to_lend_request
)
from notifications import notify_user
from categories import add_category, get_categories
from friends import add_friend, get_friends
from db import get_connection

from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        if signup(request.form['username'], request.form['password'], request.form['email']):
            notify_user("Signup Successful", "Welcome to Expense Tracker!")
            return redirect('/login')
        else:
            return render_template('signup.html', error='Signup failed')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user_id = login(request.form['username'], request.form['password'])
        if user_id:
            session['user_id'] = user_id
            session['username'] = request.form['username']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Login failed')
    return render_template('login.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_page():
    if request.method == 'POST':
        if reset_password(request.form['email'], request.form['new_password']):
            notify_user("Password Reset", "Your password was successfully updated.")
            return redirect('/login')
        else:
            return render_template('forgot_password.html', error='Reset failed')
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    transactions = get_user_transactions(session['user_id'])
    return render_template('dashboard.html', username=session['username'], transactions=transactions)

@app.route('/add', methods=['GET', 'POST'])
def add_page():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        add_transaction(session['user_id'], request.form['amount'], request.form['type'],
                        request.form['category'], request.form['description'], request.form['date'])
        notify_user("Transaction Added", "Your new transaction was recorded.")
        return redirect('/dashboard')
    return render_template('add_transaction.html')

@app.route('/delete_transaction/<int:txn_id>')
def delete_transaction_route(txn_id):
    if 'user_id' not in session:
        return redirect('/login')
    delete_transaction(txn_id, session['user_id'])
    return redirect('/dashboard')

@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect('/login')
    data = get_summary(session['user_id'])
    return render_template('report.html', **data)

@app.route('/report/pdf', methods=['POST'])
def download_report_pdf():
    if 'user_id' not in session:
        return redirect('/login')
    data = get_summary(session['user_id'])
    rendered = render_template('report_pdf_template.html', **data)
    pdf = BytesIO()
    pisa.CreatePDF(rendered, dest=pdf)
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=monthly_summary.pdf'
    return response

@app.route('/lend', methods=['GET', 'POST'])
def lend():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        request_lend(session['user_id'], request.form['to_username'], request.form['amount'])
        notify_user("Lend Request", "You requested money from your friend.")
        return redirect('/lend')
    requests = get_lend_requests(session['user_id'])
    friends = get_friend_usernames(session['user_id'])
    return render_template('lend.html', requests=requests, friends=friends)

@app.route('/pay/<int:request_id>')
def pay_now(request_id):
    mark_as_paid(request_id)
    notify_user("Payment Confirmed", "You marked a lend request as paid.")
    return redirect('/lend')

@app.route('/respond/<int:request_id>/<string:action>')
def respond_lend_request_route(request_id, action):
    respond_to_lend_request(request_id, action)
    notify_user("Lend Response", f"You {'accepted' if action == 'accept' else 'declined'} a request.")
    return redirect('/lend')

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        add_category(session['user_id'], request.form['category'])
        notify_user("Category Added", "A new category has been added.")
        return redirect('/categories')
    categories = get_categories(session['user_id'])
    return render_template('categories.html', categories=categories)

@app.route('/friends', methods=['GET', 'POST'])
def friends():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        add_friend(session['user_id'], request.form['friend_username'])
        notify_user("Friend Added", "You added a new friend.")
        return redirect('/friends')
    friends = get_friends(session['user_id'])
    return render_template('friends.html', friends=friends)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
