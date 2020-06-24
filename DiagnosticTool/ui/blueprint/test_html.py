from flask import redirect, Blueprint, request, session, url_for, render_template

blueprint_html = Blueprint('test_html', __name__, url_prefix='/')

@blueprint_html.route('/home', methods=['GET'])
def render_html():
   return render_template('index.html')