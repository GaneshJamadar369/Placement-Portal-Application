from flask import Blueprint, jsonify
from models.placement_drive import PlacementDrive
from models.application import Application

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.get('/drives')
def api_drives():
    drives = PlacementDrive.query.filter_by(status='approved').all()
    data = [{
        'id': d.id,
        'company': d.company.full_name,
        'job_title': d.job_title,
        'salary': d.salary,
        'deadline': d.deadline.isoformat()
    } for d in drives]
    return jsonify(data)

@api_bp.get('/stats/applications-per-drive')
def api_applications_per_drive():
    drives = PlacementDrive.query.all()
    data = [{
        'drive_id': d.id,
        'job_title': d.job_title,
        'company': d.company.full_name,
        'applications': len(d.applications)
    } for d in drives]
    return jsonify(data)

