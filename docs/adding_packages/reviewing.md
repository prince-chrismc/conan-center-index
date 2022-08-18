# Reviewing policies

The following policies are preferred during the review, but not mandatory:

<!-- toc -->
## Contents

  * [Trailing white-spaces](#trailing-white-spaces)
  * [Quotes](#quotes)
  * [Subfolder Properties](#subfolder-properties)
  * [Order of methods and attributes](#order-of-methods-and-attributes)
  * [License Attribute](#license-attribute)
  * [Exporting Patches](#exporting-patches)
  * [Applying Patches](#applying-patches)
  * [CMake](#cmake)
    * [Caching Helper](#caching-helper)
    * [Build Folder](#build-folder)
    * [CMake Configure Method](#cmake-configure-method)
  * [Test Package](#test-package)
    * [Minimalistic Source Code](#minimalistic-source-code)
    * [CMake targets](#cmake-targets)
  * [Recommended feature options names](#recommended-feature-options-names)
  * [Supported Versions](#supported-versions)
    * [Removing old versions](#removing-old-versions)
    * [Adding old versions](#adding-old-versions)<!-- endToc -->

## Trailing white-spaces

Avoid trailing white-space characters, if possible

## Quotes

If possible, try to avoid mixing single quotes (`'`) and double quotes (`"`) in python code (`conanfile.py`, `test_package/conanfile.py`). Consistency is preferred.

## Subfolder Properties

When extracting sources or performing out-of-source builds, it is preferable to use a _subfolder_ attribute, `_source_subfolder` and `_build_subfolder` respectively.

For example doing this with property attributes for these variables:

```py
@property
def _source_subfolder(self):
    return "source_subfolder"

@property
def _build_subfolder(self):
    return "build_subfolder"
```

## Order of methods and attributes

Prefer the following order of documented methods in python code (`conanfile.py`, `test_package/conanfile.py`):

- init
- set_name
- set_version
- export
- export_sources
- config_options
- configure
- layout
- requirements
- package_id
- validate
- build_id
- build_requirements
- system_requirements
- source
- generate
- imports
- build
- package
- package_info
- deploy
- test

the order above resembles the execution order of methods on CI. therefore, for instance, `build` is always executed before `package` method, so `build` should appear before the
`package` in `conanfile.py`.

## CMake

When working with CMake based upstream projects it is prefered to follow these principals. They are not applicable to all projects so they can not be enforced.

### Caching Helper

Due to build times and the lenght to configure CMake multiple times, there is a strong motivation to cache the `CMake` build helper from Conan between the `build()` and `package()` methods.

This can be done by adding a `_cmake` attribute to the `ConanFile` class, but consider it as outdated. The current option is using `@functools.lru_cache(1)` decorator.
As example, take a look on [miniz](https://github.com/conan-io/conan-center-index/blob/16780f87ad3db3be81323ddafc668145e4348513/recipes/miniz/all/conanfile.py#L57) recipe.

### Build Folder

Ideally use out-of-source builds by calling `cmake.configure(build_folder=self._build_subfolder)` when ever possible.

### CMake Configure Method

Use a seperate method to handle the common patterns with using CMake based projects. This method is `_configure_cmake` and looks like the follow in the most basic cases:

```py
@functools.lru_cache(1)
def _configure_cmake(self):
    cmake = CMake(self)
    cmake.definitions["BUILD_STATIC"] = not self.options.shared
    cmake.configure(build_folder=self._build_subfolder)
    return cmake
```
