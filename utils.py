def get_duration(start_date, end_date, unit):
    if unit == 'Yearly':
        return end_date.year - start_date.year
    elif unit == 'Monthly':
        years_diff = end_date.year - start_date.year
        months_diff = end_date.month - start_date.month
        return years_diff * 12 + months_diff
    elif unit == 'Weekly':
        total_days = (end_date - start_date).days
        return total_days // 7  # Integer division to get whole weeks
    elif unit == 'Daily':
        return (end_date - start_date).days