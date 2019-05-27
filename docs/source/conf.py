# -*- coding: utf-8 -*-
# -- Path setup --------------------------------------------------------------

import os
import sys
import django
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../..'))

os.environ["DJANGO_SETTINGS_MODULE"] = "autojudge.settings"
django.setup()

# -- Project information -----------------------------------------------------

project = 'autojudge'
copyright = '2019, Vaibhav Sinha, Prateek Kumar, Vishwak Srinivasan'
author = 'Vaibhav Sinha, Prateek Kumar, Vishwak Srinivasan'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = ''

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
]

autodoc_member_order = 'bysource'
source_suffix = '.rst'
master_doc = 'index'
language = None

exclude_patterns = []
pygments_style = 'sphinx'

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'collapse_navigation': False
}
