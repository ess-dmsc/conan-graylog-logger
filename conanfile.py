import os
from conans import ConanFile, CMake, tools

class GraylogloggerConan(ConanFile):
    name = "graylog-logger"
    version_number = "2.1.4"
    version = f"{version_number}-1"
    license = "BSD 2-Clause"
    url = "https://bintray.com/ess-dmsc/graylog-logger"
    build_requires = ("gtest/1.11.0",)
    requires = ("nlohmann_json/3.10.5", "asio/1.22.1", "concurrentqueue/1.0.3", "fmt/8.1.1")
    settings = "os", "compiler", "build_type", "arch"
    generators = ("cmake_find_package")
    description = "A simple logging library with support for pushing messages to a graylog-logger service."
    
    def source(self):
        self.run("git clone https://github.com/ess-dmsc/graylog-logger.git")
        self.run(f"cd graylog-logger && git checkout v{self.version_number}")
        
    def _configure_cmake(self):
        cmake = CMake(self, parallel=True)

        cmake.definitions["BUILD_EVERYTHING"] = "OFF"
        cmake.definitions["CONAN"] = "DISABLE"
        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_MACOSX_RPATH"] = "ON"
            cmake.definitions["CMAKE_SHARED_LINKER_FLAGS"] = "-headerpad_max_install_names"
        cmake.configure(source_dir=self.name, build_dir=".")
        return cmake
        
    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        cmake.build(target="unit_tests")
        self.run("unit_tests/unit_tests --gtest_filter=-'*IPv6*:*AddConsoleHandlerTest*'")

        if tools.os_info.is_macos:
            os.system("install_name_tool -id '@rpath/libgraylog_logger.dylib' "
                      "graylog_logger/libgraylog_logger.dylib")

        os.rename(
            "graylog-logger/LICENSE.md",
            "graylog-logger/LICENSE.graylog-logger"
        )

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.*", src="graylog-logger")

    def package_info(self):
        self.cpp_info.libs = ["graylog_logger"]
