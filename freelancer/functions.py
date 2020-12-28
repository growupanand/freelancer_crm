from datetime import datetime

def stringtotimestamp(timestamp):
    return datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S")

def format_timestamp(data, format):
    timestamp = stringtotimestamp(str(data))
    return timestamp.strftime(format)