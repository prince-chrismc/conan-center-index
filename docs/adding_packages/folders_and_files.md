# Adding Packages to ConanCenter

First thing is know what library you want to add. Conan packages are always lowercase.
Take note of the license and URL for the project, to fill in the `conanfile.py` attributes later.

<!-- toc -->
## Contents

  * [Styling Guidelines](#styling-guidelines)
    * [Trailing Whitespace](#trailing-whitespace)
    * [Quotes](#quotes)
  * [Recipe File Structure](#recipe-file-structure)
    * [`config.yml`](#configyml)
    * [The _recipe folder_](#the-_recipe-folder_)
      * [`conandata.yml`](#conandatayml)
      * [`conanfile.py`](#conanfilepy)
        * [Dependencies](#dependencies)
      * [The test package folders: `test_package`](#the-test-package-folders-test_package)<!-- endToc -->

## Styling Guidelines

There are many conventions in ConanCenter, a few of them are outline below. They are always to make maintaining the large number of recipes easier for everyone.

### Trailing Whitespace

Avoid trailing white-space characters, if possible

### Quotes

If possible, try to avoid mixing single quotes (`'`) and double quotes (`"`) in python code (`conanfile.py`, `test_package/conanfile.py`). Consistency is preferred.

## Recipe File Structure

Every entry in the `recipes` folder contains all the files required by Conan to create the binaries for all the versions of one library. Those
files don't depend on any other file in the repository (we are not using `python_requires`) and every pull-request can modify only one of those
folders at a time.

This is the canonical structure of one of these folders, where the same `conanfile.py` recipe is suitable to build all the versions of the library:

> :information_source: For updating the structure during the v2 migration see the [test package](test_package.md) document.

```
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- conanfile.py
|           +-- conandata.yml
|           +-- patches/
|               +-- add-missing-string-header-2.1.0.patch
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

### The _recipe folder_

This contains every needed to build packages.

#### `conandata.yml`

This file lists **all the sources that are needed to build the package**: source code, license files,... any file that will be used by the recipe
should be listed here. The file is organized into two sections, `sources` and `patches`, each one of them contains the files that are required
for each version of the library. All the files that are downloaded from the internet should include a checksum, so we can validate that
they are not changed.

```yml
sources:
  "9.0.0":
    url: "https://github.com/fmtlib/fmt/archive/9.0.0.tar.gz"
    sha256: "9a1e0e9e843a356d65c7604e2c8bf9402b50fe294c355de0095ebd42fb9bd2c5"
```

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
```

See the [Export Patches](sources_and_patches.md#exporting-patches) and [Applying Patches](sources_and_patches.md#applying-patches)
for more use case and examples.

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

> **Note** It's encouraged to verify old generator are not broken for - you can do so by using the pattern
> `test_v1_*/conanfile.py` for the folder. Please, have a look to [linter notes](v2_linter.md) to know how to prevent the linter from
> checking these files.

Remember that the `test_<package>` recipes should **test the package configuration that has just been generated** for the _host_ context, otherwise
it will fail in cross-building scenarios.
