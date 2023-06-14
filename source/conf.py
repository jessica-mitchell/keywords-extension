# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import subprocess, os

project = 'keywords-extension'
copyright = '2023, DT, JM'
author = 'DT, JM'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['breathe']

# this is where the xml should be placed
breathe_projects = {"keywords-ext": "_doxygen/xml"}
breathe_default_project = "keywords-ext"

templates_path = ['_templates']
exclude_patterns = []



read_the_docs_build = os.environ.get('READTHEDOCS', None) == 'True'

if read_the_docs_build:

     subprocess.call('cd ../doxygen; doxygen', shell=True)
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_material'
html_static_path = ['_static']
