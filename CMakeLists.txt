cmake_minimum_required(VERSION 3.25)
project(pinstripe-style VERSION 0.1.0)

# Pinstripe: an Aqua (Mac OS X 10.2 "Jaguar") inspired widget style for Qt 6 / KDE Plasma,
# with a matching colour scheme and Plasma style.

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(ECM 6.0 REQUIRED NO_MODULE)
set(CMAKE_MODULE_PATH ${ECM_MODULE_PATH})
include(KDEInstallDirs6)
include(KDECMakeSettings)
include(KDECompilerSettings NO_POLICY_SCOPE)

find_package(Qt6 6.8 REQUIRED COMPONENTS Core Gui Widgets)
find_package(KF6WindowSystem REQUIRED) # KWindowShadow: drop shadows for menus and help tags

add_subdirectory(style)

install(FILES colors/Pinstripe.colors colors/PinstripeGraphite.colors DESTINATION ${KDE_INSTALL_DATADIR}/color-schemes)
install(DIRECTORY plasma/pinstripe DESTINATION ${KDE_INSTALL_DATADIR}/plasma/desktoptheme OPTIONAL)
install(DIRECTORY gtk/Pinstripe DESTINATION ${KDE_INSTALL_DATADIR}/themes OPTIONAL)
install(DIRECTORY icons/Oxygen-Pinstripe DESTINATION ${KDE_INSTALL_DATADIR}/icons OPTIONAL)

option(BUILD_GALLERY "Build the offscreen widget gallery renderer (tools/gallery)" OFF)
if(BUILD_GALLERY)
    find_package(KF6ColorScheme REQUIRED)
    find_package(KF6Config REQUIRED)
    add_subdirectory(tools/gallery)
endif()
