"""
Created on 2016/7/16

@author: Miguel
"""

import unittest
import maya.cmds as cmds
import logging

logger = logging.Logger(__name__)

# make sure picker studio is running:
def recreateCube(pCube):
    if cmds.objExists(pCube):
        cmds.delete(pCube)
    cmds.polyCube()


def recreateSphere(pSphere):
    if cmds.objExists(pSphere):
        cmds.delete(pSphere)
    cmds.polySphere()
    cmds.move(2, 1, 2, pSphere)


def recreateCone(pCone):
    if cmds.objExists(pCone):
        cmds.delete(pCone)
    cmds.polyCone()
    cmds.move(-2, 1, -2, pCone)


mgpkr_old_language = cmds.MGPicker(q=True, config=("language", ""))


def resetLanguageConfig():
    cmds.MGPicker(e=True, config=("language", "English"))


class Test_MGPickerItems(unittest.TestCase):
    """
    Unitest for MGPickerItem command.
    """

    def createButton(self):
        self.panel = cmds.MGPickerItem(
            type="panel",
            label="Panel1",
            frameColor=(0.2, 0.2, 0.2, 1),
            x=0,
            y=0,
            w=400,
            h=300,
        )

        self.selectButton = cmds.MGPickerItem(
            type="selectButton",
            p=self.panel,
            label="selectBtn",
            x=20,
            y=20,
            w=100,
            h=20,
        )

        self.commandButton = cmds.MGPickerItem(
            type="commandButton", p=self.panel, label="cmdBtn", x=20, y=50, w=100, h=20
        )

        self.selectButton1 = cmds.MGPickerItem(
            type="selectButton",
            p=self.panel,
            label="selectBtn1",
            x=20,
            y=80,
            w=100,
            h=20,
        )

        self.attrButton = cmds.MGPickerItem(
            type="attributeButton",
            p=self.panel,
            label="Toggle",
            valueColor=(0.1, 0.5, 0.5, 1),
            x=200,
            y=35,
            w=100,
            h=20,
        )

        self.slider = cmds.MGPickerItem(
            type="slider",
            p=self.panel,
            sliderHAttribute=(self.pCube + ".translateX"),
            sliderVAttribute=(self.pCube + ".translateY"),
            label=(self.pCube + ".:tx-ty"),
            x=23,
            y=100,
            w=100,
            h=100,
        )

        self.text = cmds.MGPickerItem(
            p=self.panel,
            type="text",
            x=200,
            y=80,
            labelFontSize=11,
            label="The attribute button\ncontrols the select-button,\ncommand-button and the slider.",
            resizePreferSize=True,
        )

        self.buttons = [
            self.selectButton,
            self.commandButton,
            self.attrButton,
            self.slider,
            self.text,
        ]
        self.allButtons = [self.panel]
        self.allButtons.extend(self.buttons)

    def setUp(self):
        cmds.MGPicker(createTempPicker=True)
        cmds.MGPicker(e=True, namespace="")
        self.pCube = "pCube1"
        self.pSphere = "pSphere1"
        self.pCone = "pCone1"
        self.nodes = [self.pCube, self.pSphere, self.pCone]
        recreateCube(self.pCube)
        recreateSphere(self.pSphere)
        recreateCone(self.pCone)
        self.createButton()
        resetLanguageConfig()

    def flagTest(
        self,
        btn,
        flagDict,
        assertFalse=False,
        assertItemsEqual=False,
        almostEqual=False,
    ):
        cmds.MGPickerItem(btn, edit=True, **flagDict)
        newValue = flagDict.values()[0]
        flag = flagDict.keys()[0]
        queryDict = {flag: True}
        actualValue = cmds.MGPickerItem(btn, q=True, **queryDict)
        if not assertFalse:
            err = "Expect %s.%s = %s, actual value: %s" % (
                btn,
                flag,
                newValue,
                actualValue,
            )
            if not assertItemsEqual:
                if not almostEqual:
                    self.assertEqual(actualValue, newValue, err)
                else:
                    self.assertAlmostEqual(actualValue, newValue, 3, err)

            else:
                self.assertItemsEqual(list(actualValue), list(newValue), err)
        else:
            err = "Expect %s.%s not equal to %s" % (btn, flag, actualValue)
            self.assertNotEqual(actualValue, newValue, err)

    def flagTestToAllButtonsExceptPanel(
        self, flagDict, assertFalse=False, assertItemsEqual=False, almostEqual=False
    ):
        for btn in self.buttons:
            self.flagTest(
                btn, flagDict, assertFalse, assertItemsEqual, almostEqual=almostEqual
            )

    def flagTestToAllButtons(
        self, flagDict, assertFalse=False, assertItemsEqual=False, almostEqual=False
    ):
        for btn in self.allButtons:
            self.flagTest(
                btn, flagDict, assertFalse, assertItemsEqual, almostEqual=almostEqual
            )

    def flagTestAlmostEqualList(self, btn, flagDict, assertFalse=False):
        cmds.MGPickerItem(btn, edit=True, **flagDict)
        newValue = list(flagDict.values()[0])
        flag = flagDict.keys()[0]
        queryDict = {flag: True}
        cValues = list(cmds.MGPickerItem(btn, q=True, **queryDict))
        if not assertFalse:
            for i in range(len(cValues)):
                self.assertAlmostEqual(
                    cValues[i],
                    newValue[i],
                    3,
                    "Error set & get %s: %s, %s" % (flag, cValues[i], newValue[i]),
                )
        else:
            for i in range(len(cValues)):
                self.assertNotAlmostEqual(
                    cValues[i],
                    newValue[i],
                    3,
                    "Should issue error set & get %s but it succeed!" % flag,
                )

    def flagTestAlmostEqualListToAllButtonsExceptPanel(
        self, flagDict, assertFalse=False
    ):
        for btn in self.buttons:
            self.flagTestAlmostEqualList(btn, flagDict, assertFalse)

    def flagTestAlmostEqualListToAllButtons(self, flagDict, assertFalse=False):
        for btn in self.allButtons:
            self.flagTestAlmostEqualList(btn, flagDict, assertFalse)

    def tearDown(self):
        cmds.MGPicker(closeAll=True)

    def test_ItemCreation(self):
        self.assertTrue(
            cmds.MGPickerItem(self.panel, exist=True, q=True),
            "Error creating the picker panel!",
        )
        self.assertTrue(
            cmds.MGPickerItem(self.selectButton, exist=True, q=True),
            "Error creating the selectButton!",
        )
        self.assertTrue(
            cmds.MGPickerItem(self.commandButton, exist=True, q=True),
            "Error creating the commandButton!",
        )
        self.assertTrue(
            cmds.MGPickerItem(self.attrButton, exist=True, q=True),
            "Error creating the attrButton!",
        )
        self.assertTrue(
            cmds.MGPickerItem(self.slider, exist=True, q=True),
            "Error creating the slider!",
        )
        self.assertTrue(
            cmds.MGPickerItem(self.text, exist=True, q=True), "Error creating the text!"
        )

    def test_postChangeCommand(self):
        self.flagTest(self.attrButton, {"postChangeCommand": 'print "bingo"'})
        self.flagTest(self.attrButton, {"poc": 'print "bingo"'})

    def test_postChangeCommandType(self):
        self.flagTest(self.attrButton, {"postChangeCommandType": "python"})
        self.flagTest(self.attrButton, {"pot": "mel"})

    def test_preChangeCommand(self):
        self.flagTest(self.attrButton, {"preChangeCommand": 'print "bingo"'})
        self.flagTest(self.attrButton, {"prc": 'print "bingo"'})

    def test_preChangeCommandType(self):
        self.flagTest(self.attrButton, {"preChangeCommandType": "python"})
        self.flagTest(self.attrButton, {"prt": "mel"})

    def test_rotation(self):
        self.flagTest(self.selectButton, {"rotation": -180})
        self.flagTest(self.selectButton, {"r": 180})
        self.flagTest(self.selectButton, {"shape": "bezier"})
        self.flagTest(self.selectButton, {"rotation": 50}, assertFalse=True)
        self.flagTest(self.selectButton, {"shape": "polygon"})
        self.flagTest(self.selectButton, {"rotation": 50}, assertFalse=True)

    def test_roundness(self):
        self.flagTestToAllButtons({"roundness": 0})
        self.flagTestToAllButtons({"roundness": 2})
        self.flagTestToAllButtons({"rd": 100})

    def test_sliderChangeCommand(self):
        self.flagTest(self.slider, {"sliderChangeCommand": 'print "bingo"'})
        self.flagTest(self.slider, {"scc": 'print "bingo"'})

    def test_sliderChangeCommandType(self):
        self.flagTest(self.slider, {"sliderChangeCommandType": "python"})
        self.flagTest(self.slider, {"sct": "mel"})

    def test_sliderHSpeed(self):
        self.flagTest(self.slider, {"sliderHSpeed": -1})
        self.flagTest(self.slider, {"shs": 1})

    def test_sliderHMax(self):
        self.flagTest(self.slider, {"sliderHMax": 2})
        self.flagTest(self.slider, {"shx": 10})

    def test_showItemTip(self):
        cmds.MGPickerItem(self.commandButton, edit=True, showItemTip="This is the tip")
        cmds.MGPickerItem(self.commandButton, edit=True, sit="")

    def test_selectMembers(self):
        cmds.MGPickerItem(
            self.selectButton, edit=True, selectMembers=" ".join(self.nodes)
        )
        members = cmds.MGPickerItem(self.selectButton, q=True, sms=True)
        self.assertItemsEqual(members, self.nodes)
        testList = [self.pCube, self.pSphere]
        cmds.MGPickerItem(
            self.selectButton, edit=True, selectMembers=" ".join(testList)
        )
        members = cmds.MGPickerItem(self.selectButton, q=True, sms=True)
        self.assertItemsEqual(members, testList)
        cmds.MGPickerItem(self.selectButton, edit=True, selectMembers="")
        members = cmds.MGPickerItem(self.selectButton, q=True, sms=True)
        self.assertFalse(members)

    def test_subNamespace(self):
        btns = [self.selectButton, self.commandButton, self.attrButton, self.slider]
        for btn in btns:
            self.flagTest(btn, {"subNamespace": "haha"})
            self.flagTest(btn, {"sns": "haha:bingo"})

    def test_xPosition(self):
        self.flagTestToAllButtons({"xPosition": 0})
        self.flagTestToAllButtons({"x": -150})

    def test_yPosition(self):
        self.flagTestToAllButtons({"yPosition": 100})
        self.flagTestToAllButtons({"y": -150})
