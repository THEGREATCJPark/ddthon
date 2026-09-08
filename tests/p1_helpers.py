def snapshot(rows, name='Data', row=1, col=1):
    return {'sheets': [{'name': name, 'first_row': row, 'first_col': col,
                        'values': [list(r) for r in rows]}]}

PROC = {'action': 'file-access', 'method': 'excel-com-attach'}
MAPPING = {'sheet': 'Data', 'month_col': 1, 'total_col': 2, 'first_row': 1}
