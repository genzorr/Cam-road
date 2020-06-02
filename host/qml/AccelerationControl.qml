import QtQuick 2.12
import QtGraphicalEffects 1.0


Item {
    id: root

    property int size: 450
    property int prgWidth: 15
    property real value: 0
    property int txtsize: 16
    property color txtcolor: "white"
    property string caption: ""
    property string direction: "right"

    implicitWidth: size
    implicitHeight: size

    onValueChanged: {
        canvas.alpha = value * 110;
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
            var radius = root.size/2 - 2*root.prgWidth;

            var startAngle; var fullAngle; var prgAngle; var step; var ang;
            var gradient = ctx.createConicalGradient(width/2, width/2, (Math.PI/180)*270);

            ctx.reset();

            function drawTextAlongArc(context, str, centerX, centerY, radius, angle, sparse) {
                context.save();
                context.translate(centerX, centerY);
                var ang = angle - (Math.PI/180) * sparse *str.length/2;
                context.rotate(ang);
                for (var n = 0; n < str.length; n++) {
                    context.save();
                    context.translate(0, -radius);
                    var char1 = str[n];
                    context.fillText(char1, 0, 0);
                    context.restore();
                    context.rotate((Math.PI/180) * sparse);
                }
                context.restore();
            }
            ctx.fillStyle = txtcolor;
            ctx.textAlign = "center";
            ctx.font="normal "+txtsize.toString()+"px 'Calibri'";

            if (direction == "right") { // ускорение
                drawTextAlongArc(ctx, caption, x, y, radius+root.prgWidth, Math.PI/3, 4);
                ctx.fillText("MIN", x + (radius+root.prgWidth/2)*Math.cos(38*Math.PI/180),
                                    y + (radius+root.prgWidth/2)*Math.sin(38*Math.PI/180));
                ctx.stroke();

                startAngle = (Math.PI/180) * 280;
                fullAngle = (Math.PI/180) * (360+30);
                prgAngle = fullAngle - alpha*(Math.PI/180);
                step = -(Math.PI/180) * 1;
                gradient.addColorStop(60/360, "#03ff81");
                gradient.addColorStop(115/360, "#0062ff");
                gradient.addColorStop(170/360, "#9500ff");

                ang = fullAngle;
                while (ang > prgAngle) {
                    ctx.beginPath();
                    ctx.lineWidth = root.prgWidth*(fullAngle-ang)/(fullAngle-startAngle);
                    ctx.arc(x, y, radius, ang + step, ang);
                    ctx.strokeStyle = gradient;
                    ctx.stroke();
                    ang = ang+2.5*step;
                }
            }
            else { //замедление
                drawTextAlongArc(ctx, caption, x, y, radius+root.prgWidth, -Math.PI/3, 4);
                ctx.fillText("MIN", x - (radius+root.prgWidth/2)*Math.cos(38*Math.PI/180),
                                    y + (radius+root.prgWidth/2)*Math.sin(38*Math.PI/180));
                ctx.stroke();

                startAngle = (Math.PI/180) * 150;
                fullAngle = (Math.PI/180) * 260;
                prgAngle = startAngle + alpha*(Math.PI/180);
                step = (Math.PI/180) * 1;

                gradient.addColorStop(190/360, "#9500ff");
                gradient.addColorStop(245/360, "#0062ff");
                gradient.addColorStop(300/360, "#03ff81");

                ang = startAngle;
                while (ang < prgAngle) {
                    ctx.beginPath();
                    ctx.lineWidth = root.prgWidth*(ang-startAngle)/(fullAngle-startAngle);
                    ctx.arc(x, y, radius, ang, ang + step);
                    ctx.strokeStyle = gradient;
                    ctx.stroke();
                    ang = ang+2.5*step;
                }
            }
            ctx.textAlign = "center";
            ctx.fillText("MAX", x ,root.prgWidth*2) ;
            ctx.stroke();
        }

        Behavior on alpha {
            NumberAnimation {
                duration: 500
            }
        }
    }
}
