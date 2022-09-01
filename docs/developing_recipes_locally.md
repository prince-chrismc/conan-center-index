# Developing Recipes Locally

One of the early steps for contributing get getting familiar with the Conan client. There's also a few steps you need to take to get your environment setup.

This file is intended to provide all the commands you need to run in order to be an expert ConanCenter contributor.

<!-- toc -->
## Contents

  * [Clone your fork](#clone-your-fork)
  * [Setup your environment](#setup-your-environment)
  * [Basic Commands](#basic-commands)
  * [Installing the ConanCenter Hooks](#installing-the-conancenter-hooks)
    * [Updating conan hooks on your machine](#updating-conan-hooks-on-your-machine)
  * [Debugging failed builds](#debugging-failed-builds)
  * [Testing more environments](#testing-more-environments)<!-- endToc -->

## Clone your fork

1. Follow the GitHub UI to [fork this repository](https://github.com/prince-chrismc/conan-center-index/fork)
2. [Clone your fork](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

## Setup your environment

1. Install a C++ development toolchain - ConanCenter's [build images](#testing-more-environments) are available
2. Install the Conan client - make sure to keep it up to date!
3. Install CMake - this is the only tool which is assumed to be present

## Basic Commands

We recommend working from the `recipes/project` folder itself, this is because you can only change one recipe per pull request, and will help prevent making most mistakes.

1. `conan create all/conanfile.py 0.0.0@`

ConanCenter also tests a few support settings/options, so `conan create all/conanfile.py 0.0.0@ -o project:shared=True -s build_type=Debug` is a easy way to more sure the package is correct.

Try it yourself, for instance:

```sh
cd recipes/fmt
conan create all/conanfile.py fmt/9.0.0@
conan create all/conanfile.py fmt/9.0.0@ -o fmt:header_only=True
conan create all/conanfile.py fmt/9.0.0@ -s build_type=Debug -o fmt:shared=True
```

## Installing the ConanCenter Hooks

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

### Updating conan hooks on your machine

The hooks are updated from time to time, so it's worth keeping your own copy of the hooks updated regularly. To do this:

```sh
conan config install
```

## Debugging failed builds

Go to the [Error Knowledge Base](../error_knowledge_base.md) page to know more about Conan Center hook errors.
Some common errors related to Conan can be found on [troubleshooting](https://docs.conan.io/en/latest/faq/troubleshooting.html) section.

To test with the same environment, the [build images](../supported_platforms_and_configurations.md#build-images) are available.

## Running the Python Linters

There are several variation of python linters, which were introduced to help with Conan 2.0 migration, these product comments on pull requests.

You can test your code before hand by running:

```sh
export PYTHONPATH=$(pwd)
pylint --rcfile=linter/pylintrc_recipe recipes/fmt/all/conanfile.py
```

## Testing the different `test_*_package`

This can be done by running:

```sh
conan test recipes/fmt/all/test_v1_package/conanfile.py fmt/9.0.0@
```

## Testing more environments

This can be difficult for some platforms given virtualization support.

For Windows and MacOS users, you can test the Linux build environments by with the the Docker build images.

Assuming you've already tested it locally, and it's successfully export to your cache, you can:

1. Creating a new profile.
2. Build missing packages

Example.

```
docker run -v/Users/barbarian/.conan:/home/conan/.conan conanio/gcc8 bash -c "conan profile new --detect gcc8"
docker run -v/Users/barbarian/.conan:/home/conan/.conan conanio/gcc8 bash -c "conan install -pr gcc8 fmt/9.0.0@ --build missing"
```
