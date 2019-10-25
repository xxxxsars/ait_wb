from django import template

register = template.Library()


def get_key(value):
    print(value)
    first_key = [k for k in value.keys()][0]

    return first_key


def lookup(value, arg):
    return value[arg]


def get_list(value):
    return list(value)


register.filter('lookup', lookup)
register.filter('get_key', get_list)
register.filter('get_list', get_list)
