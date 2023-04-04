from conan.errors import ConanException
from conan.tools.scm import Version

import os
import yaml

def load_config_yaml(recipe_name):
    config_file = os.path.join("recipes", recipe_name, "config.yml")
    if not os.path.exists(config_file):
        raise ConanException(f"The file {config_file} does not exist")

    with open(config_file, "r") as file:
        config_yaml = yaml.safe_load(file)
        if not "versions" in config_yaml:
            raise ConanException(f"{config_file} is missing the required `'versions' key")

        return config_yaml

def parse_top_version_per_recipe_folder(recipe_name):
    config = load_config_yaml(recipe_name)

    known_versions = {}
    for version, folder in config["versions"].items():
        folder_name = folder['folder']
        if not folder_name in known_versions or Version(version) > Version(known_versions[folder_name]):
            known_versions.update({folder_name: version})
    return known_versions

def parse_all_version_and_recipe_folder(recipe_name):
    config = load_config_yaml(recipe_name)

    known_versions = {}
    for version, folder in config["versions"].items():
        folder_name = folder['folder']
        known_versions.update({folder_name: version})
    return known_versions
