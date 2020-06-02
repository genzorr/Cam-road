import QtQuick 2.12

Item {
    id: root

    property real value: 0
    property string txtcolor: "white"

    width: 20
    height: 15

    anchors.bottomMargin: 1
    anchors.leftMargin: 5

    Rectangle {
        id: lvl1
        width: root.width/5 - 1
        height: 1*root.height/5
        color: txtcolor
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        opacity: value > 0 ? 1 : 0.25
    }
    Rectangle {
        id: lvl2
        width: root.width/5 - 1
        height: 2*root.height/5
        color: txtcolor
        anchors.bottom: parent.bottom
        anchors.left: lvl1.right
        anchors.leftMargin: 1
        opacity: value >= 0.2 ? 1 : 0.25
    }
    Rectangle {
        id: lvl3
        width: root.width/5 - 1
        height: 3*root.height/5
        color: txtcolor
        anchors.bottom: parent.bottom
        anchors.left: lvl2.right
        anchors.leftMargin: 1
        opacity: value >= 0.4 ? 1 : 0.25
    }
    Rectangle {
        id: lvl4
        width: root.width/5 - 1
        height: 4*root.height/5
        color: txtcolor
        anchors.bottom: parent.bottom
        anchors.left: lvl3.right
        anchors.leftMargin: 1
        opacity: value >= 0.6 ? 1 : 0.25
    }
    Rectangle {
        id: lvl5
        width: root.width/5 - 1
        height: 5*root.height/5
        color: txtcolor
        anchors.bottom: parent.bottom
        anchors.left: lvl4.right
        anchors.leftMargin: 1
        opacity: value >= 0.8 ? 1 : 0.25
    }

}
