project(PackageTest LANGUAGES CXX)
cmake_minimum_required(VERSION 3.10.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(SKIP_RPATH)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(GraylogLogger REQUIRED)
message(STATUS "Libraries: ${GraylogLogger_LIBRARIES}")

add_executable(example example.cpp)
target_link_libraries(example GraylogLogger::graylog_logger)
