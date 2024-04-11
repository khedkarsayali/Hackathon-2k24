from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import secrets
import datetime

from flask_migrate import Migrate
from flask_mail import Mail, Message
import random
from reportlab.pdfgen import canvas
from io import BytesIO
import base64


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/datahub'  # MySQL database URL


app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '587',
    MAIL_USE_TLS = True,
    MAIL_USERNAME = 'hackhustler58@gmail.com',
    MAIL_PASSWORD = 'qeic vozg gtlb rhvw',
    MAIL_DEFAULT_SENDER = 'hackhustler58@gmail.com' 
    )

db = SQLAlchemy(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()
    
# Configure session interface (Example using SQLAlchemy)
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db  # SQLAlchemy instance

app.config['SECRET_KEY'] = 'HackHustlers'  # Secret key for session management

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hackhustler58@gmail.com'
app.config['MAIL_PASSWORD'] = 'hackhustler@6'
app.config['MAIL_DEFAULT_SENDER'] = 'hackhustler58@gmail.com'

mail = Mail(app)

@app.route('/')
def my_index():
    return render_template("index.html", token="Hello Sayali")



mail = Mail(app)

class Event(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(500))
    manager_name = db.Column(db.String(500))
    club_name = db.Column(db.String(100), nullable=True)
    event_date = db.Column(db.String(100))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    hall_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    ph_num = db.Column(db.BigInteger)
    department = db.Column(db.String(100), nullable=True)
    request = db.Column(db.DateTime)
    status = db.Column(db.String(255))


class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    contactNo = db.Column(db.String(20), nullable=True)
    clubname = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)


class Admin(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    


class Venue(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    capacity = db.Column(db.Integer)
    features = db.Column(db.String(255))


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query the database to find the user with the provided email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # If user exists, check if password matches
            if user.password == password:
                # If password matches, set session and redirect to dashboard
                session['user_id'] = user.sno
                flash('Login successful!', 'success')  # Flash message for successful login
                return redirect(url_for('dashboard'))
            else:
                # If password doesn't match, show error message
                flash('Incorrect password. Please try again.', 'error')
                return render_template('index.html')
        else:
            # If user doesn't exist, show error message
            flash('Email not found.', 'error')
            return render_template('index.html')
    
    return render_template('index.html', error_messages={})


@app.route('/adminlogin', methods=['POST'])
def adminlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query the database to find the user with the provided email
        admin = Admin.query.filter_by(email=email).first()
        
        if admin:
            # If user exists, check if password matches
            if admin.password == password:
                # If password matches, set session and redirect to dashboard
                session['admin_id'] = admin.sno
                flash('Login successful!', 'success')  # Flash message for successful login
                return redirect(url_for('admindashboard'))
            else:
                # If password doesn't match, show error message
                flash('Incorrect password. Please try again.', 'error')
                
        else:
            # If user doesn't exist, show error message
            flash('Email not found.', 'error')
    
    return render_template('index.html', error_messages={})
            

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        # If user is logged in, render dashboard page
        return render_template('dashboard.html')
    else:
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))

@app.route('/admindashboard')
def admindashboard():
    if 'admin_id' in session:
        # If admin is logged in, render admindashboard page
        return render_template('admindashboard.html')
    else:
        # If admin is not logged in, redirect to adminlogin page
        return redirect(url_for('adminlogin'))
    

# Route for displaying user profile
@app.route('/profile')
def profile():
    # Assuming the user is authenticated and you have their user ID stored in session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return render_template('userProfile.html', user=user)
    # If user is not authenticated or not found in the database, redirect to login
    return redirect(url_for('login'))

# Password reset token model
class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)
    token = db.Column(db.String(120), nullable=False)


# Route for updating user profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            # Update user information based on form submission
            user.name = request.form['name']
            user.contactNo = request.form['contactNo']
            user.clubname = request.form['clubname']
            user.department = request.form['department']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))


# Route to display form for verifying current password
@app.route('/verify_password', methods=['GET', 'POST'])
def verify_password():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                entered_password = request.form['current_password']
                if user.password == entered_password:
                    session['verified'] = True
                    return redirect(url_for('change_password'))
                else:
                    flash('Incorrect password. Please try again.', 'error')
                    return redirect(url_for('verify_password'))
        flash('User not authenticated.', 'error')
    return render_template('verify_password.html')

# Route for changing password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if session.get('verified'):
        if request.method == 'POST':
            user_id = session.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user:
                    new_password = request.form['new_password']
                    user.password = new_password
                    db.session.commit()
                    flash('Password changed successfully!', 'success')
                    session.pop('verified', None)  # Remove the 'verified' flag from session
                    return redirect(url_for('profile'))
        return render_template('change_password.html')
    else:
        flash('Please verify your current password first.', 'error')
        return redirect(url_for('verify_password'))


@app.route('/go_to_add_user', methods=['GET'])
def go_to_add_user():
    # Fetch all users from the database
    users = User.query.all()
    return render_template('adminAddUsers.html', users=users)
        
# Route to handle user search
@app.route('/search_users', methods=['GET'])
def search_users():
    search_term = request.args.get('search', '')
    # Search users by email
    users = User.query.filter(User.email.contains(search_term)).all()
    return render_template('adminAddUsers.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        email = request.form['email']
        # Default password
        password = 'coep123'
        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists!', 'error')
        else:
            # Create a new user object
            new_user = User(email=email, password=password)
            
            try:
                # Add the new user to the database
                db.session.add(new_user)
                db.session.commit()
                flash('User added successfully!', 'success')
            except Exception as e:
                # Rollback changes if an error occurs
                db.session.rollback()
                flash(f'Error adding user: {str(e)}', 'error')
            finally:
                # Close the database session
                db.session.close()

    return render_template('adminAddUsers.html')

if __name__ == '__main__':
    app.run(debug=True)




@app.route('/')
def index():
    return render_template('index.html')



#@app.route("/send", methods=['GET', 'POST'])
#def send_mail():
 #   error=None
  #  if request.method == 'POST':
   #     email = request.form.get('recipient')
   #     subject = request.form.get('subject')
   #     message = request.form.get('message')  # Retrieve message from form
   #     if not email:
   #         error="Enter your email"
   #     else:
   #         mail.send_message(subject,  # Use subject as the subject of the email
   #                           sender=("Your Name", "your-email@example.com"),
   #                           recipients=[email],  # Pass email address as a list
   #                           body=message)  # Use message as the body of the email
   #         return render_template('index.html')
   # return render_template('index.html',error=error)

def generate_pdf():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Hello, this is an auto-generated PDF!")
    p.save()
    buffer.seek(0)
    return buffer


@app.route("/send", methods=['GET', 'POST'])
def send_mail():
    error = None
    if request.method == 'POST':
        email = request.form.get('recipient')
        subject = request.form.get('subject')
        message = request.form.get('message')
        if not email:
            error = "Enter your email"
        else:
            # Generate PDF
            pdf_buffer = generate_pdf()

            # Attach PDF to email
            msg = Message(subject,
                          sender=("Your Name", "hackhustler58@gmail.com"),
                          recipients=[email])
            msg.body = message

            
            msg.attach("document.pdf", "application/pdf", pdf_buffer.getvalue())

            # Send email
            mail.send(msg)
            return render_template('mail.html')
    return render_template('mail.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)
