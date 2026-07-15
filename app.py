from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, init_db, User, Trek, Booking
import os

app = Flask(__name__)
app.secret_key = 'trek_management_secure_token'
app.config['SQLALCHEMY_DATABASE_DATA_URI'] = 'sqlite:///trekking.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Programmatically initialize sqlite database engine
init_db(app)

# --- Role Based Route Guards Helper Functions ---
def check_auth(required_role=None):
    if 'user_id' not in session:
        return False
    if required_role and session.get('role') != required_role:
        return False
    return True

# --- Root Redirects ---
@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        return redirect(url_for(f'{role}_dashboard'))
    return redirect(url_for('login'))

# --- System Access Authentication Routing ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        account = User.query.filter_by(username=username, password=password).first()
        
        if account:
            if account.status == 'Blacklisted':
                flash('Your account is blacklisted. Contact administration.', 'danger')
                return redirect(url_for('login'))
            if account.role == 'staff' and account.status == 'Pending':
                flash('Your staff registration is awaiting admin verification.', 'warning')
                return redirect(url_for('login'))
                
            session['user_id'] = account.id
            session['username'] = account.username
            session['role'] = account.role
            return redirect(url_for('index'))
        else:
            flash('Invalid credential matching configuration.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        contact = request.form['contact']
        role = request.form['role'] # 'staff' or 'user'
        
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Account structural username matches existing record.', 'danger')
            return redirect(url_for('register'))
            
        initial_status = 'Pending' if role == 'staff' else 'Approved'
        
        new_account = User(
            username=username,
            password=password,
            name=name,
            contact=contact,
            role=role,
            status=initial_status
        )
        db.session.add(new_account)
        db.session.commit()
        
        if role == 'staff':
            flash('Staff configuration requested. Pending Admin verification.', 'info')
        else:
            flash('Trekker system profile created successfully. Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Admin Dashboard Logic ---
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not check_auth('admin'): return redirect(url_for('login'))
    
    # Summary Cards Computations
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    
    # Filter Management Systems
    search_query = request.args.get('search', '')
    if search_query:
        all_treks = Trek.query.filter((Trek.name.like(f'%{search_query}%')) | (Trek.id == search_query)).all()
        all_users = User.query.filter((User.role == 'user') & ((User.name.like(f'%{search_query}%')) | (User.id == search_query))).all()
        all_staff = User.query.filter((User.role == 'staff') & ((User.name.like(f'%{search_query}%')) | (User.id == search_query))).all()
    else:
        all_treks = Trek.query.all()
        all_users = User.query.filter_by(role='user').all()
        all_staff = User.query.filter_by(role='staff').all()
        
    all_bookings = Booking.query.all()
    available_guides = User.query.filter_by(role='staff', status='Approved').all()
    
    return render_template('admin_dashboard.html', 
                           total_treks=total_treks, total_users=total_users, 
                           total_staff=total_staff, total_bookings=total_bookings,
                           all_treks=all_treks, all_users=all_users, 
                           all_staff=all_staff, all_bookings=all_bookings,
                           available_guides=available_guides)

@app.route('/admin/trek/create', methods=['POST'])
def admin_create_trek():
    if not check_auth('admin'): return redirect(url_for('login'))
    new_trek = Trek(
        name=request.form['name'],
        location=request.form['location'],
        difficulty=request.form['difficulty'],
        duration=int(request.form['duration']),
        available_slots=int(request.form['available_slots']),
        start_date=request.form['start_date'],
        end_date=request.form['end_date'],
        status='Pending'
    )
    db.session.add(new_trek)
    db.session.commit()
    flash('Trek created successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

# @app.route('/admin/trek/update/<int:trek_id>', methods=['POST'])
# def admin_update_trek(trek_id):
#     if not check_auth('admin'): return redirect(url_for('login'))
#     trek = Trek.query.get(trek_id)
#     if trek:
#         trek.name = request.form['name']
#         trek.location = request.form['location']
#         trek.difficulty = request.form['difficulty']
#         trek.duration = int(request.form['duration'])
#         trek.start_date = request.form['start_date']
#         trek.end_date = request.form['end_date']
#         db.session.commit()
#         flash('Trek fields altered successfully.', 'success')
#     return redirect(url_for('admin_dashboard'))
@app.route('/admin/trek/update/<int:trek_id>', methods=['POST'])
def admin_update_trek(trek_id):
    if not check_auth('admin'): return redirect(url_for('login'))
    trek = Trek.query.get(trek_id)
    if trek:
        trek.name = request.form['name']
        trek.location = request.form['location']
        trek.difficulty = request.form['difficulty']
        trek.duration = int(request.form['duration'])
        trek.start_date = request.form['start_date']
        trek.end_date = request.form['end_date']
        
        # Quick Edit Form me status dynamically catch karne ke liye (if added in form)
        if 'status' in request.form:
            new_status = request.form['status']
            trek.status = new_status
            if new_status == 'Completed':
                active_bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
                for b in active_bookings:
                    b.status = 'Completed'
                    db.session.add(b)
        db.session.commit()
        flash('Trek fields altered successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/trek/delete/<int:trek_id>')
def admin_delete_trek(trek_id):
    if not check_auth('admin'): return redirect(url_for('login'))
    trek = Trek.query.get(trek_id)
    if trek:
        db.session.delete(trek)
        db.session.commit()
        flash('Trek entry purged from system history.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/status/<int:user_id>/<string:status>')
def admin_toggle_user_status(user_id, status):
    if not check_auth('admin'): return redirect(url_for('login'))
    account = User.query.get(user_id)
    if account:
        account.status = status
        db.session.commit()
        flash(f'Account state set to {status}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/trek/assign/<int:trek_id>', methods=['POST'])
def admin_assign_staff(trek_id):
    if not check_auth('admin'): return redirect(url_for('login'))
    trek = Trek.query.get(trek_id)
    staff_id = request.form.get('staff_id')
    if trek and staff_id:
        trek.staff_id = int(staff_id)
        trek.status = 'Approved' # Switch status configuration step to approved upon staff validation
        db.session.commit()
        flash('Staff resource assigned to operational route.', 'success')
    return redirect(url_for('admin_dashboard'))


# --- Trek Staff Dashboard Logic ---
@app.route('/staff/dashboard')
def staff_dashboard():
    if not check_auth('staff'): return redirect(url_for('login'))
    staff_id = session['user_id']
    # Sirf wahi treks dikhao jo abhi tak completed nahi hue hain
    assigned_treks = Trek.query.filter(Trek.staff_id == staff_id, Trek.status != 'Completed').all()
    return render_template('staff_dashboard.html', assigned_treks=assigned_treks)
# @app.route('/staff/dashboard')
# def staff_dashboard():
#     if not check_auth('staff'): return redirect(url_for('login'))
#     staff_id = session['user_id']
#     assigned_treks = Trek.query.filter_by(staff_id=staff_id).all()
#     return render_template('staff_dashboard.html', assigned_treks=assigned_treks)

# @app.route('/staff/trek/update/<int:trek_id>', methods=['POST'])
# def staff_update_trek(trek_id):
#     if not check_auth('staff'): return redirect(url_for('login'))
#     trek = Trek.query.get(trek_id)
#     if trek and trek.staff_id == session['user_id']:
#         trek.available_slots = int(request.form['available_slots'])
#         trek.status = request.form['status']
#         db.session.commit()
#         flash('Trek tracking status parameters synchronized.', 'success')
#     else:
#         flash('Operation forbidden. Resource mapping parameters ownership conflict.', 'danger')
#     return redirect(url_for('staff_dashboard'))
@app.route('/staff/trek/update/<int:trek_id>', methods=['POST'])
def staff_update_trek(trek_id):
    if not check_auth('staff'): return redirect(url_for('login'))
    trek = Trek.query.get(trek_id)
    if trek and trek.staff_id == session['user_id']:
        new_status = request.form['status']
        trek.available_slots = int(request.form['available_slots'])
        trek.status = new_status
        
        # AUTOMATION: Agar trek complete ho gaya hai, to saari active bookings ko complete mark karo
        if new_status == 'Completed':
            active_bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
            for b in active_bookings:
                b.status = 'Completed'
                db.session.add(b)
        db.session.commit()
        flash('Trek tracking status and relative user bookings synchronized.', 'success')
    else:
        flash('Operation forbidden. Resource mapping parameters ownership conflict.', 'danger')
    return redirect(url_for('staff_dashboard'))


# --- Trekker User Dashboard Logic ---
@app.route('/user/dashboard')
def user_dashboard():
    if not check_auth('user'): return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    
    query = Trek.query.filter_by(status='Open')
    if search:
        query = query.filter(Trek.location.like(f'%{search}%') | Trek.name.like(f'%{search}%'))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
        
    open_treks = query.all()
    my_bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    user_profile = User.query.get(session['user_id'])
    
    return render_template('user_dashboard.html', open_treks=open_treks, my_bookings=my_bookings, user_profile=user_profile)

@app.route('/user/book/<int:trek_id>')
def user_book_trek(trek_id):
    if not check_auth('user'): return redirect(url_for('login'))
    trek = Trek.query.get(trek_id)
    
    if not trek or trek.status != 'Open':
        flash('Selected operation route is closed or unavailable.', 'danger')
        return redirect(url_for('user_dashboard'))
        
    if trek.available_slots <= 0:
        flash('Overbooking failure prevented. Selected route has no operational slots left.', 'danger')
        return redirect(url_for('user_dashboard'))
        
    # Prevent duplicate active bookings
    already_booked = Booking.query.filter_by(user_id=session['user_id'], trek_id=trek.id, status='Booked').first()
    if already_booked:
        flash('Profile matching active allocation sequence registered already.', 'warning')
        return redirect(url_for('user_dashboard'))
        
    # Perform transaction execution steps
    trek.available_slots -= 1
    new_booking = Booking(user_id=session['user_id'], trek_id=trek.id, status='Booked')
    db.session.add(new_booking)
    db.session.commit()
    
    flash('Trek space secured successfully.', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/user/booking/cancel/<int:booking_id>')
def user_cancel_booking(booking_id):
    if not check_auth('user'): return redirect(url_for('login'))
    booking = Booking.query.get(booking_id)
    if booking and booking.user_id == session['user_id'] and booking.status == 'Booked':
        booking.status = 'Cancelled'
        booking.trek.available_slots += 1 # Re-allocate programmatic capacity configuration numbers
        db.session.commit()
        flash('Booking sequence cancelled successfully.', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/user/profile/update', methods=['POST'])
def user_update_profile():
    if not check_auth('user'): return redirect(url_for('login'))
    account = User.query.get(session['user_id'])
    if account:
        account.name = request.form['name']
        account.contact = request.form['contact']
        db.session.commit()
        flash('Profile metadata mapping modified successfully.', 'success')
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)