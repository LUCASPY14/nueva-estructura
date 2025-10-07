from django.core.cache import cache
from django.conf import settings
import hashlib
import json

class ReportCache:
    CACHE_TTL = getattr(settings, 'REPORT_CACHE_TTL', 3600)  # 1 hora por defecto
    
    @staticmethod
    def get_cache_key(report_type, params):
        """
        Genera una clave única para el caché basada en el tipo de reporte y sus parámetros.
        """
        params_str = json.dumps(params, sort_keys=True)
        key_base = f"report_{report_type}_{params_str}"
        return f"report_cache_{hashlib.md5(key_base.encode()).hexdigest()}"
    
    @classmethod
    def get_report(cls, report_type, params):
        """
        Intenta obtener un reporte del caché.
        """
        cache_key = cls.get_cache_key(report_type, params)
        return cache.get(cache_key)
    
    @classmethod
    def set_report(cls, report_type, params, data):
        """
        Guarda un reporte en el caché.
        """
        cache_key = cls.get_cache_key(report_type, params)
        cache.set(cache_key, data, cls.CACHE_TTL)
    
    @classmethod
    def invalidate_report(cls, report_type, params=None):
        """
        Invalida el caché para un tipo de reporte específico.
        Si no se proporcionan parámetros, se puede implementar un patrón
        para invalidar todos los reportes de ese tipo.
        """
        if params:
            cache_key = cls.get_cache_key(report_type, params)
            cache.delete(cache_key)
        else:
            # Implementar lógica para invalidar todos los reportes del tipo
            pass