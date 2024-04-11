from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import login_required
import secrets
import datetime
import random
import json
from sqlalchemy import or_

from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/datahub'  # MySQL database URL
db = SQLAlchemy(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()
    
# Configure session interface (Example using SQLAlchemy)
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db  # SQLAlchemy instance

app.config['SECRET_KEY'] = 'HackHustlers'  # Secret key for session management

# Configure email settings
app.config.update(
    MAIL_SERVER = 'smtp.example.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = 'hackhustler58@gmail.com',
    MAIL_PASSWORD = 'qeic vozg gtlb rhvw',
    MAIL_DEFAULT_SENDER = 'hackhustler58@gmail.com'
)

mail = Mail(app)

@app.route('/')
def my_index():
    return render_template("index.html", token="Hello Sayali")




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
    return render_template('adminAddUsers.html', users=users,search_term=search_term)

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

@app.route("/forgotpass", methods=['GET', 'POST'])
def forgot():
    error=None
    if request.method == 'POST':
        email=request.form.get('email')
        if not email:
            error="Enter your email"
        else:
            otp = ''.join(random.choices('0123456789', k=5))
            mail.send_message('OTP Request',
                sender="hackhustlers.com",
                recipients=[email],  # Pass email address as a list
                body=f"Your OTP is {otp}.\n Do not share this OTP with anyone.")
            # error="OTP sent to your email"
            return render_template('file4(OTP).html')
    return render_template('index.html',error=error)




#vaishnavi code : 

@app.route('/approve/<int:event_id>')
def approve_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('hall_requests'))

# Route to handle reject action
@app.route('/reject/<int:event_id>')
def reject_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('hall_requests'))




@app.route('/')
def home():
    return "Hello"





@app.route('/view_event/<int:event_id>')
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    

    return render_template('view.html', event=event)





from datetime import datetime

@app.route('/hall_requests', methods=['GET', 'POST'])
def hall_requests():
    search_query = request.args.get('q', '')

    # Query the database to retrieve all requests
    all_hall_requests = Event.query.filter(Event.event_date >= datetime.now())

    # Filter events based on search criteria
    if search_query:
        all_hall_requests = all_hall_requests.filter(
            or_(
                Event.manager_name.ilike(f'%{search_query}%'),
                Event.event_name.ilike(f'%{search_query}%'),
                Event.department.ilike(f'%{search_query}%'),
                Event.club_name.ilike(f'%{search_query}%')
            )
        )

    all_hall_requests = all_hall_requests.all()

    # Render the template with the filtered requests data
    return render_template('display.html', all_hall_requests=all_hall_requests)

@app.route('/all_events')
def all_events():
    # Query all events from the database
    # all_events = Event.query.all()
    all_events = Event.query.filter(Event.event_date >= datetime.now()).all()
    return render_template('display.html', all_hall_requests=all_events, category='All Events')

@app.route('/approved_events')
def approved_events():
    # Query approved events from the database
    # approved_events = Event.query.filter_by(status='Accepted').all()
    approved_events = Event.query.filter_by(status='Accepted').filter(Event.event_date >= datetime.now()).all()
    return render_template('display.html', all_hall_requests=approved_events, category='Approved Events')




@app.route('/pending_events')
def pending_events():
    # Query pending events from the database
    # pending_events = Event.query.filter_by(status='Pending').all()
    pending_events = Event.query.filter_by(status='Pending').filter(Event.event_date >= datetime.now()).all()
    return render_template('display.html', all_hall_requests=pending_events, category='Pending Events')

@app.route('/rejected_events')
def rejected_events():
    # Query rejected events from the database
    # rejected_events = Event.query.filter_by(status='Rejected').all()
    rejected_events = Event.query.filter_by(status='Rejected').filter(Event.event_date >= datetime.now()).all()
    return render_template('display.html', all_hall_requests=rejected_events, category='Rejected Events')



