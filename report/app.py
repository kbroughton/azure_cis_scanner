from flask import Flask, render_template, redirect, url_for, make_response, render_template_string
from flask_nav import Nav
from flask_nav.elements import *
import os
import numpy as np
import pandas as pd
import io
import yaml
import re 
import datetime
import random

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt


from settings import *

with open(os.path.expanduser(APP_ROOT + '/cis_structure.yaml'), 'r') as f:
    cis_structure = yaml.load(f)

#nav = Nav()

app = Flask(__name__)
nav = Nav(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services/<service>')
def service(service):
    findings_table = [(x['subsection_number'], x['subsection_name'], x['finding_name']) for x in cis_structure['TOC'][service]]
    stats = get_latest_stats()
    return render_template('service.html', service=title_except(service), findings_table=findings_table, stats=stats)

@app.route('/services/<service>/<finding>')
def finding(service, finding):
    finding_entry = get_finding_index(cis_structure['TOC'][service], finding)
    service_data = get_filtered_data_by_name(service)
    error_str = ''
    if not service_data:
        error_str = 'No section named {} found'.format(service)
    finding_name = '_'.join(map(str.lower, finding.split(' ')))
    finding_data = service_data.get(finding_name, None)
    if not finding_data:
        error_str = 'No finding named {}'.format(finding)
    if (not finding_data.get("metadata", None)) or \
       (not finding_data.get("metadata").get("columns", None)) or \
       (not finding_data.get("items", None)):
        error_str = 'Finding data for {} missing metadata, columns or items'.format(finding)

    if error_str:
        return render_template('finding.html', service=service, finding=finding,
            finding_entry=finding_entry, table='', title=title_except(finding), error_str=error_str)
    else:
        data = pd.DataFrame(finding_data['items'], columns=finding_data['metadata']['columns'])
        return render_template('finding.html', service=service, finding=finding,
            finding_entry=finding_entry, table=data.to_html(), title=title_except(finding))

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

@app.route("/static/graphs/<service>/<finding>.png")
def graph(service, finding):

    stats = get_stats()
    fig=Figure()
    ax=fig.add_subplot(111)
    ax.set_xlabel('date')
    ax.set_ylabel('findings count')
    ax.set_title('Total Security Findings vs Time (days)')
    ax.axes.set_ylim([0,45])
    ax.autoscale(enable=False, axis='y', tight=False)

    x=[]
    y=[40, 38, 30, 30, 30, 22, 20, 20, 18, 16]
    #plt.ylim(max(y), 0)
    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now+=delta
    
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    png_output = io.BytesIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route("/graphs/<service>/<finding>.png")
def plot_finding(service, finding):
    section_name = service
    subsection_name = finding
    stats = get_stats()
    df = multi_index_df_from_stats(stats)
    finding_df = df.loc[section_name].loc[subsection_name]
    y = finding_df["Flagged"].tolist()
    y = np.array(y)
    x = finding_df.index
    
    #x = np.array([str(xx.month) + '-' + ( str(xx.day) if len(str(xx.day))==2 else '0' + str(xx.day) ) for xx in x])
    print(x)
    #x = x.day
    mask = np.isfinite(y)

    fig, ax = plt.subplots()
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    ax.axes.set_ylabel('Items Flagged for Finding')
    ax.axes.set_xlabel('Date')
    ax.set_title(subsection_name, verticalalignment='bottom')
    line, = ax.plot(x[mask],y[mask], ls="--",lw=1)
    ax.plot(x,y, color=line.get_color(), lw=1.5)

    canvas=FigureCanvas(fig)
    png_output = io.BytesIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

def multi_index_tuples_from_stats(stats):
    """
    Create a multi-index panel from stats
    
    The major axis is a multi-index is created from the first two levels of a dict (section, finding)
    The minor axis is the date
    The data columns are items_checked, items_flagged
    """
    frames = []
    tuples = []
    index_tuples = []
    for section in cis_structure['section_ordering']:
        for subsection in cis_structure['TOC'][section]:
            subsection_name = subsection['subsection_name']
            finding_name = '_'.join(map(str.lower, subsection_name.split(' ')))
            start_date, end_date = min_max_dates()
            for date in sorted(pd.date_range(start=start_date, end=end_date, freq='D')):
                str_date = datetime_to_dir_date(date)
                has_data = True
                if section not in stats:
                    has_data = False
                elif finding_name not in stats[section]:
                    has_data = False
                if has_data and (str_date in stats[section][finding_name]):
                    item_stats = stats[section][finding_name][str_date]
                    items_checked, items_flagged = item_stats['items_checked'], item_stats['items_flagged']
                else:
                    items_checked, items_flagged = None, None
                tuples.append((section, subsection_name, date, items_flagged, items_checked))
                index_tuples.append((section, subsection_name, date))                
    return tuples, index_tuples
            
def multi_index_df_from_stats(stats):
    tuples, index_tuples = multi_index_tuples_from_stats(stats)
    multi_index = pd.MultiIndex.from_tuples(index_tuples, names=["section", "finding", "date"])
    return pd.DataFrame(tuples, index=multi_index, columns=["section_drop", "finding_drop", "date","Flagged", "Checked"])

def dir_date_to_datetime(string):
    """
    Takes format of directory '%Y-%m-%d' and converts to datetime"""
    return datetime.datetime.strptime(string, "%Y-%m-%d")

def datetime_to_dir_date(dt):
    """
    Takes format of directory '%Y-%m-%d' and converts to datetime"""
    return dt.strftime("%Y-%m-%d")

def min_max_dates():
    dates = list(map(dir_date_to_datetime, get_dirs()))
    return min(dates), max(dates)


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

