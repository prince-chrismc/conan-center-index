from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Call, AssignName, Arguments, If,Expr


class RecipeSources(BaseChecker):
    """
       All recipes should use ``tools.files.get`` to download sources at least once
    """

    __implements__ = IAstroidChecker

    name = "conan-recipe-sources"
    msgs = {
        "E9018": (
            "Recipe source methods should use `conan.tools.files.get`",
            "conan-recipe-missing-source-method",
            "words here"
        )
    }

    _method_arguments = []

    def visit_classdef(self, node: nodes) -> None:
        if node.basenames == ['ConanFile']:
            for attr in node.body:
                children = list(attr.get_children())
                print(children)
                if len(children) == 2 and \
                   isinstance(children[0], Arguments) and isinstance(children[1], If) and isinstance(children[1].test, Call):
                   print("-- this ---" , children[1].test)

    def visit_functiondef(self, node: nodes) -> None:
        print("---------------------- HERE -------------------")
        print(node.name)
        if len(node.body) >= 0:
            if isinstance(node.body[0], Expr) and isinstance(node.body[0].value, Call):
                call = node.body[0].value
                print(call.func)
        print(node.args.args)
