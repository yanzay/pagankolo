# coding=utf-8
import os
#from google.appengine.ext.webapp import template
#from jinja2 import Template
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader
from webapp2_extras import jinja2

env = jinja2.Environment(loader=PackageLoader('pagankolo', 'templates'))
template_dir = os.path.dirname(__file__)+'\\templates'

def renderTemplate(hdlr,templ_name,templ_values):
    template = env.get_template(templ_name)
    path = os.path.join(template_dir,templ_name)
    hdlr.response.out.write(template.render(path,templ_values))