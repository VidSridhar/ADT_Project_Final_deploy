from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from flask import Flask
from sqlalchemy.orm import validates
from datetime import date, time
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootroot@127.0.0.1:3306/employeetimesheetdb'  

    print(app.config)
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Create database tables

    return app

#from app import create_app

app = create_app()


class Employee(db.Model):
    __tablename__ = 'employees'
    Emp_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Emp_Name = db.Column(db.String(255), nullable=False)
    Scheduled_hrs = db.Column(db.Integer, nullable=True)

    # Relationship to Attendance and LoginCredentials
    #attendances = db.relationship('Attendance', backref='employee', lazy=True)
    #login_credential = db.relationship('LoginCredentials', backref='employee', uselist=False, lazy=True)
    
    # Enforcing constraints
    @validates('emp_name')
    def validate_emp_name(self, key, emp_name):
        if not emp_name:
            raise ValueError("Employee name must not be empty")
        return emp_name
    
    @validates('scheduled_hrs')
    def validate_scheduled_hrs(self, key, scheduled_hrs):
        if scheduled_hrs is not None and not (0 <= scheduled_hrs <= 24):
            raise ValueError("scheduled_hrs must be between 0 and 24")
        return scheduled_hrs

class Department(db.Model):
    __tablename__ = 'departments'
    dept_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dept_name = db.Column(db.String(255), nullable=False)
    # Relationship to Attendance
    attendances = db.relationship('Attendance', backref='department', lazy=True)

    # Enforcing constraints
    def validate_dept_name(self, key, dept_name):
        if not dept_name:
            raise ValueError("Department name must not be empty")
        return dept_name

class Location(db.Model):
    __tablename__ = 'locations'
    location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_name = db.Column(db.String(255), nullable=False)
    # Relationship to Attendance
    attendances = db.relationship('Attendance', backref='location', lazy=True)

    # Enforcing constraints
    @validates('location_name')
    def validate_location_name(self, key, location_name):
        if not location_name:
            raise ValueError("Location name must not be empty")
        return location_name

class Attendance(db.Model):
    __tablename__ = 'attendance'
    Entry_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Date = db.Column(db.Date, nullable=False)
    Emp_ID = db.Column(db.Integer, db.ForeignKey('employees.emp_id'), nullable=True)
    Location_ID = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=True)
    Dept_ID = db.Column(db.Integer, db.ForeignKey('departments.dept_id'), nullable=True)
    ClockIn = db.Column(db.Time, nullable=True)
    ClockOut = db.Column(db.Time, nullable=True)
    Break = db.Column(db.Time, nullable=True)
    Total_hrs = db.Column(db.Time, nullable=True)
    Status = db.Column(db.String(20), nullable=False)

    # Enforcing constraints

    @validates('clock_in', 'clock_out')
    def validate_clock_times(self, key, time):
        if key == 'clock_out' and self.clock_in and time:
            if time < self.clock_in:
                raise ValueError("Clock out time must be after clock in time")
        return time
    
    @validates('status')
    def validate_status(self, key, status):
        if status not in ['Approved', 'Unapproved']:
            raise ValueError("Status must be either 'Approved' or 'Unapproved'")
        return status
    
    # Converting certain column values from objects to string, as object is not json resizeble
    def as_dict(self):
        return {column.name: str(getattr(self, column.name)) if isinstance(getattr(self, column.name), time) else getattr(self, column.name)
                for column in self.__table__.columns}

class LoginCredentials(db.Model):
    __tablename__ = 'login_credentials'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_manager = db.Column(db.Boolean, nullable=False, default=False)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.Emp_ID'), nullable=False, unique=True)


