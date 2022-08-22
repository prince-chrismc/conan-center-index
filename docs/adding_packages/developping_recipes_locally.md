# Developing Recipes Locally

One of the early steps for contributing get getting familiar with the Conan client. There's also a few steps you need to take to get your environment setup.

<!-- toc -->
## Contents<!-- endToc -->

## Basic Commands

We recommend working from the `recipes/project` folder itself, this is because you can only change one recipe per pull request, and will help prevent making most mistakes.

1. `conan create all/conanfile.py 0.0.0@`

ConanCenter also tests a few support settings/options, so `conan create all/conanfile.py 0.0.0@ -o project:shared=True -s build_type=Debug` is a easy way to more sure the package is correct.

Try it yourself, for instance:

```sh
cd conan-center-index/recipes/fmt
conan create all/conanfile.py boost/9.0.0@
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

Go to the [Error Knowledge Base](error_knowledge_base.md) page to know more about Conan Center hook errors.

Some common errors related to Conan can be found on [troubleshooting](https://docs.conan.io/en/latest/faq/troubleshooting.html) section.

To test with the same environment, the [build images](supported_platforms_and_configurations.md#build-images) are available.

## Testing more environments

This can be difficult for some platforms given virtualization support.

For Windows and MacOS users, you can test the Linux build environments by with the the Docker build images.

Assuming you've already tested it locally, and it's successfully export to your cache, you can:

1. Creating a new profile.
2. Build missing packages

Example.

```
docker run -v/Users/barbarian/.conan:/home/conan/.conan conanio/gcc8 bash -c "conan profile new --detect gcc8"
docker run -v/Users/barbarian/.conan:/home/conan/.conan conanio/gcc8 bash -c "conan install -pr gcc8 tensorflow-lite/2.9.1@ --build missing"
```