@app.route('/hall_requests_user', methods=['GET', 'POST'])
@login_required  # Ensure that the user is logged in
def hall_requests_user():
    search_query = request.args.get('q', '')

    # Ensure that the user's email is in the session
    if 'email' not in session:
        flash('Please log in to view your events', 'warning')
        return redirect(url_for('login'))

    user_email = session['email']  # Get the user's email from the session

    # Query the database to retrieve events associated with the user's email
    user_events = Event.query.filter_by(email=user_email)

    # Apply additional filters based on search criteria
    if search_query:
        user_events = user_events.filter(
            or_(
                Event.manager_name.ilike(f'%{search_query}%'),
                Event.event_name.ilike(f'%{search_query}%'),
                Event.department.ilike(f'%{search_query}%'),
                Event.club_name.ilike(f'%{search_query}%')
            )
        )

    user_events = user_events.all()

    # Render the template with the filtered events data
    return render_template('user_display.html', all_hall_requests=user_events)

@app.route('/view_event_user/<int:event_id>')
def view_event_user(event_id):
    event = Event.query.get_or_404(event_id)
    

    return render_template('user_view.html', event=event)


@app.route('/cancel_event/<int:event_id>', methods=['POST'])
def cancel_event(event_id):
    if request.form['action'] == 'cancel':
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
    return redirect(url_for('hall_requests_user'))


@app.route('/all_events_user')
def all_events_user():
    # Query all events from the database
    
    all_events = Event.query.filter(Event.event_date >= datetime.now()).all()
    return render_template('user_display.html', all_hall_requests=all_events, category='All Events')

@app.route('/approved_events_user')
def approved_events_user():
    # Query approved events from the database
    approved_events = Event.query.filter_by(status='Accepted').filter(Event.event_date >= datetime.now()).all()
    return render_template('user_display.html', all_hall_requests=approved_events, category='Approved Events')

@app.route('/pending_events_user')
def pending_events_user():
    # Query pending events from the database
    pending_events = Event.query.filter_by(status='Pending').filter(Event.event_date >= datetime.now()).all()
    return render_template('user_display.html', all_hall_requests=pending_events, category='Pending Events')

@app.route('/rejected_events_user')
def rejected_events_user():
    # Query rejected events from the database
    rejected_events = Event.query.filter_by(status='Rejected').filter(Event.event_date >= datetime.now()).all()
    return render_template('user_display.html', all_hall_requests=rejected_events, category='Rejected Events')






def is_overlapping(event_date, new_start_str, new_end_str, hall_name):
    new_start = datetime.strptime(new_start_str, '%H:%M').time()
    new_end = datetime.strptime(new_end_str, '%H:%M').time()

    events = Event.query.filter_by(event_date=event_date, hall_name=hall_name).all()
    for event in events:
        # start_time = event.start_time.strftime('%H:%M')
        # end_time = event.end_time.strftime('%H:%M')
        if(event.status.lower()=="accepted"):
            start_time = event.start_time
            end_time = event.end_time
            print(event.sno)
            # start_time = datetime.strptime(start_time, '%H:%M').time()
            # end_time = datetime.strptime(end_time, '%H:%M').time()

            if (start_time <= new_start < end_time) or \
            (start_time < new_end <= end_time) or \
            (new_start <= start_time and new_end >= end_time):
                return True
    return False


@app.route('/confirm_cancel/<int:event_id>', methods=['POST'])
def confirm_cancel(event_id):
     if request.form['action'] == 'cancel':
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
     return redirect(url_for('hall_requests_user'))

@app.route('/confirm_accept/<int:event_id>', methods=['POST'])
def confirm_accept(event_id):
    if request.form['action'] == 'accept':
        event = Event.query.get_or_404(event_id)
        event_date = event.event_date
        start_time = event.start_time  # Keep .time()
        end_time = event.end_time # Keep .time()
        hall_name = event.hall_name
        if not is_overlapping(event_date, start_time.strftime('%H:%M'), end_time.strftime('%H:%M'), hall_name):
            event.status = 'Accepted'
            db.session.commit()
            flash('Event has been accepted successfully!', 'success')
            return redirect(url_for('hall_requests'))  # Pass status parameter here
        else:
            # Handle the case when there is an overlap
            event.status = 'Rejected'
            db.session.commit()
            flash('Event has been rejected due to overlapping!', 'danger')
            return redirect(url_for('hall_requests'))   # Pass status parameter here

@app.route('/confirm_reject/<int:event_id>', methods=['POST'])
def confirm_reject(event_id):
    if request.form['action'] == 'reject':
        event = Event.query.get_or_404(event_id)
        event.status = 'Rejected'
        db.session.commit()
    return redirect(url_for('hall_requests'))  # Pass status parameter here







# vaishnavi routes ended 


if __name__ == '__main__':
    app.run(debug=True)

