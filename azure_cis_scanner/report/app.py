from flask import Flask, render_template, redirect, url_for, session, make_response, render_template_string
from flask_nav import Nav
from flask_nav.elements import *
import argparse
import os
import numpy as np
import pandas as pd
import io
import yaml
import re 
import datetime
import random

from azure_cis_scanner import utils
from azure_cis_scanner.report import settings
from azure_cis_scanner.report.render_utils import *

HAS_MATPLOTLIB = False

try:
    import matplotlib
    #matplotlib.use('TkAgg')
    matplotlib.use('Agg')
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError as e:
    print(e)
    print("Unable to import matplotlib.  No graphing available.")
except RuntimeError as e:
    print(e)
    print("Unable to import matplotlib.  No graphing available.")

app = Flask(__name__)
nav = Nav(app)
app.secret_key = os.urandom(16)
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def index_base():
    return redirect("/{}".format(app.config['ACTIVE_SUBSCRIPTION_DIR']), code=302)

@app.route('/_subscription_dir')
def _subscription_dir():
    selected_active_subscription_dir = request.args.get('state', session.get('active_subscription_dir', None))
    print('selected_active_subscription_dir2', selected_active_subscription_dir)

    print('subscription_dir route', subscription_dir)

    session['ACTIVE_SUBSCRIPTION_DIR'] = subscription_dir
    return jsonify({'selected': subscription_dir})

@app.route('/<active_subscription_dir>')
def index(active_subscription_dir, methods=['POST','GET']):
    selected_active_subscription_dir = request.args.get('selected', session.get('ACTIVE_SUBSCRIPTION_DIR', active_subscription_dir))
    session['active_subscription_dir'] = selected_active_subscription_dir
    state = {'selected', selected_active_subscription_dir}
    print('selected_active_subscription_dir', selected_active_subscription_dir)
    if selected_active_subscription_dir != active_subscription_dir:
        print('redirecting', selected_active_subscription_dir)
        return redirect('/'+selected_active_subscription_dir)
    else:
        accounts = utils.get_accounts()
        subscription_dirs = [(subscription_dir_from_account(account), subscription_dir_from_account(account)) for account in accounts]
        print('subscription_dirs', subscription_dirs)
        return render_template('index.html', 
            active_subscription_dir=active_subscription_dir, 
            state=state,
            subscription_dirs=subscription_dirs)

@app.route('/services/<service>')
def service(service):
    findings_table = [(x['subsection_number'], x['subsection_name'], get_finding_name(x['finding_name'], x['subsection_name'])) for x in cis_structure['TOC'][service]]
    stats = get_latest_stats(app.config['SCANS_DATA_DIR'])
    #pprint.pprint("service:stats: {}".format(stats))
    return render_template('service.html', service=service, title=title_except(service), findings_table=findings_table, stats=stats)

@app.route('/services/<service>/<finding>')
def finding(service, finding):
    """
    Render the non-graph portion of the finding as a table of the latest date recording this finding
    The graph portion is rendered in plot_finding
    """
    finding_entry = get_finding_index(cis_structure['TOC'][service], finding)
    service_data = get_filtered_data_by_name(app.config['SCANS_DATA_DIR'], service)
    pprint.pprint("finding:service_data: {}".format(service_data))
    error_str = ''
    if not service_data:
        error_str = 'No section named "{}" found\n'.format(service)
    finding_name = get_finding_name(finding_entry['finding_name'], finding_entry['subsection_name'])
    finding_data = service_data.get(finding_name, None)
    print("finding_data {}".format(finding_data))
    date = finding_data.get('date', 'No Date')
    if not finding_data:
        error_str += 'No finding named "{}" in {}\n'.format(finding, service_data.keys())
    elif (not finding_data.get("metadata", None)):
        error_str += 'No metadata for "{}"\n'.format(finding)
    elif not finding_data.get("metadata").get("columns", None):
        error_str += 'No columns in metadata for "{}"\n'.format(finding)
    elif not finding_data.get("items", None):
        error_str += 'No items list for "{}"\n'.format(finding)
    elif not finding_data.get("stats", None):
        error_str += 'No stats section in finding_data {}'.format(finding)
    elif not finding_data.get("stats", None):
        error_str += 'No stats section in finding_data {}'.format(finding)
    if error_str:
        return render_template('finding.html', service=service, finding=finding, date=date,
            finding_entry=finding_entry, table='', title=title_except(finding), error_str=error_str, items_checked=0)
    else:
        items_checked=finding_data['stats']['items_checked']
        data = pd.DataFrame(finding_data['items'], columns=finding_data['metadata']['columns'])
        return render_template('finding.html', service=service, finding=finding, date=date,
            finding_entry=finding_entry, table=data.to_html(), title=title_except(finding), items_checked=items_checked)

@app.route("/subscription_dir/<subscription_dir>")
def set_subscription_dir(subscription_dir):
    active_subscription_dir = subscription_dir
    return redirect("/{}".format(active_subscription_dir), code=302)


