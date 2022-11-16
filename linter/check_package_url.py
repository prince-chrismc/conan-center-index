from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class PackageUrl(BaseChecker):
    """
       All packages must have a url attribute pointing back to ConanCenterIndex
    """

    __implements__ = IAstroidChecker

    name = "conan-package-name"
    msgs = {
        "E9012": (
            "Recipe URL should be ",
            "conan-bad-url-attribute",
            "Use only CCI for URL: `url = 'https://github.com/conan-io/conan-center-index'`."
        ),
        "E9013": (
            "Missing url attribute",
            "conan-missing-url-attribute",
            "The member attribute `url` must be declared: `url = 'https://github.com/conan-io/conan-center-index'`."
        )
    }

    def visit_classdef(self, node: nodes) -> None:
        if node.basenames == ['ConanFile']:
            for attr in node.body:
                children = list(attr.get_children())
                if len(children) == 2 and \
                   isinstance(children[0], AssignName) and \
                   children[0].name == "url" and \
                   isinstance(children[1], Const):
                    value = children[1].as_string()
                    if value.lower() != value:
                        self.add_message("conan-bad-url-attribute", node=attr, line=attr.lineno)
                    return
            self.add_message("conan-missing-url-attribute", node=node)
