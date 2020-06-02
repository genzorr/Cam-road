import QtQuick 2.12
import QtQuick.Shapes 1.12

Item {
    id: root

    property real value: 0
    property string fontfam: "Calibri Solid Italic"

    property real value_norm: {
        if (value>1.1) {return 1.1}
        if (value<-0.1) {return -0.1}
        else {return value}
    }

    width: 400

    Rectangle {
        id: ab_path
        color: "white"
        height: 2
        width: parent.width*10/12
        anchors.horizontalCenter: root.horizontalCenter
    }
    Shape {
        ShapePath {
            strokeWidth: 2
            strokeColor: "white"
            fillColor: "transparent"
            strokeStyle: ShapePath.DashLine
            dashPattern: [2, 4]
            startX: 0; startY: 1
            PathLine { x: root.width/2; y: ab_path.height/2}
            PathLine { x: root.width; y: ab_path.height/2 }
        }
    }

    Text {
        text: "A"
        font.family: fontfam
        font.pointSize: 16
        color: "white"
        anchors {
            top: ab_path.bottom
            topMargin: 5
            horizontalCenter: ab_path.horizontalCenter
            horizontalCenterOffset: -root.width*5/12
        }
    }
    Rectangle {
        color: "white"
        width: 2
        height: 10
        //radius: height/2
        anchors {
            verticalCenter: ab_path.verticalCenter
            horizontalCenter: ab_path.horizontalCenter
            horizontalCenterOffset: -root.width*5/12
        }
    }
    Text {
        text: "B"
        font.family: fontfam
        font.pointSize: 16
        color: "white"
        anchors {
            top: ab_path.bottom
            topMargin: 5
            horizontalCenter: ab_path.horizontalCenter
            horizontalCenterOffset: +root.width*5/12
        }
    }
    Rectangle {
        color: "white"
        width: 2
        height: 10
        //radius: height/2
        anchors {
            verticalCenter: ab_path.verticalCenter
            horizontalCenter: ab_path.horizontalCenter
            horizontalCenterOffset: +root.width*5/12
        }
    }
    Shape {
        id: marker
        width: 25
        height: width*Math.sqrt(3)/2
        anchors.bottom: ab_path.top
        antialiasing: true
        smooth: true
        ShapePath {
            fillColor: (value > 0) && (value < 1) ? "#ffffff" :"#ff0000"
            strokeColor: "transparent"
            startX: value_norm*root.width*10/12+root.width*1/12; startY: marker.width*Math.sqrt(3)/2
            PathLine { x: value_norm*root.width*10/12+root.width*1/12-marker.width/2; y: 0 }
            PathLine { x: value_norm*root.width*10/12+root.width*1/12+marker.width/2; y: 0 }
            PathLine { x: value_norm*root.width*10/12+root.width*1/12; y: marker.width*Math.sqrt(3)/2 }
        }
    }
}
