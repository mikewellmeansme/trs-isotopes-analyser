months = ['September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']


def get_highlight_conditions(negative=False):
    return [
                [
                    {
                        'if': {
                            'column_id': f'{month}',
                            'filter_query': f'{{{month}}} contains "p=0.0{i}" && {{{month}}} contains "-"' if negative else f'{{{month}}} contains "p=0.0{i}"'
                        },
                        'backgroundColor': 'red' if negative else 'green',
                        'color': 'white'
                    } 
                for i in range(5)] 
            for month in months]
