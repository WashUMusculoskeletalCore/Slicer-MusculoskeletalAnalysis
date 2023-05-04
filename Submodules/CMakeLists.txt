#-----------------------------------------------------------------------------
set(PYTHON_TOOLS
  tools/__init__.py
  tools/fill.py
  tools/thickness.py
  tools/writeReport.py
  tools/reader.py
  tools/crop.py
  tools/largestCC.py
  tools/shape.py
  )

set(binary_dir "${CMAKE_BINARY_DIR}/${Slicer_CLIMODULES_BIN_DIR}")

if(CMAKE_CONFIGURATION_TYPES)
  if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.20")
    set(binary_dir "${binary_dir}/$<CONFIG>")
   else()
    set(binary_dir "${binary_dir}/${CMAKE_CFG_INTDIR}")
  endif()
endif()

set(MODULE_NAME Tools)

ctkMacroCompilePythonScript(
    TARGET_NAME ${MODULE_NAME}
    SCRIPTS ${PYTHON_TOOLS}
    DESTINATION_DIR ${binary_dir}
    INSTALL_DIR ${Slicer_INSTALL_CLIMODULES_BIN_DIR}
    NO_INSTALL_SUBDIR
    )

set(MODULE_NAME CorticalAnalysis)

SlicerMacroBuildScriptedCLI(
  NAME ${MODULE_NAME}
  )

set(MODULE_NAME CancellousAnalysis)

SlicerMacroBuildScriptedCLI(
  NAME ${MODULE_NAME}
  )

set(MODULE_NAME DensityAnalysis)

SlicerMacroBuildScriptedCLI(
  NAME ${MODULE_NAME}
  )