from flask import Flask, render_template, redirect, url_for, flash
from config import Config
from models.base import db
from models.user import User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.auth_forms import LoginForm, StudentRegistrationForm, CompanyRegistrationForm

from models.student import Student
from models.company import Company
from forms.auth_forms import LoginForm, StudentRegistrationForm, CompanyRegistrationForm


from flask import Flask
from config import Config
from models.base import db
from models.user import User
from flask_login import LoginManager

from models.company import Company
from flask import request

from forms.company_forms import CreateDriveForm
from models.placement_drive import PlacementDrive

from models.application import Application
from models.student import Student

from forms.student_forms import StudentProfileForm
from sqlalchemy import func

VALID_APPLICATION_TRANSITIONS = {
    'applied': ['shortlisted', 'rejected'],
    'shortlisted': ['interview_scheduled', 'rejected'],
    'interview_scheduled': ['selected', 'rejected'],
    'selected': [],    # final
    'rejected': []     # final
}

from flask_mail import Mail, Message
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Email Testing Configuration
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 1025
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@placementportal.com'

    #initing th db
    db.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        #here import is not on top beausee of circular import
        #this will lead import error, before db init it will call db in base 
        from models.user import User
        return User.query.get(int(user_id))

    with app.app_context():
        from models.user import User, Admin
        from models.company import Company
        from models.placement_drive import PlacementDrive
        from models.application import Application
        from models.notification import Notification
        db.create_all()
        if not Admin.query.filter_by(email='admin@portal.com').first():
            admin = Admin(
                email='admin@portal.com',
                full_name='Portal Admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()


    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/test')
    def test():
        return "<h1> Test page still works!</h1>"
    
    @app.route('/add-user')
    def add_user():
        user = User(email='abc3@iitm.ac.in', full_name='Ganesh')
        db.session.add(user)
        db.session.commit()
        return f"added userrr {user}"
    
    @app.route('/create-admin')
    def create_admin():
        from models.user import Admin
        admin = Admin(email = 'admin@placement.com', full_name='Admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return f"Admin creted!! {admin.password[:20]}"
    
    from flask_login import login_user, logout_user, login_required, current_user
    from forms.auth_forms import LoginForm
    from models.user import User

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            if current_user.type == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.type == 'company':
                return redirect(url_for('company_dashboard'))
            elif current_user.type == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('home'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)

                if user.type == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.type == 'company':
                    return redirect(url_for('company_dashboard'))
                elif user.type == 'student':
                    return redirect(url_for('student_dashboard'))
                else:
                    return redirect(url_for('home'))





                return redirect(url_for('dashboard'))
            flash('Invalid email or password')
        return render_template('auth/login.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return f"<h1>Welcome {current_user.full_name}!</h1><a href='/logout'>Logout</a>"

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # Registration Routes
    @app.route('/register')
    def register_select():
        return render_template('auth/register_select.html')

    from models.student import Student
    from models.company import Company
    @app.route('/register-student', methods=['GET', 'POST'])
    def register_student():
        form = StudentRegistrationForm()

        if form.validate_on_submit():

            existing_roll = Student.query.filter_by(
                roll_number=form.roll_number.data
            ).first()

            existing_email = Student.query.filter_by(
                email=form.email.data
            ).first()

            if existing_roll:
                flash("Roll number already registered!", "danger")
                return redirect(url_for('register_student'))

            if existing_email:
                flash("Email already registered!", "danger")
                return redirect(url_for('register_student'))

            student = Student(
                full_name=form.full_name.data,
                email=form.email.data,
                roll_number=form.roll_number.data,
                branch=form.branch.data,
                cgpa=float(form.cgpa.data),
                type='student'
            )

            student.set_password(form.password.data)

            db.session.add(student)
            db.session.commit()

            flash('Student registered! Login to continue.', 'success')
            return redirect(url_for('login'))

        return render_template('auth/register_student.html', form=form)

    @app.route('/register-company', methods=['GET', 'POST'])
    def register_company():
        form = CompanyRegistrationForm()
        if form.validate_on_submit():
            company = Company(
                full_name=form.full_name.data,
                email=form.email.data,
                cin=form.cin.data,
                sector=form.sector.data,
                type='company'
            )
            company.set_password(form.password.data)
            db.session.add(company)
            db.session.commit()
            flash('Company registered! Awaiting admin approval.')
            return redirect(url_for('login'))
        return render_template('auth/register_company.html', form=form)

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.type != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('home'))
        
        # --- Base KPIs ---
        pending_count = Company.query.filter_by(approval_status='pending').count()
        approved_count = Company.query.filter_by(approval_status='approved').count()
        student_count = Student.query.count()
        
        total_placements = Student.query.filter(Student.final_offer_drive_id.isnot(None)).count()
        placement_rate = round((total_placements / student_count * 100), 1) if student_count > 0 else 0
        
        active_drives = PlacementDrive.query.filter_by(status='approved').count()
        pending_drives_count = PlacementDrive.query.filter_by(status='pending').count()
        
        # Avg CTC of placed students
        placed_students = Student.query.join(PlacementDrive, Student.final_offer_drive_id == PlacementDrive.id).all()
        salaries = [s.final_offer_drive.salary for s in placed_students if s.final_offer_drive and s.final_offer_drive.salary]
        avg_ctc = round(sum(salaries) / len(salaries), 2) if salaries else 0

        # --- Chart Data JSON Preparation ---
        
        # Chart 1: Company Sector Distribution
        sectors_raw = db.session.query(Company.sector, func.count(Company.id)).filter(Company.sector.isnot(None)).group_by(Company.sector).all()
        company_dist = {sector: count for sector, count in sectors_raw if sector}
        
        # Chart 2: Salary Distribution Brackets
        drives = PlacementDrive.query.filter(PlacementDrive.salary.isnot(None)).all()
        salary_dist = {"< 5 LPA": 0, "5 - 10 LPA": 0, "10 - 15 LPA": 0, "> 15 LPA": 0}
        for d in drives:
            if d.salary < 5: salary_dist["< 5 LPA"] += 1
            elif d.salary <= 10: salary_dist["5 - 10 LPA"] += 1
            elif d.salary <= 15: salary_dist["10 - 15 LPA"] += 1
            else: salary_dist["> 15 LPA"] += 1
            
        # Chart 3: Branch-wise Placement Count
        branch_raw = db.session.query(Student.branch, func.count(Student.id)).filter(
            Student.final_offer_drive_id.isnot(None), Student.branch.isnot(None)
        ).group_by(Student.branch).all()
        branch_dist = {branch: count for branch, count in branch_raw if branch}

        # Chart 4: Application Funnel
        status_raw = db.session.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
        funnel_dict = {status: count for status, count in status_raw}
        funnel_keys = ['applied', 'shortlisted', 'selected', 'rejected']
        funnel_dist = {k: funnel_dict.get(k, 0) for k in funnel_keys}
        
        # Chart 5: Placement Trend (12 Months)
        from datetime import datetime, timedelta
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        selected_apps = Application.query.filter(
            Application.status == 'selected',
            Application.updated_at >= twelve_months_ago
        ).all()
        
        trend_dict = {}
        for i in range(11, -1, -1):
            d = datetime.utcnow() - timedelta(days=30 * i)
            month_name = d.strftime('%b %Y')
            if month_name not in trend_dict:
                trend_dict[month_name] = 0
                
        for app in selected_apps:
            if app.updated_at:
                month_name = app.updated_at.strftime('%b %Y')
                if month_name in trend_dict:
                    trend_dict[month_name] += 1

        return render_template('admin/dashboard.html',
                            pending_count=pending_count,
                            approved_count=approved_count,
                            student_count=student_count,
                            total_placements=total_placements,
                            placement_rate=placement_rate,
                            active_drives=active_drives,
                            pending_drives_count=pending_drives_count,
                            avg_ctc=avg_ctc,
                            company_dist=company_dist,
                            salary_dist=salary_dist,
                            branch_dist=branch_dist,
                            funnel_dist=funnel_dist,
                            trend_dist=trend_dict)
                            
    @app.route('/admin/export/csv')
    @login_required
    def admin_export_csv():
        if current_user.type != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('home'))
            
        import csv
        import io
        from flask import Response
            
        placed_students = Student.query.filter(Student.final_offer_drive_id.isnot(None)).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Roll Number', 'Name', 'Branch', 'Company', 'Job Title', 'CTC (LPA)'])
        
        for s in placed_students:
            drive = s.final_offer_drive
            company_name = drive.company.full_name if drive and drive.company else 'N/A'
            job_title = drive.job_title if drive else 'N/A'
            salary = drive.salary if drive else 0
            writer.writerow([s.roll_number, s.full_name, s.branch, company_name, job_title, salary])
            
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=placed_students_report.csv"}
        )
                            
    @app.route('/company/dashboard')
    @login_required
    def company_dashboard():
        if current_user.type != 'company':
            flash('Access denied')
            return redirect(url_for('home')) 
        drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()
        return render_template('company/dashboard.html', drives=drives)
    
    @app.route('/student/dashboard')
    @login_required
    def student_dashboard():
        if current_user.type != 'student':
            flash('Access denied', 'danger')
            return redirect(url_for('home'))
            
        from datetime import datetime
        
        # Base query for approved and active drives
        query = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.deadline >= datetime.utcnow()
        )
        
        # Apply Salary filter
        min_salary = request.args.get('min_salary', type=float)
        if min_salary:
            query = query.filter(PlacementDrive.salary >= min_salary)
            
        # Apply Location filter
        location = request.args.get('location')
        if location and location != 'All':
            query = query.filter(PlacementDrive.location.ilike(f'%{location}%'))
            
        # Apply Job Type filter
        job_type = request.args.get('job_type')
        if job_type and job_type != 'All':
            query = query.filter(PlacementDrive.job_type.ilike(f'%{job_type}%'))
            
        # Apply Company Sector filter
        company_sector = request.args.get('company_sector')
        if company_sector and company_sector != 'All':
            query = query.join(Company).filter(Company.sector == company_sector)

        # Apply Eligibility Filter (Student's CGPA must be >= required min_cgpa)
        # Assuming min_cgpa defaults to 0.0 if not specified
        query = query.filter(
            (PlacementDrive.min_cgpa <= current_user.cgpa) | (PlacementDrive.min_cgpa == None)
        )
            
        # Sort criteria
        sort_by = request.args.get('sort_by', 'deadline_asc')
        if sort_by == 'salary_desc':
            query = query.order_by(PlacementDrive.salary.desc())
        else:
            query = query.order_by(PlacementDrive.deadline.asc())
            
            
        # Pagination
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(page=page, per_page=12, error_out=False)
        drives = pagination.items
        
        return render_template('student/dashboard.html', drives=drives, pagination=pagination)


    @app.route('/admin/companies')
    @login_required
    def admin_companies():
        if current_user.type != 'admin':
            flash('Access denied')
            return redirect(url_for('home'))

        pending = Company.query.filter_by(approval_status='pending').all()
        approved = Company.query.filter_by(approval_status='approved').all()
        return render_template('admin/companies.html',
                            pending=pending,
                            approved=approved)

    @app.route('/admin/company/<int:company_id>/approve', methods=['POST'])
    @login_required
    def approve_company(company_id):
        if current_user.type != 'admin':
            flash('Access denied')
            return redirect(url_for('home'))

        company = Company.query.get_or_404(company_id)
        company.approval_status = 'approved'
        db.session.commit()
        flash(f'Company {company.full_name} approved.')
        return redirect(url_for('admin_companies'))

    @app.route('/company/drives/create', methods=['GET', 'POST'])
    @login_required
    def create_drive():
        if current_user.type != 'company':
            flash('Access denied')
            return redirect(url_for('home'))

        form = CreateDriveForm()
        if form.validate_on_submit():
            drive = PlacementDrive(
                company_id=current_user.id,
                job_title=form.job_title.data,
                description=form.description.data,
                salary=form.salary.data,
                positions=form.positions.data,
                eligibility=form.eligibility.data,
                location=form.location.data,
                job_type=form.job_type.data,
                min_cgpa=form.min_cgpa.data,
                deadline=form.deadline.data,
                status='pending'
            )
            db.session.add(drive)
            db.session.commit()
            flash('Drive created. Awaiting admin approval.')
            return redirect(url_for('company_dashboard'))

        return render_template('company/create_drive.html', form=form)

    @app.route('/admin/drives')
    @login_required
    def admin_drives():
        if current_user.type != 'admin':
            flash('Access denied')
            return redirect(url_for('home'))

        pending = PlacementDrive.query.filter_by(status='pending').all()
        approved = PlacementDrive.query.filter_by(status='approved').all()
        return render_template('admin/drives.html',
                            pending=pending,
                            approved=approved)

    @app.route('/admin/drives/<int:drive_id>/approve', methods=['POST'])
    @login_required
    def admin_approve_drive(drive_id):
        if current_user.type != 'admin':
            flash('Access denied')
            return redirect(url_for('home'))

        drive = PlacementDrive.query.get_or_404(drive_id)
        drive.status = 'approved'
        db.session.commit()
        flash(f'Drive {drive.job_title} approved.')
        return redirect(url_for('admin_drives'))


    @app.route('/student/drives/<int:drive_id>')
    @login_required
    def student_view_drive(drive_id):
        if current_user.type != 'student':
            flash('Access denied')
            return redirect(url_for('home'))

        drive = PlacementDrive.query.get_or_404(drive_id)
        existing_application = Application.query.filter_by(student_id=current_user.id, drive_id=drive.id).first()
        
        from datetime import datetime
        return render_template('student/view_drive.html', drive=drive, existing_application=existing_application, now=datetime.utcnow())

    @app.route('/student/drives/<int:drive_id>/apply', methods=['POST'])
    @login_required
    def student_apply_drive(drive_id):
        if current_user.type != 'student':
            flash('Access denied')
            return redirect(url_for('home'))

        drive = PlacementDrive.query.get_or_404(drive_id)

        # Prevent duplicate application
        existing = Application.query.filter_by(
            student_id=current_user.id,
            drive_id=drive.id
        ).first()
        if existing:
            flash('You already applied to this drive.')
            return redirect(url_for('student_view_drive', drive_id=drive.id))

        app_obj = Application(student_id=current_user.id, drive_id=drive.id)
        db.session.add(app_obj)
        db.session.commit()
        flash('Application submitted!')
        return redirect(url_for('student_applications'))

    @app.route('/student/applications')
    @login_required
    def student_applications():
        if current_user.type != 'student':
            flash('Access denied')
            return redirect(url_for('home'))

        applications = Application.query.filter_by(student_id=current_user.id).all()
        return render_template('student/applications.html', apps=applications)

    @app.route('/company/applications')
    @login_required
    def company_applications():
        if current_user.type != 'company':
            flash('Access denied')
            return redirect(url_for('home'))

        # all drives of this company
        drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()
        drive_ids = [d.id for d in drives]

        applications = Application.query.filter(
            Application.drive_id.in_(drive_ids)
        ).all()

        return render_template('company/applications.html',
                            applications=applications)

    

    @app.route('/company/applications/<int:app_id>/status/<string:new_status>', methods=['POST'])
    @login_required
    def company_update_application(app_id, new_status):
        if current_user.type != 'company':
            flash('Access denied')
            return redirect(url_for('home'))

        app_obj = Application.query.get_or_404(app_id)
        current = app_obj.status

        # security: ensure this application belongs to this company
        if app_obj.drive.company_id != current_user.id:
            flash('You cannot modify this application.')
            return redirect(url_for('company_applications'))

        # check valid transition
        allowed = VALID_APPLICATION_TRANSITIONS.get(current, [])
        if new_status not in allowed:
            flash(f'Invalid status change: {current} → {new_status}')
            return redirect(url_for('company_applications'))

        # check if student already has a final offer elsewhere
        if new_status == 'selected':
            existing_selected = Application.query.filter(
                Application.student_id == app_obj.student_id,
                Application.status == 'selected',
                Application.id != app_obj.id
            ).first()
            if existing_selected:
                flash('Student already has a selection in another drive.')
                return redirect(url_for('company_applications'))

            # optional: mark final offer on student
            app_obj.student.final_offer_drive_id = app_obj.drive_id

        app_obj.status = new_status
        db.session.commit()
        
        # -----------------------------------------------------
        # Phase 4 S-GRADE: Notifications + Email Integration
        # -----------------------------------------------------
        from models.notification import Notification
        
        notif_type = 'success' if new_status == 'selected' else 'danger' if new_status == 'rejected' else 'info'
        if new_status == 'interview_scheduled':
            notif_type = 'warning'
            
        notif_msg = f"Your application for {app_obj.drive.job_title} at {app_obj.drive.company.full_name} has been updated to {new_status.capitalize()}."
        
        # 1. In-App Database Notification
        new_notif = Notification(
            user_id=app_obj.student_id,
            title=f"Application Status: {new_status.capitalize()}",
            message=notif_msg,
            type=notif_type
        )
        db.session.add(new_notif)
        db.session.commit()
        
        # 2. External Email Trigger
        try:
            from flask_mail import Message
            msg = Message(
                subject=f"Placement Portal Update - {app_obj.drive.company.full_name}",
                recipients=[app_obj.student.email],
                body=f"Hello {app_obj.student.full_name},\n\n{notif_msg}\n\nGood luck,\nThe Career Center Team"
            )
            mail.send(msg)
        except Exception as e:
            print(f"Skipped email dispatch: {e}")

        flash(f'Status updated: {current} → {new_status}')
        return redirect(url_for('company_applications'))

    @app.route('/admin/applications/<int:app_id>/status/<string:new_status>', methods=['POST'])
    @login_required
    def admin_override_status(app_id, new_status):
        if current_user.type != 'admin':
            flash('Access denied')
            return redirect(url_for('home'))

        app_obj = Application.query.get_or_404(app_id)
        current = app_obj.status

        # Admin can do anything
        app_obj.status = new_status
        db.session.commit()
        flash(f'Overrode status: {current} → {new_status}')
        return redirect(url_for('admin_dashboard'))

    # ---------------------------------------------------------------------------------
    # NOTIFICATIONS ROUTES
    # ---------------------------------------------------------------------------------
    from models.notification import Notification

    @app.route('/notifications')
    @login_required
    def view_notifications():
        # Get notifications for current user, ordered by newest first
        notifications = current_user.notifications.order_by(Notification.created_at.desc()).all()
        return render_template('notifications.html', notifications=notifications)

    @app.route('/notifications/read/<int:notif_id>', methods=['POST'])
    @login_required
    def read_notification(notif_id):
        notif = Notification.query.get_or_404(notif_id)
        if notif.user_id != current_user.id:
            flash('Access denied', 'danger')
            return redirect(url_for('view_notifications'))
            
        notif.is_read = True
        db.session.commit()
        return redirect(url_for('view_notifications'))

    @app.route('/notifications/clear', methods=['POST'])
    @login_required
    def clear_notifications():
        # Mark all as read, or alternatively delete them. We will delete them to save space.
        current_user.notifications.delete()
        db.session.commit()
        flash('All notifications cleared.', 'success')
        return redirect(url_for('view_notifications'))

    # ---------------------------------------------------------------------------------
    # FILE SERVING
    # ---------------------------------------------------------------------------------
    import os
    from flask import send_from_directory
    @app.route('/uploads/resumes/<filename>')
    @login_required
    def download_resume(filename):
        return send_from_directory(os.path.join(app.root_path, 'uploads', 'resumes'), filename)

    # ---------------------------------------------------------------------------------
    # STUDENT PROFILE
    # ---------------------------------------------------------------------------------
    @app.route('/student/profile', methods=['GET', 'POST'])
    @login_required
    def student_profile():
        if current_user.type != 'student':
            flash('Access denied', 'error')
            return redirect(url_for('home'))

        import os, uuid
        from werkzeug.utils import secure_filename

        student = Student.query.get_or_404(current_user.id)
        form = StudentProfileForm(obj=student)

        if form.validate_on_submit():
            student.full_name = form.full_name.data
            student.branch = form.branch.data
            student.cgpa = form.cgpa.data
            student.phone = form.phone.data
            student.cover_letter = form.cover_letter.data
            
            if form.resume.data:
                file = form.resume.data
                ext = secure_filename(file.filename).split('.')[-1]
                filename = f"{current_user.id}_{uuid.uuid4().hex}.{ext}"
                upload_path = os.path.join(app.root_path, 'uploads', 'resumes')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                file.save(os.path.join(upload_path, filename))
                student.resume_url = filename
                
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('student_profile'))

        return render_template('student/profile.html', form=form)

    # register blueprint
    from routes.api import api_bp
    app.register_blueprint(api_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)