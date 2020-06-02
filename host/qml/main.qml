import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import QtQuick.Controls.Material 2.3

ApplicationWindow {
    id: root
    visible: true
    width: 480
    height: 800
    title: qsTr("CableControl")
    background: Image {
        id: bcg
        source: "qrc:/CableControl_bg.jpg"
    }

    header: ToolBar { //тулбар с виджетами батареи и индикацией связи
        height: Math.max(root.height/20, 40)
        background: Rectangle {
            id: toolbar_bg
            color: "#0d0d0d"
            visible: true
        }
        RowLayout {
            anchors.fill: parent
            anchors.margins: header.height/4

            BatteryProgress { //батарея канатки (input value 0-1.0)
                id: cable_battery
                value: 0.5
                height: header.height/2; width: height*2;
                bgcolor: "transparent"
                prmcolor: "white"
            }

            Rectangle {
                id: connection
                height: header.height/2

                Text { // частота связи
                    id: frq
                    text: "133.2 kHz"
                    font.family: "Calibri"
                    font.pixelSize:Math.max(20,root.height/40)
                    font.bold: true
                    color: "#ffffff"
                    anchors.right: clvl.left
                    anchors.baseline: clvl.bottom
                    anchors.rightMargin: header.height/4
                    height: header.height/2
                }
                ConnectionLevel { // уровень связи (input value 0-1.0)
                    id: clvl
                    value: 0.5
                    height: header.height/2
                    width: height*1.5
                }
            }

            BatteryProgress { //батарея пульта (input value 0-1.0)
                id: control_battery
                value:0.7
                height: header.height/2; width: height*2;
                bgcolor: "transparent"
                prmcolor: "white"
                Layout.alignment: Qt.AlignRight
            }
        }
    }

    ColumnLayout {
    anchors.fill: parent
        TabBar { // вкладки "Работа", "Настройки", "Отчеты"
            id: tabBar
            width: parent.width
            Layout.alignment: Qt.AlignTop
            background: Rectangle {
                color: "transparent"
            }

            Repeater {
                    model: ["Работа", "Настройки", "Отчеты"]

                TabButton {
                    height: Math.max(root.height/20, 40); width: root.width/3
                    background: Rectangle {
                        color: "#30004466"
                    }
                    contentItem: Text {
                        text: modelData
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: tabBar.currentIndex === index ? 16 : 15
                        font.bold: tabBar.currentIndex === index ? true : false
                    }
                    Rectangle {
                        anchors.bottom: parent.bottom
                        color: "white"
                        height: 2
                        width: parent.width
                        visible: tabBar.currentIndex === index ? true : false
                    }
                }
            }
        }

        StackLayout {
            id: content
            currentIndex: tabBar.currentIndex
            Layout.fillHeight: true
            Item { // вкладка "Работа"
                id: controlTab
                SpeedControl { // скорость (input value 0-1.0)
                    id: speed
                    objectName: "speed"
                    value: 0.5
                    size: Math.min(root.width*0.67, root.height*0.4)
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: 80
                }

                AccelerationControl { // замедление (input value 0-1.0)
                    id: acc
                    objectName: "deceleration"
                    value: 0.5
                    size: speed.size*1.4
                    direction: "left"
                    caption: "ЗАМЕДЛЕНИЕ"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: speed.verticalCenter
                }

                AccelerationControl { // ускорение (input value 0-1.0)
                    id: dec
                    objectName: "acceleration"
                    value: 0.5
                    size: speed.size*1.4
                    direction: "right"
                    caption: "УСКОРЕНИЕ"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: speed.verticalCenter
                }

                PositionControl { // положение (input value 0-1.0)
                    id: pos
                    objectName: "position"
                    value: 0.5
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: speed.bottom
                    anchors.topMargin: 120
                }
            }
            Item { // вкладка "Настройки"
                id: settingsTab
                ButtonGroup { id: endpoints_gr }
                ButtonGroup { id: connection_gr }
                ColumnLayout {
                    anchors.fill: parent
                    Rectangle {
                        id: set1
                        color: "#30004466"
                        border.color: "#50ffffff"
                        height: 130; width: 0.85*root.width;
                        Layout.alignment: Qt.AlignHCenter
                        Column {
                            spacing: 20
                            leftPadding: 0.1*parent.width
                            topPadding: 20
                            width: 0.8*parent.width; height: parent.height
                            anchors.fill: parent
                            CustomCheckBox {
                                id: set1_chbox
                                objectName: "endpoints"
                                checked: true
                                text: qsTr("Активация конечных точек")
                            }
                            Row {
                                spacing: 30
                                CustomRadioButton {
                                    objectName: "endpoints_stop"
                                    checked: true
                                    text: qsTr("Останов")
                                    enabled: set1_chbox.checked
                                    ButtonGroup.group: endpoints_gr
                                }
                                CustomRadioButton {
                                    objectName: "endpoints_revers"
                                    checked: true
                                    text: qsTr("Реверс")
                                    enabled: set1_chbox.checked
                                    ButtonGroup.group: endpoints_gr
                                }
                            }
                        }
                    }
                    Rectangle {
                        id: set2
                        color: "#30004466"
                        border.color: "#50ffffff"
                        height: 190; width: 0.85*root.width;
                        Layout.alignment: Qt.AlignHCenter
                        Column {
                            spacing: 20
                            leftPadding: 0.1*parent.width
                            topPadding: 20
                            anchors.fill: parent
                            Text {
                                text: qsTr("Условия останова:")
                                font.family: "Calibri Solid Italic"
                                font.pointSize: 12
                                color: "white"
                            }
                            CustomCheckBox {
                                objectName: "impact_sensor"
                                text: qsTr("Останов по датчику удара")
                            }
                            CustomCheckBox {
                                objectName: "ultrasound_sensor"
                                text: qsTr("Останов по УЗ датчику")
                            }
                        }
                    }
                    Rectangle {
                        id: set3
                        color: "#30004466"
                        border.color: "#50ffffff"
                        implicitHeight: 300; width: 0.85*root.width;
                        Layout.alignment: Qt.AlignHCenter
                        Column {
                            spacing: 20
                            leftPadding: 0.1*parent.width
                            topPadding: 20
                            anchors.fill:parent
                            Text {
                                text: qsTr("При потере связи:")
                                font.family: "Calibri Solid Italic"
                                font.pointSize: 12
                                color: "white"
                            }
                            Row {
                                spacing: 30
                                CustomRadioButton {
                                    objectName: "lost_stop"
                                    checked: true
                                    text: qsTr("Останов")
                                    ButtonGroup.group: connection_gr
                                }
                                CustomRadioButton {
                                    objectName: "lost_home"
                                    text: qsTr("Домой")
                                    ButtonGroup.group: connection_gr
                                }
                            }
                            Text {
                                text: qsTr("Время потери связи (сек):")
                                font.family: "Calibri Solid Italic"
                                font.pointSize: 12
                                color: "white"
                            }
                            CustomSlider {
                                objectName: "lost_time"
                                id: connection_time
                                from: 1
                                to: 10
                                value: 4
                                stepSize: 1
                                width: 0.85*root.width*0.8
                            }
                        }
                    }
                }
            }
            Item { // вкладка "Отчеты"
                id: reportsTab
            }
        }
    }
}
