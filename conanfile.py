import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanException


class GraylogloggerConan(ConanFile):
    name = "graylog-logger"
    version = "<version>"
    license = "BSD 2-Clause"
    url = "https://bintray.com/ess-dmsc/graylog-logger"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "virtualrunenv"

    def source(self):
        self.run("git clone https://github.com/ess-dmsc/graylog-logger.git")
        self.run("cd graylog-logger && git checkout <commit>")

    def build(self):
        cmake = CMake(self)

        try:
            self.output.info("Try to run cmake3")
            self.run("cmake3 --version")
            cmake_command = "cmake3"
        except ConanException:
            self.output.info("Using cmake instead of cmake3")
            cmake_command = "cmake"

        cmake.definitions["BUILD_EVERYTHING"] = "OFF"
        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_MACOSX_RPATH"] = "ON"
            cmake.definitions["CMAKE_SHARED_LINKER_FLAGS"] = "-headerpad_max_install_names"

        self.run('%s graylog-logger %s' % (cmake_command, cmake.command_line))
        self.run("%s --build . %s" % (cmake_command, cmake.build_config))

        if tools.os_info.is_macos:
            os.system("install_name_tool -id '@rpath/libgraylog_logger.dylib' "
                      "graylog_logger/libgraylog_logger.dylib")

        os.rename(
            "graylog-logger/LICENSE.md",
            "graylog-logger/LICENSE.graylog-logger"
        )

    def package(self):
        self.copy("*.h", dst="include/graylog_logger", src="graylog-logger/include/graylog_logger")
        self.copy("*.hpp", dst="include/graylog_logger", src="graylog-logger/include/graylog_logger")
        if self.settings.os == "Macos":
            self.copy("*.dylib", dst="lib", src="graylog_logger", keep_path=False)
        else:
            self.copy("*.so", dst="lib", src="graylog_logger", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("console_logger", dst="bin", src="console_logger", keep_path=False)
        self.copy("LICENSE.*", src="graylog-logger")

    def package_info(self):
        self.cpp_info.libs = ["graylog_logger"]
