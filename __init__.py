__author__ = 'Maciej Kamiński Politechnika Wrocławska'

import os,sys
from PyQt5 import uic

def classFactory(iface):
    """invoke plugin"""
    from .plugin import DendrytPlugin

    return DendrytPlugin(iface)
