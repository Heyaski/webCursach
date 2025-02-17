from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='get_badge_class')
def get_badge_class(dictionary, key):
    item = dictionary.get(key)
    return item.get('badge_class') if item else 'badge-secondary'

@register.filter(name='get_status_text')
def get_status_text(dictionary, key):
    item = dictionary.get(key)
    return item.get('text') if item else 'Не пройден'

@register.filter(name='can_decline')
def can_decline(dictionary, key):
    item = dictionary.get(key)
    return item.get('can_decline') if item else False
