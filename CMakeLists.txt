cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(BoneAnalysis)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/WashUMusculoskeletalCore/Slicer-BoneAnalysis")
set(EXTENSION_CATEGORY "Analysis")
set(EXTENSION_CONTRIBUTORS "Joseph Szatkowski ([Musculoskeletal Research Center]Washington University in St. Louis)")
set(EXTENSION_DESCRIPTION "Analyzes 3D bone images and generates reports.")
set(EXTENSION_STATUS "Pre-alpha")
#set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/BoneAnalyisis.png")
#set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/BoneAnalyisis/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
#set(Slicer_DIR "C:/D/S4R/Slicer-build")
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BoneAnalysis)
add_subdirectory(Submodules)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
