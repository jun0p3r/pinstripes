add_library(pinstripe MODULE pinstripeplugin.cpp pinstripestyle.cpp gel.cpp)
target_link_libraries(pinstripe PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)
install(TARGETS pinstripe DESTINATION ${KDE_INSTALL_QTPLUGINDIR}/styles)
install(FILES pinstripe.themerc pinstripegraphite.themerc DESTINATION ${KDE_INSTALL_DATADIR}/kstyle/themes)
# keep the built plugin under bin/styles so QT_PLUGIN_PATH=build/bin finds it
set_target_properties(pinstripe PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/styles)
