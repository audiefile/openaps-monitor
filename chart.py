# coding=utf-8
from dateutil.parser import parse


def glucose_row(date, amount, targets, predicted=False):
    time = parse(date).time()
    target = targets.at(time)

    title = 'Predicted: ' if predicted else ''

    return {'c': [
        {'v': date},
        {'v': amount},
        {'v': not predicted},
        {'v': target.get('low')},
        {'v': target.get('high')},
        {'v': '{} – {}{:.0f} mg/dL'.format(time.strftime('%I:%M %p'), title, round(amount))}
    ]}


def glucose_line_chart(recent_glucose, predicted_glucose, targets):
    # https://developers.google.com/chart/interactive/docs/reference#dataparam

    cols = [{'type': 'date', 'label': 'Date'}]
    rows = []

    if recent_glucose is not None:
        cols.extend([
            {'type': 'number', 'label': 'Glucose'},
            {'type': 'boolean', 'label': 'Glucose Certainty', 'role': 'certainty'},
            {'id': 'rangeMin', 'type': 'number', 'role': 'interval'},
            {'id': 'rangeMax', 'type': 'number', 'role': 'interval'},
            {'type': 'string', 'role': 'tooltip'}
        ])

        for entry in reversed(recent_glucose):
            rows.append(glucose_row(
                entry.get('date') or entry['display_time'],
                entry.get('sgv') or entry.get('amount') or entry['glucose'],
                targets
            ))

        iter_predicted_glucose = iter(predicted_glucose)
        next(iter_predicted_glucose)    
        for entry in iter_predicted_glucose:
            rows.append(glucose_row(entry['date'], entry['glucose'], targets, 'Predicted: '))

    return cols, rows


def input_history_area_chart(normalized_history):
    cols = [{'type': 'date', 'label': 'Date'}]
    rows = []

    if normalized_history is not None:
        cols.extend([
            {'type': 'number', 'label': 'Basal Insulin'},
            {'type': 'string', 'role': 'tooltip'},
            {'type': 'number', 'label': 'Bolus Insulin'},
            {'type': 'string', 'role': 'tooltip'},
            {'type': 'number', 'label': 'Bolus Insulin'},
            {'type': 'string', 'role': 'tooltip'},
            {'type': 'number', 'label': 'Meal carbs'},
            {'type': 'string', 'role': 'tooltip'}
        ])

        for entry in normalized_history:
            for i in range(4):
                key = 'start_at' if i < 2 else 'end_at'
                tooltip = '{} – {}'.format(
                    parse(entry[key]).time().strftime('%I:%M %p'),
                    entry['description']
                )

                if i == 1:
                    amount = entry['amount']
                elif i == 2:
                    amount = entry['amount'] if entry['start_at'] != entry['end_at'] else 0
                else:
                    amount = None
                    tooltip = ''

                values = [None] * 4

                if entry['type'] == 'TempBasal':
                    values[0] = amount
                elif entry['unit'] == 'U/hour':
                    values[1] = amount
                elif entry['type'] == 'Bolus':
                    values[2] = amount
                elif entry['type'] == 'Meal':
                    values[3] = amount

                rows.append({'c': [
                    {'v': entry[key]},
                    {'v': values[0]},
                    {'v': tooltip},
                    {'v': values[1]},
                    {'v': tooltip},
                    {'v': values[2]},
                    {'v': tooltip},
                    {'v': values[3]},
                    {'v': tooltip}
                ]})

    return cols, rows
