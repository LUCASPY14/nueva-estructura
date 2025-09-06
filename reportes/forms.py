from django import forms

BASE_INPUT_CLASSES = 'border border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500'

class ReporteForm(forms.Form):
    start_date = forms.DateField(
        label="Desde",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': BASE_INPUT_CLASSES
        })
    )
    end_date = forms.DateField(
        label="Hasta",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': BASE_INPUT_CLASSES
        })
    )
    REPORTE_CHOICES = [
        ('ventas', 'Ventas'),
        ('compras', 'Compras'),
        ('stock', 'Stock'),
        ('consumo', 'Consumo por Alumno'),
        ('financiero', 'Financiero'),
    ]
    tipo_reporte = forms.ChoiceField(
        label="Tipo de Reporte",
        choices=REPORTE_CHOICES,
        widget=forms.Select(attrs={
            'class': BASE_INPUT_CLASSES
        })
    )
