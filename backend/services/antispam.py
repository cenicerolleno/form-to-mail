def is_bot(data):
    trap = data.get('website')
    return bool(trap and trap.strip())