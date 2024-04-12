
from flask import Flask, render_template, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
import calendar as calendar_module
from calendar import monthcalendar


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/datahub'
db = SQLAlchemy(app)


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

class Venue(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    capacity = db.Column(db.Integer)
    features = db.Column(db.String(255))
    # image = db.Column(db.String(255),nullable=False,default='img1.jpg')



with app.app_context():
    db.create_all()  # Create tables based on the defined models
@app.route('/booking_form', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle form submission
        event_name = request.form['eventName']
        manager_name = request.form['eventManagerName']
        club_name = request.form['orgClubName']
        event_date = request.form['eventDate']
        start_time = request.form['startTime']
        end_time = request.form['endTime']
        hall_name = request.form['hallName']  # Retrieve hall name from the form
        email = request.form['email']
        ph_num = request.form['phoneNumber']
        department = request.form['department']
        request_text = request.form['requestCreatedAt']

        status = "pending"
        # Check for event overlap at the same venue
        if not is_overlapping(event_date, start_time, end_time, hall_name):
            # Add new event to the database
            new_event = Event(event_name=event_name, manager_name=manager_name, club_name=club_name, event_date=event_date,
                              start_time=start_time, end_time=end_time, hall_name=hall_name, email=email,
                              ph_num=ph_num, department=department, request=request_text,status=status)
            db.session.add(new_event)
            db.session.commit()
            return "Event added successfully!"
        else:
            return "The event overlaps with an existing event at the same venue. Please choose another time."

    # Fetch all venues from the Venue table
    venues = Venue.query.all()
    return render_template('overlap.html', venues=venues)



def is_overlapping(event_date, new_start_str, new_end_str, hall_name):
    new_start = datetime.strptime(new_start_str, '%H:%M').time()
    new_end = datetime.strptime(new_end_str, '%H:%M').time()

    events = Event.query.filter_by(event_date=event_date, hall_name=hall_name,status='accepted').all()
    for event in events:
        start_time = event.start_time.strftime('%H:%M')
        end_time = event.end_time.strftime('%H:%M')

        start_time = datetime.strptime(start_time, '%H:%M').time()
        end_time = datetime.strptime(end_time, '%H:%M').time()

        if (start_time <= new_start < end_time) or \
           (start_time < new_end <= end_time) or \
           (new_start <= start_time and new_end >= end_time):
            return True
    return False



@app.route('/calendar1',methods=['POST'])
def calendar1():
    return render_template('calendar1.html')


@app.route('/fetch-events', methods=['POST'])
def fetch_events():
    try:
        selected_date_str = request.json.get('selectedDate')
        selected_datetime = datetime.fromisoformat(selected_date_str)
        selected_date = selected_datetime.date()

        print(selected_date)

        # Query events from the database for the selected date
        events = Event.query.filter_by(event_date=selected_date,status='accepted').all()

        # Convert event objects to dictionary format
        event_list = []
        for event in events:
            print(event.event_name)
            event_data = {
                'event_name': event.event_name,
                'manager_name': event.manager_name,
                'club_name': event.club_name,
                'start_time': event.start_time.strftime('%H:%M'),
                'end_time': event.end_time.strftime('%H:%M'),
                'hall_name': event.hall_name,
                'email': event.email,
                'ph_num': event.ph_num,
                'department': event.department,
                'status': event.status
            }
            event_list.append(event_data)
            for i in event_list:
                print(i)
        return jsonify({'events': event_list})

    except Exception as e:
        # Handle the exception
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An error occurred while fetching events'}), 500


if __name__ == '__main__':
    app.run(debug=True)