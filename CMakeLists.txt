#1.cmake verson
cmake_minimum_required(VERSION 2.8)

#2.project name
project(FaceService)

# Support parallel
Option(USE_OPENMP "openmp support" ON)

file(GLOB_RECURSE SRC_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
)

message(${SRC_FILES})

# list(APPEND SRCS ${LAYER_ARCH_SRC})
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O2 -fPIC -std=c++11 -fopenmp")
add_library(FaceService STATIC ${SRC_FILES})

find_package(OpenCV)
message("Opencv Version: ${OPENCV_VERSION}" )
include_directories(${CMAKE_SOURCE_DIR}/3rdparty/ncnn/include/ncnn)
link_directories(${CMAKE_SOURCE_DIR}/3rdparty/ncnn/lib)
include_directories(${CMAKE_SOURCE_DIR}/3rdparty/amqpcpp/include)
link_directories(${CMAKE_SOURCE_DIR}/3rdparty/amqpcpp/lib)
include_directories(${CMAKE_SOURCE_DIR}/3rdparty/kashmir)
include_directories(${CMAKE_SOURCE_DIR}/3rdparty/json)
target_link_libraries(FaceService PUBLIC ${OpenCV_LIBS} ncnn amqpcpp PocoNet PocoFoundation)
#
find_package(OpenMP)
# if(NOT TARGET OpenMP::OpenMP_CXX AND (OpenMP_CXX_FOUND OR OPENMP_FOUND))
#     target_compile_options(FaceService PRIVATE ${OpenMP_CXX_FLAGS})
# endif()

if(USE_OPENMP AND OpenMP_CXX_FOUND)
    message("Building with OpenMP")
    target_link_libraries(FaceService PUBLIC OpenMP::OpenMP_CXX)
endif()

#
target_include_directories(FaceService
    PUBLIC
        # include for detect face
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/common>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/detection>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/detection/detect_face/retinaface>
        # -------------------include align and detect keypoint face---------------------
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/detection/alignment>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/detection/landmark/insightface>
        # -------------------include extract feature---------------------
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/extraction>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/extraction/mobilefacenet>
        # -------------------include rabbitmq---------------------
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/rabbitmq>
)
#
add_executable(detect_worker ${CMAKE_SOURCE_DIR}/src/detect_worker.cpp)
add_executable(extract_worker ${CMAKE_SOURCE_DIR}/src/extract_worker.cpp)
# add_executable(test ${CMAKE_SOURCE_DIR}/src/test.cpp)

# 
target_link_libraries(detect_worker PUBLIC FaceService)
target_link_libraries(extract_worker PUBLIC FaceService)
# target_link_libraries(test PUBLIC FaceService)
# target_link_libraries(detect PUBLIC FaceService)
# target_link_libraries(align PUBLIC FaceService)