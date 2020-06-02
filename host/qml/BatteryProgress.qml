import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.0

ProgressBar {
    property string name: "BatteryProgress"
    property color bgcolor
    property color prmcolor
    id: prgb
    from: 0
    to: 1

    background: Rectangle {
        id: bg
        color: bgcolor
    }
    contentItem: Item {
        Rectangle {
            id: border
            border.width: 2
            border.color: prgb.value <= 0.2 ? "red" : prmcolor
            radius: 4
            width: bg.width
            height: bg.height
            color: "transparent"
            z: 10
            Rectangle {
                id: fill
                width: prgb.value * (bg.width-8) / (prgb.to-prgb.from)
                height: bg.height-8
                color: prgb.value <= 0.2 ? "red" : prmcolor
                anchors.left: parent.left
                anchors.leftMargin: 4
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}
