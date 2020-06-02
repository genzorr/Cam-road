import QtQuick 2.12
import QtQuick.Controls 2.12

RadioButton {
    property real size: 25
    property real fontsize: 12

    id: rbtn
    contentItem: Text {
        text: rbtn.text
        font.family: "Calibri Solid Italic"
        font.pointSize: fontsize
        color: rbtn.enabled ? "white": "#b2b2b2"
        verticalAlignment: Text.AlignVCenter
        leftPadding: 1.5*rbtn.indicator.width
    }
    indicator: Rectangle {
        width: size
        height: size
        anchors.verticalCenter: parent.verticalCenter
        color: "transparent"
        border.color: rbtn.enabled ? "white": "#b2b2b2"
        border.width: 2
        radius: width/2

        Rectangle {
            visible: rbtn.checked
            width: parent.width-4*parent.border.width
            height: width
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            color: rbtn.enabled ? "white": "#b2b2b2"
            radius: width/2
        }
    }

}

