import os
import json
import yaml
import inspect as python_inspect

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


# This is me going down the wrong path
from conans.client.cache.cache import ClientCache
from conans.client.profile_loader import ProfileLoader
from conans.model.profile import Profile
from conans.model.options import Options

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

    recipe_folder = os.path.join("recipes", recipe_name)
    if not os.path.isdir(recipe_folder):
        raise ConanException(f"Invalid user input: '{recipe_name}' folder does not exist")
    known_versions = parse_all_version_and_recipe_folder(recipe_name)

    for version, recipe_subfolder in known_versions.items():
        out.title(f"{recipe_name}/{version}")

        conanfile_path = os.path.join(recipe_folder, recipe_subfolder, "conanfile.py")
        if not os.path.isfile(conanfile_path):
            raise ConanException(f"The file {conanfile} does not exist")
        # This just loads the Python Class in "memory"
        conanfile = conan_api.graph.load_conanfile_class(conanfile_path)

        options = None
        # This is taken from the `conan inspect` command
        # https://github.com/conan-io/conan/blob/5bb2b8ddd7b23f460c1b81ee82c78aaf56c208ad/conan/cli/commands/inspect.py#L35
        for name, value in python_inspect.getmembers(conanfile):
            if name.startswith('_') or python_inspect.ismethod(value) \
            or python_inspect.isfunction(value) or isinstance(value, property):
                continue
            if name is "options":
                out.info("Options:")
                default_json_formatter(value)
                options = value

        if not options:
            raise ConanException("Unable to find options object")

        # The processes the recipe up until the exports, so conan's init, setter, export source, etc
        # ref, conanfile = conan_api.export.export(os.path.abspath(conanfile_path), recipe_name, version, None, None)

        # To run configure for (what I want)
        # But this is hidden, so we need to run for the full graph
        # But the methods are not expected to be called so we should not do that since it's unintended
        # - Possible but easily break (e.g setting are not set)

        for option_name, option_values in options.items():
            out.writeln(f"{option_name} can be set to {option_values}")
            for option in option_values:

                # This is destructive! manipulated the host profiles
                # new_opts = Options.loads(f"{option_name}={option}\n")
                # profile_host.options.update_options(new_opts)

                # Try to make a new profile to include the input one by name
                # TODO: Make a new profile `include(default)` with option set

                # Composing profiles ``get_profile`` from the CLI args
                # https://github.com/conan-io/conan/blob/5bb2b8ddd7b23f460c1b81ee82c78aaf56c208ad/conan/api/subapi/profiles.py#L40
                # Directly passing in the CLI args here
                new_host_profile = conan_api.profiles.get_profile(profiles=["default"], options=[f"{option_name}={option}",])

                # > The API is designed ot be close to the CLI

                out.title("Output profiles")
                out.info("Profile host:")
                print(new_host_profile)

                return

                deps_graph = conan_api.graph.load_graph_requires(requires=[ref], tool_requires=[],
                    profile_host=profile_host, profile_build=profile_build, lockfile=None, remotes=[],
                    update=False, check_updates=False)
                conan_api.graph.analyze_binaries(deps_graph, build_mode=["missing"], remotes=[], update=False,
                                        lockfile=None)
                print_graph_packages(deps_graph)
                conan_api.install.install_binaries(deps_graph=deps_graph, remotes=[])

        return deps_graph


