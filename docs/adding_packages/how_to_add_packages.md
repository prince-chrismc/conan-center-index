# Adding Packages to ConanCenter

First thing is know what library you want to add. Conan packages are always lowercase.
Take note of the license and URL for the project, to fill in the `conanfile.py` attributes later.

<!-- toc -->
## Contents

  * [Recipe files structure](#recipe-files-structure)
    * [`config.yml`](#configyml)
    * [`conandata.yml`](#conandatayml)
    * [The _recipe folder_: `conanfile.py`](#the-_recipe-folder_-conanfilepy)
    * [The test package folders: `test_package` and `test_<something>`](#the-test-package-folders-test_package-and-test_something)
  * [How to provide a good recipe](#how-to-provide-a-good-recipe)
    * [Header Only](#header-only)
    * [CMake](#cmake)
      * [Components](#components)
    * [Autotools](#autotools)
      * [Components](#components-1)
    * [No Upstream Build Scripts](#no-upstream-build-scripts)
    * [System Packages](#system-packages)
    * [Verifying Dependency Version](#verifying-dependency-version)
    * [Verifying Dependency Options](#verifying-dependency-options)
  * [Test the recipe locally](#test-the-recipe-locally)
    * [Updating conan hooks on your machine](#updating-conan-hooks-on-your-machine)
  * [Debugging failed builds](#debugging-failed-builds)<!-- endToc -->

## Recipe files structure

Every entry in the `recipes` folder contains all the files required by Conan to create the binaries for all the versions of one library. Those
files don't depend on any other file in the repository (we are not using `python_requires`) and every pull-request can modify only one of those
folders at a time.

This is the canonical structure of one of these folders, where the same `conanfile.py` recipe is suitable to build all the versions of the library:

:information_source: For the updating the structure with the v2 migration [see here](../v2_migration.md#recipe-structure)

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

This file lists the versions and the folders where they are located (if there are more than a single `all` folder):

```yml
versions:
  "1.1.1":
    folder: 1.x.x
  "2.0.0":
    folder: all
  "2.1.0":
    folder: all
```

### Supported Versions

In this repository we are building a subset of all the versions for a given library. This set of version changes over time as new versions
are released and old ones stop being used.

We always welcome latest releases as soon as they are available, and from time to time we remove old versions mainly due to technical reasons:
the more versions we have, the more resources that are needed in the CI and the more time it takes to build each pull-request (also, the
more chances of failing because of unexpected errors).

### Removing old versions

When removing old versions, please follow these considerations:
 - keep one version for every major release
 - for the latest major release, at least three versions should be available (latest three minor versions)

The Conan Team may ask you to remove more if they are taking a lot of resources.

Logic associated to removed revisions, and entries in `config.yml` and `conandata.yml` files should be removed as well. If anyone needs to
recover them in the future, Git contains the full history and changes can be recovered from it.

Please, note that even if those versions are removed from this repository, **the packages will always be accessible in ConanCenter remote**
associated to the recipe revision used to build them.

### Adding old versions

We love to hear why in the opening description of the PR.
We usually don't add old versions unless there is a specific request for it.

Take into account that the version might be removed in future pull-requests according to the statements above.
Adding versions that are not used by consumer only requires more resources and time from the CI servers.

### `conandata.yml`

This file lists **all the sources that are needed to build the package**: source code, license files,... any file that will be used by the recipe
should be listed here. The file is organized into two sections, `sources` and `patches`, each one of them contains the files that are required
for each version of the library. All the files that are downloaded from the internet should include a checksum, so we can validate that
they are not changed.

> :information_source: Under our mission to ensure quality, patches undergo extra scrutiny. **Make sure to review** our [Modifying sources policy](policy_patching.md)

A detailed breakdown of all the fields can be found in [conandata_yml_format.md](conandata_yml_format.md). We strongly encourage adding the [patch fields](conandata_yml_format.md#patches-fields) to help track where patches come from and what issue they solve.

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

#### Sources

**Origin of sources:**

* Library sources should come from an official origin like the library source code repository or the official
release/download webpage.

* If an official source archive is available, it should be preferred over an auto-generated archive.

**Source immutability:** Downloaded source code stored under `source` folder should not be modified. Any patch should be applied to the copy of this source code when a build is executed (basically in `build()` method).

**Building from sources:** Recipes should always build packages from library sources.

**Sources not accessible:**

* Library sources that are not publicly available will not be allowed in this repository even if the license allows their redistribution.

* If library sources cannot be downloaded from their official origin or cannot be consumed directly due to their
  format, the recommendation is to contact the publisher and ask them to provide the sources in a way/format that can be consumed
  programmatically.

* In case of needing those binaries to use them as a "build require" for some library, we will consider following the approach of adding it
  as a system recipe (`<build_require>/system`) and making those binaries available in the CI machines (if the license allows it).


### The _recipe folder_: `conanfile.py`

The main files in this repository are the `conanfile.py` ones that contain the logic to build the libraries from sources for all the configurations,
as we said before there can be one single recipe suitable for all the versions inside the `all` folder, or there can be several recipes targetting
different versions in different folders. For maintenance reasons, we prefer to have only one recipe, but sometimes the extra effort doesn't worth
it and it makes sense to split and duplicate it, there is no common rule for it.

Together with the recipe, there can be other files that are needed to build the library: patches, other files related to build systems (many recipes
include a `CMakeLists.txt` to run some Conan logic before using the one from the library),... all these files will usually be listed in the
`exports_sources` attribute and used during the build process.

Also, **every `conanfile.py` should be accompanied by at least one folder to test the generated packages** as we will see below.

#### License Attribute

The mandatory license attribute of each recipe **should** be a [SPDX license](https://spdx.org/licenses/) [short Identifiers](https://spdx.dev/ids/) when applicable.

Where the SPDX guidelines do not apply, packages should do the following:

- When no license is provided or when it's given to the "public domain", the value should be set to [Unlicense](https://spdx.org/licenses/Unlicense) as per [KB-H056](error_knowledge_base.md#kb-h056-license-public-domain) and [FAQ](faqs.md#what-license-should-i-use-for-public-domain).
- When a custom (e.g. project specific) license is given, the value should be set to `LicenseRef-` as a prefix, followed by the name of the file which contains a custom license. See [this example](https://github.com/conan-io/conan-center-index/blob/e604534bbe0ef56bdb1f8513b83404eff02aebc8/recipes/fft/all/conanfile.py#L8). For more details, [read this conversation](https://github.com/conan-io/conan-center-index/pull/4928/files#r596216206)

#### Settings

All recipes should list the four settings `os`, `arch`, `compiler` and `build_type` so Conan will compute a different package ID
for each combination. There are some particular cases for this general rule:

* **Recipes for _header only_ libraries** might omit the `settings` attribute, but in any case they should add

   ```python
   def package_id(self):
      self.info.header_only()
   ```

* **Recipes that provide applications** (`b2`, `cmake`, `make`,...) that are generally used as a _build requires_, must list all
   the settings as well, but they should remove the `compiler` one in the corresponding method unless the recipe provides also
   libraries that are consumed by other packages:

   ```python
   def package_id(self):
      del self.info.settings.compiler
   ```

   Removing the `compiler` setting reduces the number of configurations generated by the CI, reducing the time and workload and, at the
   same time, demonstrates the power of Conan behind the package ID logic.

   > Note.- Intentionally, the `build_type` setting should not be removed from the package ID in this case. Preserving this
   > setting will ensure that the package ID for Debug and Release configurations will be different and both binaries can be
   > available in the Conan cache at the same time. This enable consumers to switch from one configuration to the other in the case
   > they want to run or to debug those executables.

## Options

Recipes can list any number of options with any meaning, and defaults are up to the recipe itself. The CI cannot enforce anything
in this direction.

### Recommended feature options names

It's often needed to add options to toggle specific library features on/off. Regardless of the default, there is a strong preference for using positive naming for options. In order to avoid the fragmentation, we recommend to use the following naming conventions for such options:

- enable_<feature> / disable_<feature>
- with_<dependency> / without_<dependency>
- use_<feature>

the actual recipe code then may look like:

```py
    options = {"use_tzdb": [True, False]}
    default_options = {"use_tzdb": True}
```

```py
    options = {"enable_locales": [True, False]}
    default_options = {"enable_locales": True}
```

```py
    options = {"with_zlib": [True, False]}
    default_options = {"with_zlib": True}
```

having the same naming conventions for the options may help consumers, e.g. they will be able to specify options with wildcards: `-o *:with_threads=True`, therefore, `with_threads` options will be enabled for all packages in the graph that support it.

### Known Options

However, there are a couple of options that have a special meaning for the CI:

* `fPIC` (with values `True` or `False`). Default should be `True`.

* `shared` (with values `True` or `False`). Default should be `False`. The CI inspects the recipe looking for this option. If it is found, it will
   generate all the configurations with values `shared=True` and `shared=False`.

   > Note.- The CI applies `shared=True` only to the package being built, while every other requirement will use their defaults
   > (typically `shared=False`). It's important to keep this in mind when trying to consume shared packages from ConanCenter
   > as their requirements were linked inside the shared library. See [FAQs](faqs.md#how-to-consume-a-graph-of-shared-libraries) for more information.

* `header_only` (with values `True` or `False`). Default should be `False`. If the CI detects this option, it will generate all the configurations for the
   value `header_only=False` and add one more configuration with `header_only=True`. **Only one
   package** will be generated for `header_only=True`, so it is crucial that the package is actually a _header only_ library, with header files only (no libraries or executables inside).

   Recipes with such option should include the following in their `package_id` method

   ```python
   def package_id(self):
      if self.options.header_only:
         self.info.header_only()
   ```

   ensuring that, when the option is active, the recipe ignores all the settings and only one package ID is generated.

* `build_testing` should not be added, nor any other related unit test option. Options affect the package ID, therefore, testing should not be part of that.
   Instead, use Conan config [skip_test](https://docs.conan.io/en/latest/reference/config_files/global_conf.html#tools-configurations) feature:

   ```python
   def _configure_cmake(self):
      cmake = CMake(self)
      cmake.definitions['BUILD_TESTING'] = not self.conf.get("tools.build:skip_test", default=true, check_type=bool)
   ```

   The `skip_test` configuration is supported by [CMake](https://docs.conan.io/en/latest/reference/build_helpers/cmake.html#test) and [Meson](https://docs.conan.io/en/latest/reference/build_helpers/meson.html#test).

### Dependencies

When a package needs other packages those are can be include with the `requirements()` methods.

```python
def requirements(self):
    self.require("fmt/8.1.1")
```

There are rules to follow:

* Version range is not allowed.
* Specify explicit RREV (recipe revision) of dependencies is not allowed.
* Only other conan-center recipes are allowed in `requires`/`requirements()` and `build_requires`/`build_requirements()` of a conan-center recipe.

#### Optional Requirements

If a requirement is conditional, this condition must not depend on build context. Build requirements don't have this constraint.
Add an option, see [naming recommendation](#recommended-feature-options-names), and set the default to make the upstream build system.

#### Requirements Options

Forcing options of dependencies inside a conan-center recipe should be avoided, except if it is mandatory for the library.
You need to use the `validate()` method in order to ensure they check after the Conan graph is completely built.

#### Handling "internal" dependencies

Vendoring in library source code should be removed (best effort) to avoid potential ODR violations. If upstream takes care to rename symbols, it may be acceptable.

### The test package folders: `test_package`

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

### Verifying Dependency Version

Some project requirements need to respect a version constraint. This can be enforced in a recipe by accessing the [`deps_cpp_info`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#deps-cpp-info) attribute.
An exaple of this can be found in the [spdlog recipe](https://github.com/conan-io/conan-center-index/blob/9618f31c4d9b4da5d06f905befe9691cf105a1fc/recipes/spdlog/all/conanfile.py#L92-L94).

```py
if tools.Version(self.deps_cpp_info["liba"].version) < "7":
    raise ConanInvalidConfiguration(f"The project {self.name}/{self.version} requires liba > 7.x")
```

In Conan version 1.x this needs to be done in the `build` method, in future release is should be done in the `validate` method.

### Verifying Dependency Options

Certain projects are dependant on the configuration (a.k.a options) of a dependency. This can be enforced in a recipe by accessing the [`options`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#options) attribute.
An example of this can be found in the [kealib recipe](https://github.com/conan-io/conan-center-index/blob/9618f31c4d9b4da5d06f905befe9691cf105a1fc/recipes/kealib/all/conanfile.py#L44-L46).

```py
    def validate(self):
        if not self.options["liba"].enable_feature:
            raise ConanInvalidConfiguration(f"The project {self.name}/{self.version} requires liba.enable_feature=True.")
```

## Test the recipe locally

The system will use the [conan-center hook](https://github.com/conan-io/hooks) to perform some quality checks. You can install the hook running:

```sh
conan config install https://github.com/conan-io/hooks.git -sf hooks -tf hooks
conan config set hooks.conan-center
```

The hook will show error messages but the `conan create` won’t fail unless you export the environment variable `CONAN_HOOK_ERROR_LEVEL=40`.
All hook checks will print a similar message:

```
[HOOK - conan-center.py] post_source(): [LIBCXX MANAGEMENT (KB-H011)] OK
[HOOK - conan-center.py] post_package(): ERROR: [PACKAGE LICENSE] No package licenses found
```

Call `conan create . lib/1.0@` in the folder of the recipe using the profile you want to test. For instance:

```sh
cd conan-center-index/recipes/boost/all
conan create conanfile.py boost/1.77.0@
```

### Updating conan hooks on your machine

The hooks are updated from time to time, so it's worth keeping your own copy of the hooks updated regularly. To do this:

```sh
conan config install
```

## Debugging failed builds

Go to the [Error Knowledge Base](error_knowledge_base.md) page to know more about Conan Center hook errors.

Some common errors related to Conan can be found on [troubleshooting](https://docs.conan.io/en/latest/faq/troubleshooting.html) section.

To test with the same enviroment, the [build images](supported_platforms_and_configurations.md#build-images) are available.
