from flask import Blueprint, render_template, session, redirect, url_for, make_response, request, flash
from flask import current_app as app
import requests

User = Blueprint (
    name='User',
    import_name=__name__,
    url_prefix='/user',
    template_folder='../../templates/user'
)

@User.route('/')
def index():
    return render_template (
        title="Home Page | My Absensi",
        template_name_or_list=''
    )
    
# end def