@app.route('/login', methods=['POST'])
def login():
    print("Here I am at login")
    data = request.get_json()
    user_id = data['username']  
    user_password = data['password']  
    print("Entered values: ",user_id, user_password)

    # entry = LoginCredentials.query.filter_by(
    #     userid = LoginCredentials.username,
    #     password_hash = LoginCredentials.password_hash
    # ).first()

    user = LoginCredentials.query.filter_by(username=user_id, password_hash=user_password).first()
    print("is manager?  :", user.emp_id)
    if user:
        # User found, passwords match
        return jsonify({'message': 'Login successful', 'message': user.is_manager, 'employee id': user.emp_id}), 200
    else:
        # User not found or password incorrect
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/clockin', methods=['POST'])
def clockin():
    print("Here")
    data = request.get_json()
    empployeeid = data['employee']  
    clockintime = data['clockintime']  
    print("Entered values: ",empployeeid, clockintime)
    
    #new_record = Attendance()

    #new_record.ClockIn = clockintime
    #new_record.Emp_ID = empployeeid
    print("Todays date: ", date.today())
    new_record = Attendance(Date = date.today(), Emp_ID = empployeeid, ClockIn = clockintime, Status = 'Unapproved')
    db.session.add(new_record)
    db.session.merge(new_record)
    db.session.commit()


    return jsonify({"message": "Clock-in successful"}), 200


@app.route('/clockout', methods=['POST'])
def clockout():
    print("Here")
    data = request.get_json()
    empployeeid = data['employee']  
    clockouttime = data['clockouttime']  
    totalhours = data['totalhours']
    clockedinat = data['clockedinat']
    print("Entered values: ",empployeeid, clockouttime, totalhours, clockedinat)
    
    user = Attendance.query.filter_by(Emp_ID=empployeeid, ClockIn=clockedinat).first()

    if user:
        # User found, passwords match
        user.ClockOut = clockouttime
        user.totalhours = totalhours

        db.session.commit()
        return jsonify({'message': 'Clockout successful'}), 200
    else:
        # User not found or password incorrect
        return jsonify({'message': 'Couldnt clock out'}), 401
    

@app.route('/createdata', methods=['POST'])
def createdata():
    print("Here, about to create data")
    data = request.get_json()
    employeeid = data['employeeid']
    employeename = data['empname']
    schdhrs = data['schdhrs']
    department = data['dept']
    location = data['location']

    print('Received values: ',employeeid, employeename, schdhrs, department, location)

    user = Employee()
    dept = Department.query.filter_by(dept_name = department).first()
    loc = Location.query.filter_by(location_name = location).first()

        #if dept and loc:
    user.Emp_ID = employeeid
    user.Emp_Name = employeename
    user.Scheduled_hrs = schdhrs
    db.session.merge(user)
    db.session.commit()
    return jsonify({'message': 'Employee aded successfully.'}), 201

@app.route('/dashboarddata', methods=['POST'])
def dashboarddata():
    print("Here, about to send data for dashboard!")
    data = Attendance.query.all()

    
    all_data = [entry.as_dict() for entry in data]

    print("Data in dict form: ",all_data)
    #return jsonify(all_data)
    #data_toreturn = jsonify(all_data)
    #data_toreturn.status_code=201
    #print("Data in json form: ", data_toreturn)
    return jsonify({'message':'Done!', 'Data': all_data})


@app.route('/delete_employee', methods=['POST'])
def delete_employee():
    print("Here, deleting an employee record")
    data = request.get_json()
    empid = data['emp_id']
    try:
        user = Employee.query.filter_by(Emp_ID = empid).first()
        #print(empid, empname)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'Deleted successfully'}), 201
        else:
            return jsonify({'message': 'Employee does not exist'}), 401
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'IntegrityError - Unable to delete employee'}), 500


@app.route('/update', methods=['POST'])
def update():
    print("Here at update")
    data = request.get_json()
    emp_id = data['emp_name']
    new_password = data['new_password']
    print(emp_id, new_password)

    user = LoginCredentials.query.filter_by(emp_id = emp_id).first()

    if user:
        user.password_hash = new_password
        db.session.merge(user)
        db.session.commit()
        return jsonify({'message': 'Updates successfully'}), 201
    else:
        return jsonify({'message': 'Employee does not exist'}), 401



if __name__ == "__main__":
    app.run(debug=True)





