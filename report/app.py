from flask import Flask, render_template, redirect, url_for, make_response
from flask_nav import Nav
from flask_nav.elements import *
import os
import pandas as pd
import io
import yaml
import re 
import datetime
import random

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

from settings import STATIC, APP_ROOT

with open(os.path.expanduser(APP_ROOT + '/cis_structure.yaml'), 'r') as f:
    cis_structure = yaml.load(f)

#print(list(map(View, cis_structure['section_ordering'])))

#nav = Nav()

app = Flask(__name__)
nav = Nav(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services/<service>')
def service(service):
    findings_table = [(x['subsection_number'], x['subsection_name']) for x in cis_structure['TOC'][service]]
    return render_template('service.html', service=service, findings_table=findings_table)

@app.route('/services/<service>/<finding>')
def finding(service, finding):
    finding_entry = get_finding_index(cis_structure['TOC'][service], finding)
    with open(os.path.expanduser('~/owl_projects/texas_capital_bank_2018-04-1301/phases/azure/scans/2018-5-8/filtered/expiry_date_is_set_on_all_keys_and_secrets.yaml'), 'r') as f:
        items_flagged_list = yaml.load(f)
    data = pd.DataFrame(items_flagged_list, columns=['Region', 'Vault', 'Type', 'Status', 'Created', 'Expires'])
    #data.set_index(['Name'], inplace=True)
    #data.index.name=None
    return render_template('finding.html', service=service, finding=finding, finding_entry=finding_entry, table=data.to_html(), title=title_except(finding))

# registers the "top" menubar

def title_except(string):
    articles = ['a', 'an', 'of', 'the', 'is', 'not', 'for', 'if']
    word_list = re.split(' ', string)       # re.split behaves as expected
    final = [word_list[0].capitalize()]
    for word in word_list[1:]:
        final.append(word if word in articles else word.capitalize())
    return " ".join(final)

def get_finding_index(findings_list, finding):
    for finding_entry in findings_list:
        if finding_entry['subsection_name'] == finding:
            return finding_entry
    raise ValueError("finding {} not found in {}".format(finding, findings_list))

# Todo: use wrappers to generate the nav bars.  Too tricky for now.  Generated with print statements.
def build_navbar(cis_structure):
    navbar = [('Home', 'index')]
    kwarg_list = [ dict(service=section) for section in cis_structure['section_ordering'] ]
    arg_list = [ (section, 'section') for section in cis_structure['section_ordering'] ]
    navbar = list(map(sappable_f, zip(arg_list, kwarg_list)))
    print(navbar)
    return navbar

@app.route("/simple.png")
def simple():


    fig=Figure()
    ax=fig.add_subplot(111)
    x=[]
    y=[]
    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now+=delta
        y.append(random.randint(0, 1000))
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    png_output = io.BytesIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

nav.register_element(
    'top',
    Navbar(
        View('Identity and Access Management', 'service', service='Identity and Access Management'),
        View('Security Center', 'service', service='Security Center'),
        View('Storage Accounts', 'service', service='Storage Accounts'),
        View('SQL Servers', 'service', service='SQL Servers'),
        View('SQL Databases', 'service', service='SQL Databases'),
        View('Logging and Monitoring', 'service', service='Logging and Monitoring'),
        View('Networking', 'service', service='Networking'),
        View('Virtual Machines', 'service', service='Virtual Machines'),
        View('Other Security Considerations', 'service', service='Other Security Considerations')
        )
    )


# def create_app(configfile=None):
#     app = Flask(__name__)
#     nav.init_app(app)

#     # not good style, but like to keep our examples short
#     @app.route('/')
#     def index():
#         return render_template('index.html')

#     @app.route('/services/<service>')
#     def service(service):
#         findings_table = [(x['section_number'], x['section_name']) for x in service['findings'].items()]
#         print(findings_table)
#         return render_template('service.html', service=service, findings_table=findings_table)

#     @app.route('/services/<service>/<finding>')
#     def finding(service, finding):
#         return render_template('finding.html', service=service, finding=finding)

#     return app

if __name__ == "__main__":
    app.run(debug=True)

