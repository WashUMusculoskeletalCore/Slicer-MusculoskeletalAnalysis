cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(MusculoskeletalAnalysis)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis")
set(EXTENSION_CATEGORY "Analysis")
set(EXTENSION_CONTRIBUTORS "Joseph Szatkowski (Washington University in St. Louis)")
set(EXTENSION_DESCRIPTION "Analyzes 3D musculoskeletal images and generates reports.")
set(EXTENSION_STATUS "Alpha")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/main/Scripted/MusculoskeletalAnalysis/Resources/Icons/MusculoskeletalAnalysis.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/main/Scripted/MusculoskeletalAnalysis/Resources/Icons/Screenshot.png")

set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
#set(Slicer_DIR "C:/D/S4R/Slicer-build")
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Scripted)
add_subdirectory(CLI)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
