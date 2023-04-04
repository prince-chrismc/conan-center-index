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
        conanfile = conan_api.graph.load_conanfile_class(conanfile_path)

        options = None
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

        ref, conanfile = conan_api.export.export(os.path.abspath(conanfile_path), recipe_name, version, None, None)


        for option_name, option_values in options.items():
            out.writeln(f"{option_name} can be set to {option_values}")
            for option in option_values:

                new_opts = Options.loads(f"{option_name}={option}\n")
                profile_host.options.update_options(new_opts)
                print(profile_host)

                return

                deps_graph = conan_api.graph.load_graph_requires(requires=[ref], tool_requires=[],
                    profile_host=profile_host, profile_build=profile_build, lockfile=None, remotes=[],
                    update=False, check_updates=False)
                conan_api.graph.analyze_binaries(deps_graph, build_mode=["missing"], remotes=[], update=False,
                                        lockfile=None)
                print_graph_packages(deps_graph)
                conan_api.install.install_binaries(deps_graph=deps_graph, remotes=[])

        return deps_graph


