import QtQuick 2.12
import QtGraphicalEffects 1.0

Item {
    id: root

    property int size: 325
    property int prgWidth: 20
    property real value: 0
    property int txtsize: 16

    property color bgcolor: "black"
    property color txtcolor: "white"

    implicitWidth: size
    implicitHeight: size

    onValueChanged: {
        canvas.alpha = value * 240;
    }

    Rectangle {
        anchors.fill: parent
        radius: width / 2
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {
                position: 0.00;
                color: "#15c1e7fa";
            }
            GradientStop {
                position: 1.00;
                color: "#30004466";
            }
        }
        Rectangle {
            width: root.width * 0.5
            height: width * 0.5
            radius: width * 0.5
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop {
                    position: 0.00;
                    color: "#157a8f99";
                }
                GradientStop {
                    position: 1.00;
                    color: "#301a2b33";
                }
            }
            Text {
                text: parseInt(root.value * 100) + "%"
                font.family: "Calibri Solid Italic"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: root.txtsize*2
                color: root.txtcolor
            }
        }
        Text {
            text: "СКОРОСТЬ"
            font.family: "Harlow Solid Italic"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: parent.height/10
            anchors.bottom: parent.bottom
            font.pointSize: root.txtsize+2
            color: root.txtcolor
        }
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        property real alpha: 0

        onAlphaChanged: {
            requestPaint();
        }

        onPaint: {
            var ctx = getContext("2d");

            var x = root.width/2;
            var y = root.width/2;
            var radius = root.size/2 - root.prgWidth
            var startAngle = (Math.PI/180) * 150;
            var fullAngle = (Math.PI/180) * (360+30);
            var prgAngle = (Math.PI/180) * (alpha + 150);

            //градиент
            var gradient = ctx.createConicalGradient(width/2, width/2, (Math.PI/180)*270);
            gradient.addColorStop(60/360, "#9500ff");
            gradient.addColorStop(180/360, "#0062ff");
            gradient.addColorStop(300/360, "#03ff81")

            ctx.reset()
            ctx.lineWidth = root.prgWidth;

            //фон шкалы скорости
            ctx.beginPath();
            ctx.arc(x, y, radius, startAngle, fullAngle);
            ctx.strokeStyle = "#50c1e7fa";
            ctx.stroke();

            //градиент скорости
            ctx.beginPath();
            ctx.arc(x, y, radius, startAngle, prgAngle);
            ctx.strokeStyle = gradient;
            ctx.stroke();

            // шкала
            var ang = startAngle;
            var i = 0;
            while (ang <= fullAngle) {
                var innerX = x + (radius-root.prgWidth/2) * Math.cos(ang);
                var innerY = y + (radius-root.prgWidth/2) * Math.sin(ang);
                var outerX = x + (radius+root.prgWidth/2) * Math.cos(ang);
                var outerY = y + (radius+root.prgWidth/2) * Math.sin(ang);
                ctx.lineWidth = root.prgWidth/10;
                ctx.beginPath();
                ctx.moveTo(innerX,innerY);
                ctx.lineTo(outerX,outerY);
                ctx.strokeStyle = txtcolor
                ctx.stroke();
                // подписи шкалы
                ctx.fillStyle = txtcolor;
                ctx.textAlign = "center";
                ctx.font="normal "+txtsize.toString()+"px 'Calibri'";
                ctx.fillText(i.toString(), x + (radius-1.5*root.prgWidth) * Math.cos(ang),
                                         y + 5 + (radius-1.5*root.prgWidth) * Math.sin(ang));
                ctx.stroke();
                ang = ang + 24*(Math.PI/180)
                i = i+10;
            }
        }
        Behavior on alpha {
            NumberAnimation {
                duration: 500
            }
        }
    }
}
