# custom_tags.py
from django import template
from ..models import FavoriteTour

register = template.Library()

@register.filter
def favorite_tour(user, tour):
    return FavoriteTour.objects.filter(user=user, tour=tour).exists()
