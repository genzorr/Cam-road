import QtQuick 2.12
import QtQuick.Controls 2.12

Slider {
    id: slider
    stepSize: 1
    height: 80

    background: Rectangle {
        x: slider.leftPadding
        y: slider.topPadding + slider.availableHeight / 2 - height / 2
        width: slider.availableWidth
        height: implicitHeight
        implicitWidth: slider.width
        implicitHeight: 4
        color: "#30ffffff"

        Rectangle {
            width: slider.visualPosition * parent.width
            height: parent.height
            color: "white"
            radius: 2
        }
    }

    handle: Rectangle {
        x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
        y: slider.topPadding + slider.availableHeight / 2 - height / 2
        width: 25
        height: 25
        radius: width/2
        color: "white"
    }

    Repeater {
        id: rep
        model:  10
        Rectangle {
            color: "transparent"
            anchors.verticalCenter: slider.verticalCenter
            anchors.left: slider.left
            anchors.leftMargin: slider.handle.width/2+slider.leftPadding+index*((slider.availableWidth-slider.handle.width)/(rep.count-1))
            Rectangle {
                id: tickmark
                color: "white"
                width: 2 ; height: 2
                radius: width/2
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.verticalCenter
                anchors.topMargin: slider.handle.height

            }
            Text {
                text: (slider.from+slider.stepSize*index).toString()
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: tickmark.bottom
                anchors.topMargin: 5
                font.family: "Calibri Solid Italic"
                font.pointSize: 12
                color: "white"
            }
        }
    }
}
