from flask import Blueprint, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Redirect to courses page as requested
    return redirect(url_for('courses.course_list'))
