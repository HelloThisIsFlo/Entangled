def seconds(seconds_num):
    return seconds_num


def minutes(minutes_num):
    return seconds(minutes_num * 60)


config = {
    'mqtt': {
        'user': 'entangled',
        'pass': 'hello',
        'domain': 'localhost',
        'port': 1883,
        'topic': 'entangled'
    },
    'entangled': {
        'start_delay': seconds(30)
    },
    'entangled_mock': {
        'start_delay': seconds(30)
    }
}
