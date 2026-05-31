def detect_side(start: dict, point: dict, degrees): 
    if start['lat'] < point['lat'] and start['lng'] < point['lng']:
        return f'{degrees} degrees right' 
    elif start['lat'] < point['lat'] and start['lng'] > point['lng']:
        return f'{degrees} degrees left' 
    elif start['lat'] > point['lat'] and start['lng'] < point['lng']:
        return f'{degrees + 90} degrees right' 
    elif start['lat'] > point['lat'] and start['lng'] > point['lng']:
        return f'{degrees + 90} degrees left' 
    elif degrees == 0: 
        return f'{0} degress' 
    elif degrees == 180: 
        return f'{180} degrees right' 
    elif start['lat'] == point['lat'] and start['lng'] < point['lng']:
        return f'{degrees} degress right' 
    elif start['lat'] == point['lat'] and start['lng'] > point['lng']:
        return f'{degrees} degress left'