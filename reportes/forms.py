from django import forms

class ReporteForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    REPORTE_CHOICES = [
        ('ventas', 'Ventas'),
        ('compras', 'Compras'),
        ('stock', 'Stock'),
        ('consumo', 'Consumo por Alumno'),
        ('financiero', 'Financiero'),
    ]
    tipo_reporte = forms.ChoiceField(choices=REPORTE_CHOICES)