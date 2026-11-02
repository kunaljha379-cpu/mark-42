/*  MARK 42 login splash (Plasma 6)
 *  Clean v1.2: slow rotating rings + logo, no glow or text. */
import QtQuick
import org.kde.kirigami 2 as Kirigami

Rectangle {
    id: root
    color: "#000000"

    property int stage

    // Plasma drives stage 0..6; fade the content in near the start and out at
    // the end so the splash opens and closes smoothly.
    onStageChanged: {
        if (stage == 2) {
            introAnimation.running = true;
        } else if (stage == 6) {
            outroAnimation.running = true;
        }
    }

    OpacityAnimator {
        id: outroAnimation
        running: false
        target: content
        from: 1
        to: 0
        duration: Kirigami.Units.veryLongDuration * 2
        easing.type: Easing.InOutQuad
    }

    Item {
        id: content
        anchors.fill: parent
        opacity: 0

        readonly property real size: Math.min(root.width, root.height) * 0.30

        Item {
            id: reactor
            anchors.horizontalCenter: parent.horizontalCenter
            y: parent.height * 0.42 - height / 2
            width: content.size; height: content.size

            Image {
                anchors.centerIn: parent
                width: parent.width * 1.08; height: width
                source: "images/ring_outer.png"
                asynchronous: true
                opacity: 0.8
                RotationAnimator on rotation { from: 0; to: -360; duration: 14000; loops: Animation.Infinite }
            }
            Image {
                anchors.centerIn: parent
                width: parent.width * 0.86; height: width
                source: "images/ring_inner.png"
                asynchronous: true
                opacity: 0.8
                RotationAnimator on rotation { from: 0; to: 360; duration: 10000; loops: Animation.Infinite }
            }
            Image {
                anchors.centerIn: parent
                width: parent.width * 0.82; height: width
                source: "images/logo.png"
                asynchronous: true
                opacity: 0.85
            }
        }

        Image {
            id: title
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: reactor.bottom
            anchors.topMargin: content.size * 0.22
            width: content.size * 0.9
            fillMode: Image.PreserveAspectFit
            source: "images/title.png"
            asynchronous: true
            opacity: 0.9
        }

    }

    OpacityAnimator {
        id: introAnimation
        running: false
        target: content
        from: 0
        to: 1
        duration: Kirigami.Units.veryLongDuration * 2
        easing.type: Easing.InOutQuad
    }
}
