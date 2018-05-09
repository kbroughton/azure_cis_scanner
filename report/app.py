from flask import Flask, render_template
from flask_nav import Nav
from flask_nav.elements import *
import os
import pandas as pd
import yaml

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
    findings_table = [(x['subsection_number'], x['subsection_name']) for x in cis_structure['TOC']['Storage Accounts']]
    print(findings_table)
    return render_template('service.html', service=service, findings_table=findings_table)

@app.route('/services/<service>/<finding>')
def finding(service, finding):
    return render_template('finding.html', service=service, finding=finding)

# registers the "top" menubar

def build_navbar(cis_structure):
    navbar = [('Home', 'index')]
    for section in cis_structure['section_ordering']:
        navbar.append(section, 'finding', service=section)

nav.register_element(
    'top',
    Navbar(
     #*map(View, navbar)

        View('Home', 'index'),
        View('IAM', 'service', service={'findings': [{'subsection_name': 'mfa'}, {'subsection_name': 'admin portal'}]}),
        View('IAM - mfa', 'finding', service='IAM', finding={'subsection_name': 'mfa', 'columns': ['Server', "Database"], 'flagged_items_list': [('a', 'b'), ('c', 'd')]} )
        # View('Our Mission', 'about'),
        # Subgroup('Products',
        #          View('Wg240-Series',
        #               'products',
        #               product='wg240'),
        #          View('Wg250-Series',
        #               'products',
        #               product='wg250'),
        #          Separator(),
        #          Text('Discontinued Products'),
        #          View('Wg10X',
        #               'products',
        #               product='wg10x'), ),
        # Link('Tech Support', 'http://techsupport.invalid/widgits_inc'), 
        )
    )


@app.route("/tables")
def show_tables():
    data = pd.read_excel('dummy_data.xlsx')
    data.set_index(['Name'], inplace=True)
    data.index.name=None
    females = data.loc[data.Gender=='f']
    males = data.loc[data.Gender=='m']
    return render_template('view.html',tables=[females.to_html(classes='female'), males.to_html(classes='male')],
    titles = ['na', 'Female surfers', 'Male surfers'])

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

