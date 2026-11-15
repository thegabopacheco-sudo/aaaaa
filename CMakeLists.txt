cmake_minimum_required(VERSION 3.20)
project(fivem_cheat)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (WIN32)
    add_compile_definitions(WIN32_LEAN_AND_MEAN NOMINMAX)
    add_compile_options(/W4 /permissive-)
endif()

set(IMGUI_DIR ${CMAKE_CURRENT_SOURCE_DIR}/external/imgui)

if (NOT EXISTS "${IMGUI_DIR}/imgui.cpp")
    message(FATAL_ERROR "ImGui no encontrado en ${IMGUI_DIR}. Clona el repo primero.")
endif()

add_library(imgui STATIC
    ${IMGUI_DIR}/imgui.cpp
    ${IMGUI_DIR}/imgui_draw.cpp
    ${IMGUI_DIR}/imgui_tables.cpp
    ${IMGUI_DIR}/imgui_widgets.cpp
    ${IMGUI_DIR}/backends/imgui_impl_win32.cpp
    ${IMGUI_DIR}/backends/imgui_impl_dx11.cpp
)
target_include_directories(imgui PUBLIC ${IMGUI_DIR} ${IMGUI_DIR}/backends)
target_link_libraries(imgui PUBLIC d3d11 dxgi)

set(SOURCES
    src/dll/dllmain.cpp
    src/dll/hook.cpp
    src/dll/common.cpp
)
set(HEADERS
    src/dll/hook.h
    src/dll/common.h
)

add_library(fivem_cheat SHARED ${SOURCES} ${HEADERS})
target_link_libraries(fivem_cheat PRIVATE imgui d3d11 dxgi user32 gdi32)
set_target_properties(fivem_cheat PROPERTIES
    PREFIX ""
    OUTPUT_NAME "fivem_cheat"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIG>"
)

add_executable(injector src/injector/main.cpp)
target_link_libraries(injector PRIVATE user32)
set_target_properties(injector PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIG>"
)