from django import template                                                                                                                                                        
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def split(word, value):
    return word.split(value)