#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Donghao Wang
# time : 2020/6/22


__author__ = "dd"

import maya.OpenMayaUI as mui
try:
    from PySide2 import QtWidgets, QtCore
    from shiboken2 import wrapInstance
except ImportError:
    import PySide.QtGui as QtWidgets
    from PySide import QtCore
    from shiboken import wrapInstance
import pymel.core as pm
import maya.cmds as cmds
import logging
import maya.mel as mel

def get_cam_shape(sel_cam):
    try:
        cam_shape = sel_cam if pm.nodeType(sel_cam) == 'camera' else sel_cam.getShape()
        return cam_shape
    except:
        logging.error(u'Please Select The cam you want to bake！！')
        return False

def main(new_cam_name):
    sel_cam = pm.ls(sl=1)
    if not sel_cam:
        logging.error(u'Please Select The cam you want to bake！！')
        return False
    sel_cam = sel_cam[0]
    if pm.ls(new_cam_name):
        logging.error(u'This cam exists!Please input another name!')
        return False
    try:
        cam_shape = get_cam_shape(sel_cam)
        cam_transform = cam_shape.getParent()
        new_cam = pm.duplicate(cam_transform, rr=1, name=new_cam_name)[0]
        new_cam_shape = new_cam.getShape()
        pm.select(new_cam, r=1)
        mel.eval('Unparent;')
        mel.eval('DeleteHistory;')
        pm.select(cam_transform, new_cam, r=1)
        mel.eval('doCreateParentConstraintArgList 1 { "0","0","0","0","0","0","0","0","1","","1" };')
        cons_name = mel.eval('parentConstraint -weight 1;')
        pm.select(new_cam)
        min_time = pm.playbackOptions(min=True, query=True)
        max_time = pm.playbackOptions(max=True, query=True)
        all_shapes_source = cmds.listConnections(cam_shape.name(), s=1, d=0, p=1)
        if all_shapes_source:
            for es in all_shapes_source:
                dest = cmds.listConnections(es, d=1, s=0, p=1)[0]
                cmds.disconnectAttr(es,dest)
                dest = dest.replace(cam_shape.name(), new_cam_shape.name())
                cmds.connectAttr(es, dest)
        mel.eval('bakeResults -simulation true -t "%s:%s" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"%s"};'%(min_time, max_time, new_cam))
        transform_anims = cmds.listConnections(cam_transform.name(), s=1, d=0, type='animCurve') or []
        for trans in transform_anims:
            cmds.delete(trans)
        pm.delete(cons_name)
        return True
    except Exception as e:
        logging.error(u'Error occured: %s'%e)
        return False

def getMayaWindow():
    main_window_ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class BakeCamDialog(QtWidgets.QDialog):
    def __init__(self, parent_window=getMayaWindow()):
        super(BakeCamDialog, self).__init__(parent=parent_window)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle('Camera Backing Tool by wangdonghao @ mihoyoAnime')
        Dialog.resize(480, 150)
        layout = QtWidgets.QHBoxLayout()
        Dialog.setLayout(layout)
        label = QtWidgets.QLabel(u'Select the cam then input the new name：')
        self.line_edit = QtWidgets.QLineEdit(Dialog)
        doit_pb = QtWidgets.QPushButton('Bake!')
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(doit_pb)
        doit_pb.clicked.connect(self.bake_doit)
    
    def bake_doit(self):
        if not self.line_edit.text():
            logging.error(u'Input the name of the cam please!')
            return
        result = main(self.line_edit.text())
        if result:
            cmds.confirmDialog(t=u"Note", m=u"Success!", b=['OK'])
            self.close()