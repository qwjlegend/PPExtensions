"""Package sparkmonitor

This package contains two modules:
    kernelextension.py is the Jupyter kernel extension.
    serverextension.py is the Jupyter web server extension.
"""


def _jupyter_nbextension_paths():
    """Used by 'jupyter nbextension' command to install frontend extension"""
    return [dict(
        section="notebook",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="github",
        # _also_ in the `nbextension/` namespace
        require="github/githubcommit"),
        dict(
        section="tree",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="github",
        # _also_ in the `nbextension/` namespace
        require="github/github"),
        dict(
        section="tree",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="github",
        # _also_ in the `nbextension/` namespace
        require="github/githubmain")
    ]


def _jupyter_server_extension_paths():
    """Used by "jupyter serverextension" command to install web server extension'"""
    return [{
        "module": "github.github"
    }]
