"""
Logic for dashboard related routes
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from .forms import LogUserForm
from ..data.database import db


blueprint = Blueprint('public', __name__)

@blueprint.route('/', methods=['GET'])
def index():
    if current_user.is_anonymous():
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.listuserzimbra'))
