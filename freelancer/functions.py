from datetime import datetime

source_type = {'cold_call':'Cold Call'}

def stringtotimestamp(timestamp):
    return datetime.strptime(str(timestamp).split('.')[0], "%Y-%m-%d %H:%M:%S")

def format_timestamp(data, format):
    if data is None:
        return None
    timestamp = stringtotimestamp(str(data))
    return timestamp.strftime(format)