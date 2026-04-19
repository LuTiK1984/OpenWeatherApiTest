import sys
import os
"""pytest tests/ -v"""
"""pytest tests/ -v --alluredir=allure-results"""
"""C:\allure\bin\allure.bat serve allure-results"""
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))