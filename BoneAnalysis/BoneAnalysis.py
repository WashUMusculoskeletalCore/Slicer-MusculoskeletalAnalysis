import logging
import os
import time 
import vtk
import numbers

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


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
        2. Select a segmentation representing the bone area to analyze. For cortical analysis exclude the medullary cavity. For cancellous analysis exclude the cortical bone.\n
        3. Use the threshold slider to select a threshold identifying the bone.\n
        4. Select the function to perform. See <a href="https://github.com/WashUMusculoskeletalCore/Slicer-BoneAnalysis/blob/main/README.md">here</a> for more information.\n
        5. Select the directory to send the output files to. If files already exist they will be appended to.\n
        6. Click "Apply"\n
        ADVANCED\n
        7. If the image volume is not the original DICOM, select the original DICOM node to get DICOM tags from.
        """
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
        Developed by the Washington University in St. Louis Musculoskeletal Reseach Center.\n
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


    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='BoneAnalysis',
        sampleName='Cortical1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'BoneAnalysis1.png'),
        # Download URL and target file name
        uris="INSERT URL HERE",
        fileNames='CorticalSample1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='INSERT CHECKSUM HERE',
        # This node name will be used when the data set is loaded
        nodeNames='Cortical'
    )

    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='BoneAnalysis',
        sampleName='CorticalMask',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'BoneAnalysis1.png'),
        # Download URL and target file name
        uris="INSERT URL HERE",
        fileNames='CorticalMaskSample.seg.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='INSERT CHECKSUM HERE',
        # This node name will be used when the data set is loaded
        nodeNames='CorticalMask'
    )


    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='BoneAnalysis',
        sampleName='Cancellous',
        thumbnailFileName=os.path.join(iconsPath, 'BoneAnalysis2.png'),
        # Download URL and target file name
        uris="INSERT URL HERE",
        fileNames='CancellousSample.nrrd',
        checksums='INSERT CHECKSUM HERE',
        # This node name will be used when the data set is loaded
        nodeNames='Cancellous'
    )


    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='BoneAnalysis',
        sampleName='CancellousMask',
        thumbnailFileName=os.path.join(iconsPath, 'BoneAnalysis2.png'),
        # Download URL and target file name
        uris="INSERT URL HERE",
        fileNames='CancellousMaskSample.seg.nrrd',
        checksums='INSERT CHECKSUM HERE',
        # This node name will be used when the data set is loaded
        nodeNames='CancellousMask'
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

        # Hidden elements
        self.ui.AnalysisProgress.hide()
        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()
        
        

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

        # Set default state for flags
        self._parameterNode.SetParameter("Analyzing", "False")

        
        
        


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
        
        if self._parameterNode.GetParameter("Analyzing")=="True":
            self.ui.applyButton.toolTip = "Currently running analysis"
            self.ui.applyButton.enabled = False
        elif self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetParameter("BoneSegmentID") and (self._parameterNode.GetParameter("UseDICOM")=="False" or self._parameterNode.GetNodeReferenceID("DICOMNode")):
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
        self.setNumParameter("0018,0050", str(self.ui.voxelSizeLineEdit.text))
        self.setNumParameter("0029,1000", str(self.ui.scalingLineEdit.text))
        self.setNumParameter("0029,1004", str(self.ui.densitySlopeLineEdit.text))
        self.setNumParameter("0029,1005", str(self.ui.densityInterceptLineEdit.text))
        self.setNumParameter("0029,1006", str(self.ui.waterDensityLineEdit.text))
        self._parameterNode.SetParameter("OutputDirectory", str(self.ui.outputDirectorySelector.currentPath))

        self._parameterNode.EndModify(wasModified)
        self.updateGUIFromParameterNode()

    # Sets a parameter to a value if the value can be converted to a float, otherwises sets it to blank
    def setNumParameter(self, parameter, value):
        try:
            float(value)
            self._parameterNode.SetParameter(parameter, value)
        except ValueError:
            self._parameterNode.SetParameter(parameter, "")


    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
            # Compute output
            self.logic.process(self._parameterNode.GetNodeReference("InputVolume"), self._parameterNode.GetNodeReference("SegmentNode"), self._parameterNode.GetParameter("BoneSegmentID"), 
                               self.ui.thresholdSelector.lowerThreshold,  self.ui.thresholdSelector.upperThreshold, self.ui.analysisSelector.currentText, self.ui.outputDirectorySelector.currentPath,
                               self.ui.AlternateDICOMCheckBox.checkState, self._parameterNode.GetNodeReference("DICOMNode"), self.ui.ManualDICOMCheckBox.checkState, 
                               {"0018,0050":self._parameterNode.GetNodeReference("0018,0050"), "0029,1000":self._parameterNode.GetNodeReference("0029,1000"), "0029,1004":self._parameterNode.GetNodeReference("0029,1004"), "0029,1005":self._parameterNode.GetNodeReference("0029,1005"), "0029,1006":self._parameterNode.GetNodeReference("0029,1006")}, self)        
        self.updateGUIFromParameterNode()
            
            


    def analysisUpdate(self, cliNode, event):
        if cliNode.GetStatus() & cliNode.Completed:
            self.ui.AnalysisProgress.setValue(100)
            self.ui.AnalysisProgress.hide()
            if cliNode.GetStatus() & cliNode.ErrorsMask:
                # error
                errorText = cliNode.GetErrorText()
                print("CLI execution failed: " + errorText)
            else:
                # success
                print("CLI execution succeeded.")    
            startTime=float(self._parameterNode.GetParameter("startTime"))
            stopTime = time.time()
            logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')
            # Clean up temp nodes
            slicer.mrmlScene.RemoveNode(self._parameterNode.GetNodeReference("labelMap"))          
            slicer.mrmlScene.RemoveNode(cliNode)
            self._parameterNode.SetParameter("Analyzing", "False")
        else:
            self.ui.AnalysisProgress.setValue(cliNode.GetProgress())


        


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

    def process(self, inputVolume, mask, maskLabel, lowerThreshold, upperThreshold, analysis, outputDirectory, altDICOM=False, DICOMNode=None, manDICOM=False, DICOMOptions=None, source=None, wait=False):
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
        if altDICOM and not DICOMNode:
            raise ValueError("No DICOM source")
        if manDICOM and not all(DICOMOptions):
            raise ValueError("Not all DICOM options are selected")
        if not os.access(outputDirectory, os.W_OK):
            if not os.access(outputDirectory, os.F_OK):
                # If directory doesn't exist try to create it
                try: 
                    os.makedirs(outputDirectory)
                    if not os.access(outputDirectory, os.W_OK):
                        raise ValueError("Output Directory is invalid")
                except:
                    raise ValueError("Output Directory is invalid")
            else:
                # If directory is not writable for other reason
                raise ValueError("Output Directory is invalid")

        startTime = time.time()
        logging.info('Processing started')
        
        # Get mask segment
        maskID = mask.GetSegmentation().GetSegmentIdBySegmentName(maskLabel)
        maskArray = vtk.vtkStringArray()
        maskArray.InsertNextValue(maskID)
        labelmap = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsToLabelmapNode(mask, maskArray, labelmap, inputVolume)
        

        # Get DICOM source
        if altDICOM and DICOMNode:
            dSource = DICOMNode
        elif manDICOM and DICOMOptions:
            dSource = DICOMOptions
        else:
            dSource = inputVolume

        # Get Density info
        slope=float(self.getDICOMTag(dSource, '0029,1006'))*float(self.getDICOMTag(dSource, '0029,1004'))/1000
        intercept=float(self.getDICOMTag(dSource, '0029,1006'))*float(self.getDICOMTag(dSource, '0029,1004'))+float(self.getDICOMTag(dSource, '0029,1005'))

        voxelSize = self.getDICOMTag(dSource, '0018,0050')

        # Prepare parameters for the selected function
        if analysis == "Cortical": 
            parameters = {"image":inputVolume, "mask":labelmap, "lowerThreshold":lowerThreshold, "upperThreshold":upperThreshold, "voxelSize":voxelSize, "slope":slope, "intercept":intercept, "output":outputDirectory}
            module=slicer.modules.corticalanalysis
        elif analysis == "Cancellous":
            parameters = {"image":inputVolume, "mask":labelmap, "lowerThreshold":lowerThreshold, "upperThreshold":upperThreshold, "voxelSize":voxelSize, "slope":slope, "intercept":intercept, "output":outputDirectory}
            module=slicer.modules.cancellousanalysis
        elif analysis == "Density":
            parameters = {"image":inputVolume, "mask":labelmap, "voxelSize":voxelSize, "slope":slope, "intercept":intercept, "output":outputDirectory}
            module=slicer.modules.densityanalysis
        node = slicer.cli.createNode(module, parameters=parameters)
        # Set up source before running to avoid race conditions
        if source:
            source.ui.AnalysisProgress.setValue(0)
            source.ui.AnalysisProgress.show()
            source._parameterNode.SetParameter("Analyzing", "True")
            source._parameterNode.SetNodeReferenceID("labelmapNode", labelmap.GetID())
            source._parameterNode.SetParameter("startTime", str(startTime))
            node.AddObserver('ModifiedEvent', source.analysisUpdate)   
        slicer.cli.run(module=module, node=node, wait_for_completion=wait)   
        

    # Used to get dicom metadata from the volume
    # source: the volume node or DICOM dict
    # tag: The DICOM tag number as a string ('####,####')
    def getDICOMTag(self, source, tag):
        if type(source) is dict:
            data=source[tag]
        else:
            shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
            volumeItemId = shNode.GetItemByDataNode(source)
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
        #registerSampleData()
        #inputVolume = SampleData.downloadSample('Cortical')
        #mask = SampleData.downloadSample('CorticalMask')
        inputVolume = slicer.util.loadVolume("C:/Users/szatkowski/Documents/4195_Linear_Attenuation_1-cm_(4195).nrrd")    
        mask = slicer.util.loadSegmentation("C:/Users/szatkowski/Documents/Segmentation.seg.nrrd")
        maskLabel = "Segment_1"
        lowerThreshold = 1643
        upperThreshold = 7437
        analysis="Cortical"
        options = {"0018,0050":0.007996, "0029,1000":4096,"0029,1004":365.712, "0029,1005":-199.725998, "0029,1006":0.4939}
        outputDirectory = os.path.expanduser("~\\Documents\\BoneAnalysisTest")      
        self.delayDisplay('Loaded test data set')

        # Test the module logic

        logic = BoneAnalysisLogic()

        
        # Test cortical analysis
        logic.process(inputVolume, mask, maskLabel, lowerThreshold, upperThreshold, analysis, outputDirectory, manDICOM=True, DICOMOptions=options, wait=True)
        testFile(os.path.join(outputDirectory, "cortical.txt"), [])
        # Use assert statements here to test output
        """
        inputVolume = SampleData.downloadSample('Cancellous')
        mask = SampleData.downloadSample('CancellousMask')
        maskLabel = "Segment_1"
        lowerThreshold = 1234
        upperThreshold = 5678
        analysis="Cancellous"      
        self.delayDisplay('Loaded test data set')
        # Test cancellous analysis
        logic.process(inputVolume, mask, maskLabel, lowerThreshold, upperThreshold, analysis, outputDirectory)


        analysis="Density"
        self.delayDisplay('Loaded test data set')
        # Test density analysis
        logic.process(inputVolume, mask, maskLabel, lowerThreshold, upperThreshold, analysis, outputDirectory)
        """

        self.delayDisplay('Test passed')


def testFile(fileName, data):
    with open(fileName) as f:
        lines = f.read().splitlines()
        firstLine = lines[0]
        lastLine = lines[-1]
    header = firstLine.split("\t")
    testData = lastLine.split("\t")
    assert len(data) == len(testData), "Expected "+ str(len(data)) + " lines, got " + str(len(testData)) + " instead."
    for i in range(data.length):
        if isinstance(testData[i], numbers.Number):
            assert data[i] > testData[i]*.95 and data[i] < testData[i]*1.05, "Value for " + header[i] + ", " + data[i] + " outside of range of expected value " + testData[i] + "."
        else:
            assert data[i] == testData[i], "Value for " + header[i] + ", " + data[i] + ", doesn't match expected value " + testData[i] + "."
        
