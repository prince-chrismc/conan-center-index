from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class RecipeAttributes(BaseChecker):
    """
    All packages must have a url attribute pointing back to ConanCenterIndex
    """

    __implements__ = IAstroidChecker

    name = "conan-recipe-attributes"
    msgs = {
        "E9015": (
            "Missing license attribute",
            "conan-missing-license-attribute",
            "The member attribute `license` must be declared: `license = '<spdx.com short-identifier>'`.",
        ),
        "E9016": (
            "Missing homepage attribute",
            "conan-missing-homepage-attribute",
            "The member attribute `homepage` must be declared: `homepage = 'https://<official site for the project>'`.",
        ),
        "E9017": (
            "Missing description attribute",
            "conan-missing-description-attribute",
            "The member attribute `description` must be declared: `description = 'something meaningful from the projects homepage'`.",
        ),
    }

    def visit_classdef(self, node: nodes) -> None:
        def _does_node_have_attribute(req: str, node: nodes):
            for attr in node.body:
                children = list(attr.get_children())
                if (
                    len(children) == 2
                    and isinstance(children[0], AssignName)
                    and children[0].name == req
                    and isinstance(children[1], Const)
                ):
                    return True
            return False

        if node.basenames == ["ConanFile"]:
            for req in ["license", "homepage", "description"]:
                if not _does_node_have_attribute(req, node):
                    self.add_message(f"conan-missing-{req}-attribute", node=node)
