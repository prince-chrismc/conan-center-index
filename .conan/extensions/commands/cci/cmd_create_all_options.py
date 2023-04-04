import os
import json
import yaml

# conan config install .conan
# conan cci:create-all-options -n fmt

from conan.api.output import ConanOutput
from conan.cli.args import add_profiles_args
from conan.cli.command import conan_command, OnceArgument
from conan.cli.commands.test import run_test
from conan.cli.formatters import default_json_formatter
from conan.cli.formatters.graph.graph_info_text import filter_graph
from conan.cli.printers.graph import print_graph_packages

from conan.errors import ConanException


from .cci_list_or_name import parse_list_from_args
from .cci_load_config_yml import parse_all_version_and_recipe_folder


def output_json(results):
    default_json_formatter(results.serialize())


@conan_command(group="Conan Center Index", formatters={"json": output_json})
def create_all_options(conan_api, parser, *args):
    """
    Build the combinatorics of options available in a given recipe
    """
    parser.add_argument('-n', '--name', action=OnceArgument, help="Name of the recipe to export")
    # parser.add_argument('-l', '--list', action=OnceArgument, help="YAML file with list of recipes to export")
    add_profiles_args(parser)
    args = parser.parse_args(*args)

    recipes_to_create = parse_list_from_args(args)

    out = ConanOutput()

    profile_host, profile_build = conan_api.profiles.get_profiles_from_args(args)
    out.title("Input profiles")
    out.info("Profile host:")
    out.info(profile_host.dumps())
    out.info("Profile build:")
    out.info(profile_build.dumps())

    recipe_name = recipes_to_create[0] # limited to just using a single recipe for now
    out.verbose(f"Beginning to look into {recipe_name}")
    known_versions = parse_all_version_and_recipe_folder(recipe_name)

    for _, version_to_build in known_versions.items():
        reference = f"{recipe_name}/{version_to_build}"
        out.title(reference)

        # This is assuming the "export all command" was run before hand
        in_cache = False if not conan_api.search.recipes(reference, remote=None) else True # None remote is "local cache"
        if not in_cache:
            raise ConanException(f"{reference} was not found in the cache")

        deps_graph = conan_api.graph.load_graph_requires(requires=[reference], tool_requires=[],
            profile_host=profile_host, profile_build=profile_build, lockfile=None, remotes=[],
            update=False, check_updates=False)
        conan_api.graph.analyze_binaries(deps_graph, build_mode=["missing"], remotes=[], update=False,
                                lockfile=None)
        print_graph_packages(deps_graph)

        return deps_graph


