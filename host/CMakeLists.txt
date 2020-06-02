cmake_minimum_required(VERSION 3.15)
project(host)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED on)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# Qt
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)
find_package(Qt5Core REQUIRED)
find_package(Qt5Widgets REQUIRED)
find_package(Qt5Quick REQUIRED)

file(GLOB INCLUDES
        src
        images
        qml
        )
include_directories(host PUBLIC ${INCLUDES})

file(GLOB SOURCES
        src/*.*
        qml/*.*
        images/*.*
        )
add_executable(host ${SOURCES})

target_link_libraries(host Qt5::Core Qt5::Widgets Qt5::Quick)
