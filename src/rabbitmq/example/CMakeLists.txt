cmake_minimum_required(VERSION 2.8)

project(rabbitmq_example)
file(GLOB_RECURSE SRC_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp
)#
add_library(rabbitmq_example STATIC ${SRC_FILES})
target_link_libraries(rabbitmq_example PUBLIC amqpcpp PocoNet PocoFoundation)

set(PROGS send_default
          receive_default
          send_direct
          receive_direct
)

foreach(item ${PROGS})
    add_executable(${item} "${item}.cpp")
    target_link_libraries(${item} PUBLIC rabbitmq_example)    
endforeach(item)
