import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import qt


#
# BoneAnalysis
#

class BoneAnalysis(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Bone Analysis"
        self.parent.categories = ["Analysis"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = ["CorticalAnalysis", "CancellousAnalysis", "DensityAnalysis"]  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Joseph Szatkowski (Washington University in St. Louis)"]
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
1. Select a volume containing the image to analyze.\n
2. Select a segmentation representing the area to analyze. Include the bone and medullary cavity. For cancellous analysis exclude the cortical bone.\n
3. Use the threshold slider to select a threshold identifying the bone.\n
4. Select the function to perform. See <a href="https://github.com/WashUMusculoskeletalCore/Washington-University-Musculoskeletal-Image-Analyses">INSERT DOCUMENTATION LINK HERE</a> for more information.\n
5. Select the directory to send the output files to. If files already exist they will be appended to.\n
6. Click "Apply"\n
ADVANCED\n
7. If the image volume is not the original DICOM, select the original DICOM node to get DICOM tags from.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was partially funded by NIH grant INSERT NUMBER HERE.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # BoneAnalysis1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='BoneAnalysis',
        sampleName='BoneAnalysis1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'BoneAnalysis1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='BoneAnalysis1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='BoneAnalysis1'
    )

    # BoneAnalysis2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='BoneAnalysis',
        sampleName='BoneAnalysis2',
        thumbnailFileName=os.path.join(iconsPath, 'BoneAnalysis2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='BoneAnalysis2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='BoneAnalysis2'
    )


#
# BoneAnalysisWidget
#

class BoneAnalysisWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):        
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/BoneAnalysis.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = BoneAnalysisLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.inputVolumeChanged)
        self.ui.segmentSelector.connect("currentNodeChanged(vtkMRMLNode*)",self.segmentNodeChanged)
        self.ui.segmentSelector.connect("currentSegmentChanged(QString)",self.segmentChanged)
        self.ui.thresholdSelector.connect("thresholdValuesChanged(double, double)", self.updateParameterNodeFromGUI)
        self.ui.analysisSelector.connect("currentTextChanged(const QString)", self.updateParameterNodeFromGUI)
        self.ui.DICOMOptions.connect("buttonClicked(QAbstractButton*)", self.updateParameterNodeFromGUI)
        self.ui.DICOMSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.DICOMSeriesChanged)
        self.ui.voxelSizeLineEdit.connect("editingFinished()", self.updateParameterNodeFromGUI)
        self.ui.scalingLineEdit.connect("editingFinished()", self.updateParameterNodeFromGUI)
        self.ui.densitySlopeLineEdit.connect("editingFinished()", self.updateParameterNodeFromGUI)
        self.ui.densityInterceptLineEdit.connect("editingFinished()", self.updateParameterNodeFromGUI)
        self.ui.waterDensityLineEdit.connect("editingFinished()", self.updateParameterNodeFromGUI)
        self.ui.outputDirectorySelector.connect("currentPathChanged(const QString)", self.updateParameterNodeFromGUI)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

        # Validator
        numValidator = qt.DoubleValidator()


        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()
        self.ui.voxelSizeLineEdit.
        self.ui.scalingLineEdit.
        self.ui.densitySlopeLineEdit.
        self.ui.densityInterceptLineEdit.
        self.ui.waterDensityLineEdit.
        

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

        if not self._parameterNode.GetNodeReference("SegmentNode"):
            firstSegmentNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
            if firstSegmentNode:
                self._parameterNode.SetNodeReferenceID("SegmentNode", firstSegmentNode.GetID())
        if not self._parameterNode.GetParameter("BoneSegmentID"):
            if self._parameterNode.GetNodeReference("SegmentNode"):
                segmentation = self._parameterNode.GetNodeReference("SegmentNode").GetSegmentation()
                self._parameterNode.SetParameter("BoneSegmentID", segmentation.GetNthSegmentID(0))

        if not self._parameterNode.GetNodeReference("DICOMNode"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("DICOMNode", firstVolumeNode.GetID())

        
        
        


    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update node selectors and sliders
        #self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
        #self.ui.segmentSelector.setCurrentNode(self._parameterNode.GetNodeReference("SegmentSelectionNode"))
        #self.ui.segmentSelector.setCurrentSegmentID(str(self._parameterNode.GetParameter("BoneSegmentID")))
        self.ui.thresholdSelector.setMRMLVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
        if self._parameterNode.GetParameter("LowerThreshold") and self._parameterNode.GetParameter("UpperThreshold"):
            self.ui.thresholdSelector.setLowerThreshold(float(self._parameterNode.GetParameter("LowerThreshold")))
            self.ui.thresholdSelector.setUpperThreshold(float(self._parameterNode.GetParameter("UpperThreshold")))
        self.ui.analysisSelector.setCurrentText(str(self._parameterNode.GetParameter("Analysis")))
        self.ui.AlternateDICOMCheckBox.setChecked(self._parameterNode.GetParameter("UseAlt")=="True")
        self.ui.ManualDICOMCheckBox.setChecked(self._parameterNode.GetParameter("UseMan")=="True")
        self.ui.DICOMSelector.setCurrentNode(self._parameterNode.GetNodeReference("DICOMNode"))
        self.ui.voxelSizeLineEdit.setText(self._parameterNode.GetParameter("0018,0050"))
        self.ui.scalingLineEdit.setText(self._parameterNode.GetParameter("0029,1000"))
        self.ui.densitySlopeLineEdit.setText(self._parameterNode.GetParameter("0029,1004"))
        self.ui.densityInterceptLineEdit.setText(self._parameterNode.GetParameter("0029,1005"))
        self.ui.waterDensityLineEdit.setText(self._parameterNode.GetParameter("0029,1006"))
        self.ui.outputDirectorySelector.setCurrentPath(str(self._parameterNode.GetParameter("OutputDirectory")))

        # Update buttons states and tooltips
        if self._parameterNode.GetNodeReference("InputVolume"):
            self.ui.thresholdSelector.enabled = True
        else:
            self.ui.thresholdSelector.enabled = False

        self.ui.DICOMSelector.enabled = (self._parameterNode.GetParameter("UseAlt")=="True")
        manual = (self._parameterNode.GetParameter("UseMan")=="True")
        self.ui.voxelSizeLineEdit.enabled=manual
        self.ui.scalingLineEdit.enabled=manual
        self.ui.densitySlopeLineEdit.enabled=manual
        self.ui.densityInterceptLineEdit.enabled=manual
        self.ui.waterDensityLineEdit.enabled=manual
        self.ui.voxelSizeLabel.enabled=manual
        self.ui.scalingLabel.enabled=manual
        self.ui.densitySlopeLabel.enabled=manual
        self.ui.densityInterceptLabel.enabled=manual
        self.ui.waterDensityLabel.enabled=manual
        

        if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetParameter("BoneSegmentID") and (self._parameterNode.GetParameter("UseDICOM")=="False" or self._parameterNode.GetNodeReferenceID("DICOMNode")):
            self.ui.applyButton.toolTip = "Perform the selected analysis"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input volume node, input segment, and output directory"
            self.ui.applyButton.enabled = False

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False       

    def inputVolumeChanged(self, event):
        """
        Called when the input volume is changed in the selector.
        Passes the caller information to updateParameterNode
        """
        self.updateParameterNodeFromGUI(event, "InputVolume")

    def segmentNodeChanged(self, event):
        """
        Called when the segment node is changed in the selector.
        Passes the caller information to updateParameterNode
        """
        self.updateParameterNodeFromGUI(event, "SegmentNode")


    def segmentChanged(self, event):
        """
        Called when the segment is changed in the selector.
        Passes the caller information to updateParameterNode
        """
        self.updateParameterNodeFromGUI(event, "Segment")

    def DICOMSeriesChanged(self, event):
        self.updateParameterNodeFromGUI(event, "DICOM")

    def updateParameterNodeFromGUI(self, event=None, caller=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """
        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch
        self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
        if caller == "InputVolume":
            self._parameterNode.SetNodeReferenceID("InputVolume", event.GetID())
        elif caller == 'SegmentNode':
            self._parameterNode.SetNodeReferenceID("SegmentNode", event.GetID())
        elif caller == 'Segment':
            self._parameterNode.SetParameter("BoneSegmentID", str(event))
        elif caller == 'DICOM':
            self._parameterNode.SetNodeReferenceID("DICOMNode", event.GetID())
        self._parameterNode.SetParameter("LowerThreshold", str(self.ui.thresholdSelector.lowerThreshold))
        self._parameterNode.SetParameter("UpperThreshold", str(self.ui.thresholdSelector.upperThreshold))
        self._parameterNode.SetParameter("Analysis", str(self.ui.analysisSelector.currentText))
        self._parameterNode.SetParameter("UseAlt", str(self.ui.AlternateDICOMCheckBox.checked))     
        self._parameterNode.SetParameter("UseMan", str(self.ui.ManualDICOMCheckBox.checked)) 
        self._parameterNode.SetParameter("0018,0050", str(self.ui.voxelSizeLineEdit.text))
        self._parameterNode.SetParameter("0029,1000", str(self.ui.scalingLineEdit.text))
        self._parameterNode.SetParameter("0029,1004", str(self.ui.densitySlopeLineEdit.text))
        self._parameterNode.SetParameter("0029,1005", str(self.ui.densityInterceptLineEdit.text))
        self._parameterNode.SetParameter("0029,1006", str(self.ui.waterDensityLineEdit.text))
        self._parameterNode.SetParameter("OutputDirectory", str(self.ui.outputDirectorySelector.currentPath))

        self._parameterNode.EndModify(wasModified)

        self.updateGUIFromParameterNode()

    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
            # Compute output
            self.logic.process(self._parameterNode.GetNodeReference("InputVolume"), self._parameterNode.GetNodeReference("SegmentNode"), self._parameterNode.GetParameter("BoneSegmentID"), 
                               self.ui.thresholdSelector.lowerThreshold,  self.ui.thresholdSelector.upperThreshold, self.ui.analysisSelector.currentText, 
                               self.ui.AltenateDICOMCheckBox.checkState, self._parameterNode.GetNodeReference("DICOMNode"), self.ui.ManualDICOMCheckBox.checkState, 
                               [self._parameterNode.GetNodeReference("0018,0050"), self._parameterNode.GetNodeReference("0029,1000"), self._parameterNode.GetNodeReference("0029,1004"), self._parameterNode.GetNodeReference("0029,1005"), self._parameterNode.GetNodeReference("0029,1006")],
                               self.ui.outputDirectorySelector.currentPath)

            # Compute inverted output (if needed)
            #if self.ui.invertedOutputSelector.currentNode():
                # If additional output volume is selected then result with inverted threshold is written there
             #   self.logic.process(self.ui.inputSelector.currentNode(), self.ui.analysisSelector.currentText(),
             #                      self.ui.outputDirectory.currentPath(), showResult=False)



        


#
# BoneAnalysisLogic
#

class BoneAnalysisLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("Analysis"):
            parameterNode.SetParameter("Analysis", "Cortical")

    def process(self, inputVolume, mask, maskLabel, lowerThreshold, upperThreshold, analysis, altDICOM, DICOMNode, manDICOM, DICOMOptions, outputDirectory, showResult=True):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param InputVolume: volume to be thresholded
        :param Analysis: analysis function to perform
        :param OutputDirectory: directory to write output files to
        """

        # Check inputs
        if not inputVolume:
            raise ValueError("Input volume is invalid")
        if not mask or not maskLabel:
            raise ValueError("Segment is invalid")
        if not os.access(outputDirectory, os.W_OK):
            raise ValueError("Output Directory is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')
        
        # Get mask segment
        maskID = mask.GetSegmentation().GetSegmentIdBySegmentName(maskLabel)
        maskArray = vtk.vtkStringArray()
        maskArray.InsertNextValue(maskID)
        labelmap = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsToLabelmapNode(mask, maskArray, labelmap, inputVolume)
        

        # Get DICOM source
        if altDICOM:
            dSource = DICOMNode
        elif manDICOM:
            dSource = DICOMOptions
        else:
            dSource = inputVolume

        # Get Density info
        slope=float(self.getDICOMTag(dSource, '0029,1006'))*float(self.getDICOMTag(dSource, '0029,1004'))/1000
        intercept=float(self.getDICOMTag(dSource, '0029,1006'))*float(self.getDICOMTag(dSource, '0029,1004'))+float(self.getDICOMTag(dSource, '0029,1005'))

        # Execute the selected function
        if analysis == "Cortical": 
            parameters = {"image":inputVolume, "mask":labelmap, "lowerThreshold":lowerThreshold, "upperThreshold":upperThreshold, "voxelSize":self.getDICOMTag(dSource, '0018,0050'), "slope":slope, "intercept":intercept, "output":outputDirectory}
            node = slicer.cli.runSync(slicer.modules.corticalanalysis, None, parameters)
        elif analysis == "Cancellous":
            parameters = {"image":inputVolume, "mask":labelmap, "lowerThreshold":lowerThreshold, "upperThreshold":upperThreshold, "voxelSize":self.getDICOMTag(dSource, '0018,0050'), "slope":slope, "intercept":intercept, "output":outputDirectory}
            node = slicer.cli.runSync(slicer.modules.cancellousanalysis, None, parameters)
        elif analysis == "Density":
            parameters = {"image":inputVolume, "mask":labelmap, "voxelSize":self.getDICOMTag(dSource, '0018,0050'), "slope":slope, "intercept":intercept, "output":outputDirectory}
            node = slicer.cli.runSync(slicer.modules.densityanalysis, None, parameters)

        # Clean up temp nodes
        slicer.mrmlScene.RemoveNode(labelmap)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')

    # Used to get dicom metadata from the volume
    # inputVolume: the volume node
    # tag: The DICOM tag number as a string ('####,####')
    def getDICOMTag(self, inputVolume, tag):
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        volumeItemId = shNode.GetItemByDataNode(inputVolume)
        seriesInstanceUID = shNode.GetItemUID(volumeItemId, 'DICOM')

        db = slicer.dicomDatabase
        instanceList = db.instancesForSeries(seriesInstanceUID)
        data = db.instanceValue(instanceList[0], tag)
        return data


#
# BoneAnalysisTest
#

class BoneAnalysisTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_BoneAnalysis1()

    def test_BoneAnalysis1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('BoneAnalysis1')
        outputDirectory = "C:\BoneAnalysisTest"
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        # Test the module logic

        logic = BoneAnalysisLogic()

        # Test cortical analysis
        logic.process(inputVolume, "Cortical", outputDirectory)
        # Use assert statements here to test output

        # Test cancelous analysis
        logic.process(inputVolume, "Cancelous", outputDirectory)

        self.delayDisplay('Test passed')
