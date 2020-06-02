import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Shapes 1.12

CheckBox {
    property real size: 25
    property real fontsize: 12

    id: chbox
    contentItem: Text {
        text: chbox.text
        font.family: "Calibri Solid Italic"
        font.pointSize: fontsize
        color: "white"
        verticalAlignment: Text.AlignVCenter
        leftPadding: 1.5*chbox.indicator.width
    }
    indicator: Rectangle {
        width: size
        height: size
        anchors.verticalCenter: parent.verticalCenter
        color: "transparent"
        border.color: "white"
        border.width: 2

        Shape {
            visible: chbox.checked
            ShapePath {
                id: checkmark
                property int gap: 2*chbox.indicator.border.width
                strokeWidth: 2
                strokeColor: "white"
                fillColor: "transparent"
                startX: checkmark.gap; startY: chbox.indicator.height/2
                PathLine { x: checkmark.gap; y: chbox.indicator.height/2}
                PathLine { x: chbox.indicator.width/2; y: chbox.indicator.height-checkmark.gap }
                PathLine { x: chbox.indicator.width-checkmark.gap; y: checkmark.gap }
            }
        }
    }
}
