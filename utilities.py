import datetime


def valid_meal_time(meal_time):
    if meal_time != 'breakfast' and meal_time != 'lunch' and meal_time != 'dinner':
        return False
    else:
        return True


def valid_date_and_time(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M')
        return True
    except ValueError:
        return False

