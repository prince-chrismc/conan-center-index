# Adding Packages to ConanCenter

ConanCenter aims to provide the best quality packages open for any open source project.
Any C/C++ project can be made available.

Getting started is easy.

<!-- toc -->
## Contents<!-- endToc -->

## Request access

:one: The first step to add packages to ConanCenter is requesting access. To enroll in ConanCenter repository, please write a comment
requesting access in this GitHub [issue](https://github.com/conan-io/conan-center-index/issues/4). Feel free to introduce yourself and
your motivation to join ConanCenter community.

This process helps conan-center-index against spam and malicious code. The process is not not automated on purpose and the requests are generally approved on a weekly basis.

> :warning: The requests are reviewed manually, checking the GitHub profile activity of the requester to avoid a misuse of the service. All interactions are subject to the expectations of the [code of conduct](../code_of_conduct.md). In case of detecting a misuse or inappropriate behavior, the requester will be dropped from the authorized users list and at last instance even banned from the repository.

## Creating a package

The easiest way is to copy an existing recipe that was recently updated. Pick one that uses the same build system to keep things easy.

- Rename the folder and recipe - names are always lowercase
- Add _only_ the latest version in the `config.yml` and `conandata.yml`
- Make sure to update the `ConanFile` attributes like `license`, `description`, ect...

In ConanCenter, our belief is recipes should always match upstream, in other words, what the original author(s) intended.

- Options should follow our recommendations as well as match the default of upstream.
- Package information, libraries, components should match as well. This include supported build system names.

Where dependencies are involved, there's no shortcuts, inspect the upstream's build scripts for how they usually consume them. Pick the Conan generator that matches.
The most common example is CMake's `find_package` can be satisfied by Conan's `CMakeDeps` generator. There are a few things to be cautious about, many projects
like to "vendor" other projects within them. This can be files checked into the repository or downloaded during the build process.

## Submitting a Package

:two: To contribute a package, you can submit a [Pull Request](https://github.com/conan-io/conan-center-index/pulls) to this GitHub repository https://github.com/conan-io/conan-center-index.

The specific steps to submitting changes are:

* Fork the [conan-center-index](https://github.com/conan-io/conan-center-index/fork) git repository, and then clone it locally.
* Make sure you are using the latest [Conan client](https://conan.io/downloads) version, as recipes might evolve introducing features of the newer Conan releases.
* Build and test the new recipe in several combinations
* Commit and push to GitHub then submit a pull request.
* Our automated [build service](#the-build-service) will build 100+ different configurations, and provide messages that indicate if there were any issues found during the pull request on GitHub.

:three: When the pull request is [reviewed and merged](../review_process.md), those packages are published to [JFrog ConanCenter](https://conan.io/center/) and available for everyone.

## The Build Service

The **build service** associated to this repo will generate binary packages automatically for the most common platforms and compilers. See [the Supported Platforms and Configurations page](../supported_platforms_and_configurations.md) for a list of generated configurations. For a C++ library, the system is currently generating more than 100 binary packages.

> ⚠️ **Note**: This not a testing service, it is a binary building service for package **released**. Unit tests shouldn't be built nor run in recipes by default, see the [FAQs](../faqs.md#why-conancenter-does-not-build-and-execute-tests-in-recipes) for more. Before submitting a pull request, please ensure that it works locally for some configurations.

- The CI bot will start a new build only [after the author is approved](#request-access). Your PR may be reviewed in the mean time, but is not guaranteed.
- The CI system will also report with messages in the PR any error in the process, even linking to the logs to see more details and debug.
- The Actions are used to lint and ensure the latest conventions are being used. You'll see comments from bots letting you know.

The pipeline will report errors and build logs by creating a comment in the pull-request after every commit. The message will include links to the logs for inspecting.

Packages generated and uploaded by this build service does not include any _user_ or _channel_ (existing references with any `@user/channel` should be considered as deprecated in favor of packages without it). Once the packages are uploaded, you will be able to install them using the reference as `name/version` (requires Conan >= 1.21): `conan install cmake/3.18.2@`.
