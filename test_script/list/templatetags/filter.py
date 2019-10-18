from django import template


register = template.Library()

def lookup(value, arg):
    return value[arg]


def get_list(value):
    return list(value)

register.filter('lookup',lookup)

register.filter('get_list',get_list)

