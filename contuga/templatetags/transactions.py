from django import template

register = template.Library()


@register.inclusion_tag("templatetags/show_transfer_transaction.html")
def show_transfer_transaction(transaction):
    return {"transaction": transaction}
