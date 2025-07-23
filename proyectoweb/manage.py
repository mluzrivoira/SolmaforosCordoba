#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""      
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyectoweb.settings') #apunta a los ajustes del proyecto   
    try:
        from django.core.management import execute_from_command_line  #interpreta los argumentos de la línea de comandos y ejecuta la acción correspondiente.
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
