# Handling Dependencies

<!-- toc -->
## Contents

  * [Rules and Recommendations](#rules-and-recommendations)
    * [Optional Requirements](#optional-requirements)
    * [Requirements Options](#requirements-options)
        * [Handling "internal" dependencies](#handling-internal-dependencies)
    * [Verifying Dependency Version](#verifying-dependency-version)<!-- endToc -->

## Rules and Recommendations

There are rules to follow:

* Version range is not allowed.
* Specify explicit RREV (recipe revision) of dependencies is not allowed.
* Only other conan-center recipes are allowed in `requires`/`requirements()` and `build_requires`/`build_requirements()` of a conan-center recipe.

### Optional Requirements

If a requirement is conditional, this condition must not depend on build context. Build requirements don't have this constraint.
Add an option, see [naming recommendation](conanfile_attributes.md#recommended-names), and set the default to make the upstream build system.

```py
class ExampleConan(ConanFile):
    options = {
        # ...
        "with_zlib": [True, False],
    }
    default_options = {
        # ...
        "with_zlib": True,
    }

    def requirements(self):
        # ...
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
```

### Requirements Options

Forcing options of dependencies inside a ConanCenter should be avoided, except if it is mandatory for the library.
You need to use the `validate()` method in order to ensure they check after the Conan graph is completely built.

Certain projects are dependant on the configuration (a.k.a options) of a dependency. This can be enforced in a recipe by accessing the [`options`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#options) attribute.
An example of this can be found in the [kealib recipe](https://github.com/conan-io/conan-center-index/blob/9618f31c4d9b4da5d06f905befe9691cf105a1fc/recipes/kealib/all/conanfile.py#L44-L46).

```py
    def validate(self):
        if not self.options["liba"].enable_feature:
            raise ConanInvalidConfiguration(f"The project {self.name}/{self.version} requires liba.enable_feature=True.")
```

##### Handling "internal" dependencies

Vendoring in library source code should be removed (best effort) to avoid potential ODR violations. If upstream takes care to rename symbols, it may be acceptable.

### Verifying Dependency Version

Some project requirements need to respect a version constraint. This can be enforced in a recipe by accessing the [`deps_cpp_info`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#deps-cpp-info) attribute.
An exaple of this can be found in the [spdlog recipe](https://github.com/conan-io/conan-center-index/blob/9618f31c4d9b4da5d06f905befe9691cf105a1fc/recipes/spdlog/all/conanfile.py#L92-L94).

```py
if tools.Version(self.deps_cpp_info["liba"].version) < "7":
    raise ConanInvalidConfiguration(f"The project {self.name}/{self.version} requires liba > 7.x")
```

In Conan version 1.x this needs to be done in the `build` method, in future release is should be done in the `validate` method.
