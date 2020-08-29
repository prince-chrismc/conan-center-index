cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(safe_c_stub INTERFACE)
# "source_subfolder/safe_c_stub/src/safe_mem_stub.c")
#                        "source_subfolder/safe_c_stub/src/safe_str_stub.c")
target_include_directories(safe_c_stub INTERFACE "source_subfolder/safe_c_stub/include")
target_compile_definitions(safe_c_stub INTERFACE WIN32, HAVE_STDINT, LIBEST_EXPORTS=1, DISABLE_BACKTRACE, __STDC_WANT_SECURE_LIB__, DISABLE_PTHREADS=1, __SAFE_LIB_H__, PACKAGE_STRING=libest-3.2.0)

file(GLOB EST_C_SOURCES "source_subfolder/src/est/*.c")
file(GLOB EST_H_SOURCES "source_subfolder/src/est/*.h")

add_library(est ${EST_H_SOURCES} ${EST_C_SOURCES})
target_link_libraries(est PUBLIC safe_c_stub ${CONAN_LIBS})
