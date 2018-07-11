import json
import os
import yaml
    
def clean_latex(tuple_entry):
    """
    Filter/escape problematic characters
    Our minerva pdf generator chokes on '_', '*', ...
    and possibly other things.
    """
    def _clean_latex(tuple_entry_string):
        processed = False
        for symbol in ['_', '*']:
            if symbol in tuple_entry_string:
                tuple_entry_string = tuple_entry_string.replace(symbol, '\\' + symbol)
                processed = True
        if processed:
            return '\\texttt{' + tuple_entry_string + '}'
        else:
            return tuple_entry_string

    return _clean_latex(str(tuple_entry))
    
    
def render_latex(resource_tuples, header, title):
    header = list(map(clean_latex, header))
    title = clean_latex(title)
    
    render_table_start(header, title)
    num_columns = len(header)
    if num_columns > 1:
        line = ' & '.join(['{}']*num_columns)
    else:
        line = '{}'
    line = line + ' \\\\'
    for resource_tuple in resource_tuples:
        print('    ' + line.format(*map(clean_latex, resource_tuple)))
    render_table_end(header)
    
def render_table_start(header, title):
    """
    Render latex table suitable for minerva rendering
    
            
    If the elements in the table are very long you can correct spacing with invisible text like this:
    {\color[HTML]{FFFFFF} {}} & {\color[HTML]{333333}{spacing}}{\color[HTML]{FFFFFF} {}}{\color[HTML]{333333}{spacing_2}} & {\color[HTML]{333333}{spacing_3}}{\color[HTML]{FFFFFF}{}} \\

    TODO: Paginate pages to break nicely over many pages.
    
    Some exceptions used to manually fix for specific cases:
    
    Text wrap some long arrays based on answer by zyy on
    https://tex.stackexchange.com/questions/54069/table-with-text-wrapping
    
    GROUPS column had variable length and this worked.
    \begin{tabular}{|l|>{\centering\arraybackslash}m{10cm}|}
    \hline
    \multicolumn{2}{|c|}{IAM Users without MFA} \\
    \rowcolor[HTML]{333333}
    {\color[HTML]{FFFFFF}USER NAME} & {\color[HTML]{FFFFFF}GROUPS} \\
    """
    num_columns = len(header)
    entries = ['\color[HTML]{FFFFFF}' + '{}'.format(clean_latex(x)) for x in header]
    if num_columns > 1: 
        line = '} & {'.join(entries)
    else:
        line = entries[0]
    columns_format = '{|' + '|'.join(['l']*num_columns) + '|}'
    print('\\begin{tabular}' + '{}'.format(columns_format) + '\n'
         '    ' + '\\hline\n' +
         '    ' + '\\multicolumn{' + str(num_columns) + '}' +
        '{|c|}' + '{' + title + '}' +  ' \\\\\n' +
        '    ' + '\\rowcolor[HTML]{333333}\n' +
        '    ' + '{' + line + '}' + ' \\\\' 
    )
    

def render_table_end(header):
    """
    Render table end
    """
    print('    \\hline\n' +
          '\\end{tabular}\n')