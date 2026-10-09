cmake_minimum_required(VERSION 3.16)
project(segmentacao_textura_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(OpenCV REQUIRED COMPONENTS core imgcodecs imgproc)

add_executable(segmentacao_textura segmentacao_textura.cpp)
target_link_libraries(segmentacao_textura PRIVATE ${OpenCV_LIBS})
target_include_directories(segmentacao_textura PRIVATE ${OpenCV_INCLUDE_DIRS})