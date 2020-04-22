import os
import glob
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration, ConanException

class JsonSchemaValidatorConan(ConanFile):
    name = "json-schema-validator"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pboettch/json-schema-validator"
    description = "JSON schema validator for JSON for Modern C++ "
    topics = ("json-schema-validator", "modern-json",
              "schema-validation", "json")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        compiler_version = Version(self.settings.compiler.version)
        if self.settings.os == "Windows"and self.settings.compiler == "Visual Studio" and compiler_version < "16":
            try:
                # Force check to ensure compatability
                tools.check_min_cppstd(self, "17") # There's an issue in upstream forcing a higher cppstd version. See https://github.com/pboettch/json-schema-validator/issues/106
            except ConanInvalidConfiguration:
                raise
            except ConanException:
                self.output.warn("Unnable to determine the default standard version of the compiler")
        elif self.settings.compiler == "clang" and compiler_version < "4":
            try:
                # Force check to ensure compatability
                tools.check_min_cppstd(self, "11") # Clang 3.9 requires this to be set to ignore the issue above https://releases.llvm.org/3.9.1/tools/clang/docs/ReleaseNotes.html#c-1z-feature-support
            except ConanInvalidConfiguration:
                raise
            except ConanException:
                self.output.warn("Unnable to determine the default standard version of the compiler")
        elif self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def requirements(self):
        self.requires("nlohmann_json/3.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "nlohmann_json_schema_validator"
        self.cpp_info.names["cmake_find_package_multi"] = "nlohmann_json_schema_validator"