def subscription_dir_from_account(account):
    return account['name'].split(' ')[0] + '-' + account['id'].split('-')[0]

# Todo: use wrappers to generate the nav bars.  Too tricky for now.  Generated with print statements.
# def build_navbar(cis_structure):
#     navbar = [('Home', 'index')]
#     kwarg_list = [ dict(service=section) for section in cis_structure['section_ordering'] ]
#     arg_list = [ (section, 'section') for section in cis_structure['section_ordering'] ]
#     navbar = list(map(mappable_f, zip(arg_list, kwarg_list)))
#     print(navbar)
#     return navbar

@app.route("/graphs/<service>/<finding>.png")
def plot_finding(service, finding):
    if not HAS_MATPLOTLIB:
        return make_response("Install matplotlib for graphing support")
    section_name = service
    subsection_name = finding
    stats = get_stats(app.config['SCANS_DATA_DIR'])
    df = multi_index_df_from_stats(stats)
    finding_df = df.loc[section_name].loc[subsection_name]
    if len(finding_df) < 2:
        return make_response('Need at least 2 days of data for a plot.  Come back tomorrow!')
    filled_df = finding_df.fillna(method='ffill')
    #y_filled = filled_df["Flagged"].tolist()
    #y_filled = np.array(y_filled)
    y = finding_df["Flagged"].tolist()
    y = np.array(y)
    x = finding_df.index
    print("plot_finding x: ", x)
    print("plot_finding y: ", y)
    mask = np.isfinite(y)

    fig, ax = plt.subplots()
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    ax.axes.set_ylabel('Items Flagged for Finding')
    ax.axes.set_xlabel('Date')
    ax.set_title(subsection_name, verticalalignment='bottom')
    line, = ax.plot(x[mask],y[mask], ls="--",lw=1)
    print("line", line)
    ax.plot(x,y, color=line.get_color(), lw=1.5)

    png_output = io.BytesIO()
    canvas = FigureCanvas(fig)
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
            #print("start_date {} end_date {}".format(start_date, end_date))
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
    #print(multi_index)
    return pd.DataFrame(tuples, index=multi_index, columns=["section_drop", "finding_drop", "date", "Flagged", "Checked"])

def dir_date_to_datetime(string):
    """
    Takes format of directory '%Y-%m-%d' and converts to datetime"""
    return datetime.datetime.strptime(string, "%Y-%m-%d")

def datetime_to_dir_date(dt):
    """
    Takes format of directory '%Y-%m-%d' and converts to datetime"""
    return dt.strftime("%Y-%m-%d")

def min_max_dates():
    dates = list(map(dir_date_to_datetime, get_dirs(app.config['SCANS_DATA_DIR'])))
    return min(dates), max(dates)


nav.register_element(
    'top',
    Navbar(
        View('Identity and Access Management', 'service', service='Identity and Access Management'),
        View('Security Center', 'service', service='Security Center'),
        View('Storage Accounts', 'service', service='Storage Accounts'),
        View('SQL Servers', 'service', service='SQL Servers'),
        View('Logging and Monitoring', 'service', service='Logging and Monitoring'),
        View('Networking', 'service', service='Networking'),
        View('Virtual Machines', 'service', service='Virtual Machines'),
        View('Other Security Considerations', 'service', service='Other Security Considerations'),
        )
    )

def main(parser=None):
    """
    parser is a parsed argparse parser passed in from controller
    """
    if not parser:
        mainparser = argparse.ArgumentParser()
        mainparser.add_argument('--tenant-id', default=None, help='azure tenant id, if None, use default.  Scanner assumes different runs/project dirs for distinct tenants')
        mainparser.add_argument('--subscription-id', default=None, help='azure subscription id, if None, use default, if "all" use all subscriptions with default tenant')
        mainparser.add_argument('--use-api-for-auth', default=True, help='if false, use azure cli calling subprocess, else use python-azure-sdk')
        mainparser.add_argument('--scans-dir', default='/engagements/cis_test/sacans', help='base dir of where to place or load files')
        mainparser.add_argument('--example-scan', action='store_true', help='allow running without credentials on example_scan data')

        parser = mainparser.parse_args()

    # TODO figure out better way to get base dir or let user select in UI
    credentials_tuples = utils.set_credentials_tuples(parser)

    tenant_id, subscription_id, subscription_name, credentials = credentials_tuples[0]
    subscription_dirname = utils.get_subscription_dirname(subscription_id, subscription_name)
    active_subscription_dir = subscription_dirname
    scans_dir = utils.set_scans_dir(parser.scans_dir)
    
    app.config['ACTIVE_SUBSCRIPTION_DIR'] = active_subscription_dir
    app.config['SCANS_DIR'] = scans_dir
    app.config['SCANS_DATA_DIR'] = os.path.join(scans_dir, active_subscription_dir)
    app.config['ACCOUNTS'] = utils.get_accounts(scans_dir)
    #app.config['STATS'] = get_stats()
    app.run(debug=True, host='0.0.0.0', use_reloader=False)


if __name__ == "__main__":
    main()


