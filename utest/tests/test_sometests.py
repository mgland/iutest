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


class Test_MGPickerItem(unittest.TestCase):
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

    def test_annotation(self):
        newValue = "This is annotaion"
        for btn in self.allButtons:
            self.flagTest(btn, {"annotation": newValue})
            self.flagTest(btn, {"ann": newValue})

    def test_addSelectMember(self):
        logger.error("Some log error.")
        for btn in self.allButtons:
            if btn == self.selectButton:
                cmds.MGPickerItem(btn, edit=True, addSelectMember=self.pCube)
                members = cmds.MGPickerItem(btn, q=True, selectMembers=True)
                self.assertTrue(
                    self.pCube in members, "Error add member for select button!"
                )
            else:
                try:
                    cmds.MGPickerItem(btn, edit=True, addSelectMember=self.pCube)
                except:
                    pass
                else:
                    raise RuntimeError(
                        "addSelectMember should not works on non-selectButton"
                    )

        # Now test multiple flag usage:
        cmds.MGPickerItem(
            self.selectButton, edit=True, asm=(self.pCube, self.pSphere, self.pCone)
        )
        members = cmds.MGPickerItem(self.selectButton, q=True, sms=True)

        self.assertItemsEqual(
            members, self.nodes, "Error add multiple member for select button!"
        )

    def test_attributeType(self):
        logger.warning("Some log warning.")
        newValue = "enum"
        self.flagTest(self.attrButton, {"attributeType": newValue})
        self.flagTest(self.attrButton, {"atp": "bool"})

    def test_attribute(self):
        logger.info("Some log info.")
        self.assertTrue(False)
        # first test maya attribute:
        self.flagTest(self.attrButton, {"attributeType": "maya"})
        attr = "translateX"
        newValue = self.pCube + "." + attr
        self.flagTest(self.attrButton, {"attribute": newValue})
        newValue = self.pSphere + "." + attr
        self.flagTest(self.attrButton, {"att": newValue})

        # first test dummy enum attribute:
        self.flagTest(self.attrButton, {"attributeType": "enum"})
        enumValues = ["Proxy", "LoRes", "HiRes"]
        enumStr = ":".join(enumValues)
        self.flagTest(self.attrButton, {"attribute": enumStr})

        # for dummy bool attribute type, attribute return empty str:
        self.flagTest(self.attrButton, {"attributeType": "bool"})
        self.flagTest(self.attrButton, {"attribute": "haha"}, assertFalse=True)

    @unittest.skip("I just wanna skip.")
    def test_skip(self):
        pass

    def test_error(self):
        cmds.error("some maya error.")
        abcd

    def test_failed(self):
        cmds.warning("some maya warning.")
        self.assertTrue(False)

    def test_passed(self):
        print("some maya message.")
        self.assertTrue(True)
