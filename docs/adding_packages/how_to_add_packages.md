# Adding Packages to ConanCenter

First thing is know what library you want to add. Conan packages are always lowercase.
Take note of the license and URL for the project, to fill in the `conanfile.py` attributes later.

<!-- toc -->
## Contents<!-- endToc -->

## Styling Guidelines

There are many conventions in ConanCenter, a few of them are outline below. They are always to make maintaining the large number of recipes easier for everyone.

### Trailing white-spaces

Avoid trailing white-space characters, if possible

### Quotes

If possible, try to avoid mixing single quotes (`'`) and double quotes (`"`) in python code (`conanfile.py`, `test_package/conanfile.py`). Consistency is preferred.

## Recipe files structure

Every entry in the `recipes` folder contains all the files required by Conan to create the binaries for all the versions of one library. Those
files don't depend on any other file in the repository (we are not using `python_requires`) and every pull-request can modify only one of those
folders at a time.

This is the canonical structure of one of these folders, where the same `conanfile.py` recipe is suitable to build all the versions of the library:

> :information_source: For the updating the structure with the v2 migration [see here](../v2_migration.md#recipe-structure)

```
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- conanfile.py
|           +-- conandata.yml
|           +-- test_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- test_pacakge.cpp
```

If it becomes too complex to maintain the logic for all the versions in a single `conanfile.py`, it is possible to split the folder `all` into
two or more folders, dedicated to different versions, each one with its own `conanfile.py` recipe. In any case, those folders should replicate the
same structure.

### `config.yml`

This file lists the versions that should be built along with the folders where they are located - this should be `all`.

```yml
versions:
  "2.1.0":
    folder: all
```

- `versions` is a top level dictionary, containing a list of known versions.
- `folder` is a string entry providing the name of the folder, relative to the current directory where the `conanfile.py` that
can package that given folder.

It's strongly preferred to only have one one recipe, however if it's no possible to maintain one recipe for all version, older version maybe moved to a
separate folder.

```yml
versions:
  "1.1.1":
    folder: 1.x.x
  "2.0.0":
    folder: all
  "2.1.0":
    folder: all
```

### `conandata.yml`

This file lists **all the sources that are needed to build the package**: source code, license files,... any file that will be used by the recipe
should be listed here. The file is organized into two sections, `sources` and `patches`, each one of them contains the files that are required
for each version of the library. All the files that are downloaded from the internet should include a checksum, so we can validate that
they are not changed.

For more information about picking source tarballs, adding or removing versions, or what the rules are for patches - continue reading our
[Sources and Patches](sources_and_patches.md) guide.

> :information_source: Under our mission to ensure quality, patches undergo extra scrutiny. **Make sure to review** our
> [Modifying sources policy](sources_and_patches.md#policy-about-patching)

A detailed breakdown of all the fields can be found in [conandata_yml_format.md](conandata_yml_format.md). We strongly recommend adding the
[patch fields](conandata_yml_format.md#patches-fields) to help track where patches come from and what issue they solve.

Inside the `conanfile.py` recipe, this data is available in a `self.conan_data` attribute that can be used as follows:

```py
def source(self):
    files.get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

def export_sources(self):
    for patch in self.conan_data.get("patches", {}).get(self.version, []):
        files.copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

def build(self):
    files.apply_conandata_patches(self)
    [...]
```

### The _recipe folder_

#### `conanfile.py`

This file is the recipe contain the logic to build the libraries from sources for all the configurations.
It's the single most important part of writing a package.

Each recipe should derive the `ConanFile` class and implement key attributes and methods.

- Basic attributes and conversions can be found in [recipe attributes](recipe_attributes.md)
- Some of the key methods are outline in this document and will link to more details

Also, **every `conanfile.py` should be accompanied by at least one folder to test the generated packages** as we will see below.

##### Dependencies

When a package needs other packages those are can be include with the `requirements()` methods.

```python
def requirements(self):
    self.require("fmt/9.0.0")
```

For more information see the [Dependencies and Requirements](dependencies_and_requirements.md) documentation for more use cases.

#### The test package folders: `test_package`

All the packages in this repository need to be tested before they join ConanCenter. A `test_package` folder with its corresponding `conanfile.py` and
a minimal project to test the package is strictly required. You can read about it in the
[Conan documentation](https://docs.conan.io/en/latest/creating_packages/getting_started.html#the-test-package-folder).

> **Note.-** If, for any reason, it is useful to write a test that should only be checked using Conan v1, you can do so by using the pattern
> `test_v1_*/conanfile.py` for the folder. Please, have a look to [linter notes](v2_linter.md) to know how to prevent the linter from
> checking these files.

> Remember that the `test_<package>` recipes should **test the package configuration that has just been generated** for the _host_ context, otherwise
> it will fail in crossbuilding scenarios.

### CMake targets

When using CMake to test a package, the information should be consumed using the **targets provided by `cmake_find_package_multi` generator**. We
enforce this generator to align with the upcoming
[Conan's new `CMakeDeps` generator](https://docs.conan.io/en/latest/reference/conanfile/tools/cmake/cmakedeps.html?highlight=cmakedeps)
and it should help in the migration (and compatibility) with Conan v2.

In ConanCenter we try to accurately represent the names of the targets and the information provided by CMake's modules and config files that some libraries
provide. If CMake or the library itself don't enforce any target name, the default ones provided by Conan should be recommended. The minimal project
in the `test_package` folder should serve as an example of the best way to consume the package, and targets are preferred over raw variables.

This rule applies for the _global_ target and for components ones. The following snippet should serve as example:

We encourage contributors to check that not only the _global_ target works properly, but also the ones for the components. It can be
done creating and linking different libraries and/or executables.

#### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(package REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE package::package)
```

#### V1 Test Package CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(package REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} package::package)
```

#### Testing more generators with `test_<something>`

The CI will explore all the folders and run the tests for the ones matching `test_*/conanfile.py` pattern. You can find the output of all
of them together in the testing logs.

Sometimes it is useful to test the package using different build systems (CMake, Autotools,...). Instead of adding complex logic to one
`test_package/conanfile.py` file, it is better to add another `test_<something>/conanfile.py` file with a minimal example for that build system. That
way the examples will be short and easy to understand and maintain. In some other situations it could be useful to test different Conan generators
(`cmake_find_package`, `CMakeDeps`,...) using different folders and `conanfile.py` files ([see example](https://github.com/conan-io/conan-center-index/tree/master/recipes/fmt/all)).

When using more than one `test_<something>` folder, create a different project for each of them to keep the content of the `conanfile.py` and the
project files as simple as possible, without the need of extra logic to handle different scenarios.

```
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- conanfile.py
|           +-- conandata.yml
|           +-- test_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- main.cpp
|           +-- test_cmakedeps/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- conanfile.py
```

### Minimalist Source Code

The contents of `test_package.c` or `test_package.cpp` should be as minimal as possible, including a few headers at most with simple
instantiation of objects to ensure linkage and dependencies are correct. Any build system can be used to test the package, but
CMake or Meson are usually preferred.

## How to provide a good recipe

The [recipes](https://github.com/conan-io/conan-center-index/tree/master/recipes) available in CCI can be used as good examples, you can use them as the base for your recipe. However it is important to note Conan features change over time and our best practices evolve so some minor details may be out of date due to the vast number of recipes.

### Header Only

If you are looking for header-only projects, you can take a look on [rapidjson](https://github.com/conan-io/conan-center-index/blob/master/recipes/rapidjson/all/conanfile.py), [rapidxml](https://github.com/conan-io/conan-center-index/blob/master/recipes/rapidxml/all/conanfile.py), and [nuklear](https://github.com/conan-io/conan-center-index/blob/master/recipes/nuklear/all/conanfile.py). Also, Conan Docs has a section about [how to package header-only libraries](https://docs.conan.io/en/latest/howtos/header_only.html).

### CMake

For C/C++ projects which use CMake for building, you can take a look on [szip](https://github.com/conan-io/conan-center-index/blob/master/recipes/szip/all/conanfile.py) and [recastnavigation](https://github.com/conan-io/conan-center-index/blob/master/recipes/recastnavigation/all/conanfile.py).

#### Components

Another common use case for CMake based projects, both header only and compiled, is _modeling components_ to match the `find_package` and export the correct targets from Conan's generators. A basic examples of this is [cpu_features](https://github.com/conan-io/conan-center-index/blob/master/recipes/cpu_features/all/conanfile.py), a moderate/intermediate example is [cpprestsdk](https://github.com/conan-io/conan-center-index/blob/master/recipes/cpprestsdk/all/conanfile.py), and a very complex example is [OpenCV](https://github.com/conan-io/conan-center-index/blob/master/recipes/opencv/4.x/conanfile.py).

### Autotools

However, if you need to use autotools for building, you can take a look on [mpc](https://github.com/conan-io/conan-center-index/blob/master/recipes/mpc/all/conanfile.py), [libatomic_ops](https://github.com/conan-io/conan-center-index/blob/master/recipes/libatomic_ops/all/conanfile.py), [libev](https://github.com/conan-io/conan-center-index/blob/master/recipes/libev/all/conanfile.py).

#### Components

Many projects offer **pkg-config**'s `*.pc` files which need to be modeled using components. A prime example of this is [Wayland](https://github.com/conan-io/conan-center-index/blob/master/recipes/wayland/all/conanfile.py).

### No Upstream Build Scripts

For cases where a project only offers source files, but not a build script, you can add CMake support, but first, contact the upstream and open a PR offering building support. If it's rejected because the author doesn't want any kind of build script, or the project is abandoned, CCI can accept your build script. Take a look at [Bzip2](https://github.com/conan-io/conan-center-index/blob/master/recipes/bzip2/all/CMakeLists.txt) and [DirectShowBaseClasses](https://github.com/conan-io/conan-center-index/blob/master/recipes/directshowbaseclasses/all/CMakeLists.txt) as examples.

### System Packages

> :information_source: For exceptional cases where only system packages can be used and a regular Conan package may result in an incompatible and fragile package, a separated system package may be created. See the [FAQs](faqs.md#can-i-install-packages-from-the-system-package-manager) for more.

The [SystemPackageTool](https://docs.conan.io/en/latest/reference/conanfile/methods.html#systempackagetool) can easily manage a system package manager (e.g. apt,
pacman, brew, choco) and install packages which are missing on Conan Center but available for most distributions. It is key to correctly fill in the `cpp_info` for the consumers of a system package to have access to whatever was installed.

As example there are [glu](https://github.com/conan-io/conan-center-index/blob/master/recipes/glu/all/conanfile.py) and [OpenGL](https://github.com/conan-io/conan-center-index/blob/master/recipes/opengl/all/conanfile.py). Also, it will require an exception rule for [conan-center hook](https://github.com/conan-io/hooks#conan-center), a [pull request](https://github.com/conan-io/hooks/pulls) should be open to allow it over the KB-H032.
