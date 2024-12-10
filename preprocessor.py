import re
import pandas as pd

def preprocess(data):
    # Pattern to handle both 24-hour and 12-hour time formats
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?[APap][Mm])?\s-\s'

    # Extract messages and dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create a DataFrame with user messages and dates
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date to datetime
    # Try parsing both 12-hour and 24-hour formats
    def parse_date(date_str):
        for fmt in ['%d/%m/%y, %H:%M - ', '%m/%d/%y, %I:%M %p - ']:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError:
                continue
        raise ValueError(f"Date format not recognized: {date_str}")

    df['message_date'] = df['message_date'].apply(parse_date)
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Split user messages into users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        if len(entry) > 1:  # If message has a user
            users.append(entry[1])
            messages.append(entry[2])
        else:  # System notification
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Add additional time-related columns
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create periods for time slots (e.g., "23-00")
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour}-{hour + 1}")

    df['period'] = period

    return df

# Example usage
# chat_data = """19/06/24, 09:55 - This is a test message.
# 10/28/20, 12:48 PM - This is another message.
# 19/06/24, 00:15 - Midnight message."""
# processed_data = preprocess(chat_data)
# print(processed_data)
