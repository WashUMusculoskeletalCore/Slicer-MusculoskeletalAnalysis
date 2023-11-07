#-----------------------------------------------------------------------------
set(PYTHON_TOOLS
  MusculoskeletalAnalysisCLITools/__init__.py
  MusculoskeletalAnalysisCLITools/crop.py
  MusculoskeletalAnalysisCLITools/density.py
  MusculoskeletalAnalysisCLITools/fill.py
  MusculoskeletalAnalysisCLITools/largestCC.py
  MusculoskeletalAnalysisCLITools/reader.py
  MusculoskeletalAnalysisCLITools/shape.py
  MusculoskeletalAnalysisCLITools/thickness.py
  MusculoskeletalAnalysisCLITools/writeReport.py
  )

set(binary_dir "${CMAKE_BINARY_DIR}/${Slicer_CLIMODULES_BIN_DIR}")

if(CMAKE_CONFIGURATION_TYPES)
  if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.20")
    set(binary_dir "${binary_dir}/$<CONFIG>")
   else()
    set(binary_dir "${binary_dir}/${CMAKE_CFG_INTDIR}")
  endif()
endif()

set(MODULE_NAME MusculoskeletalAnalysisCLITools)

ctkMacroCompilePythonScript(
    TARGET_NAME ${MODULE_NAME}
    SCRIPTS ${PYTHON_TOOLS}
    DESTINATION_DIR ${binary_dir}
    INSTALL_DIR ${Slicer_INSTALL_CLIMODULES_BIN_DIR}
    NO_INSTALL_SUBDIR
    )

add_subdirectory(CancellousAnalysis)
add_subdirectory(CorticalAnalysis)
add_subdirectory(DensityAnalysis)
