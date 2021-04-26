import importlib
import pkgutil

import secondlife.plugins

# Reference: https://packaging.python.org/guides/creating-and-discovering-plugins/
def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

def load_plugins():
    global loaded_plugins
    
    loaded_plugins = {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespace(secondlife.plugins)
    }
