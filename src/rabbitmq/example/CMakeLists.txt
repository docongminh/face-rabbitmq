cmake_minimum_required(VERSION 2.8)

project(face_rabbitmq)
file(GLOB_RECURSE SRC_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp
)#
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O2 -fPIC -std=c++11")
#
add_library(face_rabbitmq STATIC ${SRC_FILES})
#
include_directories(${CMAKE_SOURCE_DIR}/../../../3rdparty/amqpcpp/include)
link_directories(${CMAKE_SOURCE_DIR}/../../../3rdparty/amqpcpp/lib)
include_directories(${CMAKE_SOURCE_DIR}/../../../3rdparty/kashmir)
target_link_libraries(face_rabbitmq PUBLIC amqpcpp PocoNet PocoFoundation)

set(PROGS send_default
          receive_default
          send_direct
          receive_direct
)

foreach(item ${PROGS})
    add_executable(${item} "${item}.cpp")
    target_link_libraries(${item} PUBLIC face_rabbitmq)    
endforeach(item)
