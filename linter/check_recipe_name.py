from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class RecipeName(BaseChecker):
    """
       All packages must have a lower-case name
    """

    __implements__ = IAstroidChecker

    name = "conan-recipe-name"
    msgs = {
        "E9004": (
            "Reference name should be all lowercase",
            "conan-lowercase-name",
            "Use only lower-case for the package name: `name = 'foobar'`."
        ),
        "E9005": (
            "Missing name attribute",
            "conan-missing-name",
            "The member attribute `name` must be declared as a string: `name = 'foobar'`."
        ),
        "E9014": (
            "Incorrect name attribute",
            "conan-incorrect-name",
            "The member attribute `name` must be declared as a string: `name = 'foobar'`."
        ),
        "W9001": (
            "Inconsistent package class name",
            "conan-inconsistent-class-name",
            "The derived `ConanFile` class should contain the recipe name and have a 'Conan` suffix: `class FooConan(ConanFile):`."
        )
    }

    def visit_classdef(self, node: nodes) -> None:
        if node.basenames == ['ConanFile']:
            classname = node.name
            if not classname.endswith('Conan'):
                self.add_message("conan-inconsistent-class-name", node=node, line=node.lineno)

            for attr in node.body:
                children = list(attr.get_children())
                if len(children) == 2 and \
                   isinstance(children[0], AssignName) and \
                   children[0].name == "name" and \
                   isinstance(children[1], Const):
                    if not isinstance(children[1].value, str):
                        self.add_message("conan-incorrect-name", node=attr, line=attr.lineno)
                        return # Fatal error the rest wont work!
                    value = children[1].as_string()
                    if value.lower() != value:
                        self.add_message("conan-lowercase-name", node=attr, line=attr.lineno)
                    if not classname.lower().startswith(value.replace("'", "")): # String values are quoted :shrug:
                        self.add_message("conan-inconsistent-class-name", node=node, line=node.lineno)
                    return
            self.add_message("conan-missing-name", node=node)
