from django import template


register = template.Library()


@register.filter
def addclass(field, css):
    """
    :param field: form field name where we need add attribute "class"
    :param css: value of new attribute "class"
    :return: object "field" with added attribute "class"
    """
    return field.as_widget(attrs={'class': css})
