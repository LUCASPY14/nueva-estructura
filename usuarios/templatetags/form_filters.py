from django import template
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_classes):
    """
    Añade clases CSS a un campo de formulario.
    Uso: {{ form.field|add_class:"clase1 clase2" }}
    """
    return field.as_widget(attrs={
        "class": f"{field.field.widget.attrs.get('class', '')} {css_classes}".strip()
    })