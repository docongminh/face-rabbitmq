#1.cmake verson
cmake_minimum_required(VERSION 2.8)

#2.project name
project(FaceService)

# Support parallel
Option(USE_OPENMP "openmp support" ON)

file(GLOB_RECURSE SRC_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp
)

message(${SRC_FILES})

# list(APPEND SRCS ${LAYER_ARCH_SRC})
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O2 -fPIC -std=c++11 -fopenmp")
add_library(FaceService STATIC ${SRC_FILES})

find_package(OpenCV)
message("Opencv Version: ${OPENCV_VERSION}" )
include_directories(${CMAKE_SOURCE_DIR}/ncnn/include/ncnn)
link_directories(${CMAKE_SOURCE_DIR}/ncnn/lib)
target_link_libraries(FaceService PUBLIC ${OpenCV_LIBS} ncnn)
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
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/utils>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/detection>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/detection/detect_face/retinaface>
        # -------------------include align and detect keypoint face---------------------
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/detection/alignment>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/detection/landmark/insightface>
        # -------------------include extract feature---------------------
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/extraction>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/extraction/mobilefacenet>
)
#
# add_executable(main ${CMAKE_SOURCE_DIR}/src/main.cpp)
add_executable(similarity ${CMAKE_SOURCE_DIR}/src/test_similarity.cpp)
# add_executable(detect ${CMAKE_SOURCE_DIR}/src/test_detect.cpp)
# add_executable(align ${CMAKE_SOURCE_DIR}/src/test_alignment.cpp)
# 
# target_link_libraries(main PUBLIC FaceService)
target_link_libraries(similarity PUBLIC FaceService)
# target_link_libraries(detect PUBLIC FaceService)
# target_link_libraries(align PUBLIC FaceService)
