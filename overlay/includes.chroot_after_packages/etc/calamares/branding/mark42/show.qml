import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation
    Timer { interval: 15000; running: presentation.activatedInCalamares; repeat: true
            onTriggered: presentation.goToNextSlide() }

    function onActivate() { }
    function onLeave() { }

    Rectangle { anchors.fill: parent; color: "#0c111a"; z: -1 }

    Slide {
        Image { id: s1; source: "slide1.png"; width: 640; height: 288
                fillMode: Image.PreserveAspectFit; anchors.centerIn: parent }
        Text { anchors.horizontalCenter: s1.horizontalCenter; anchors.top: s1.bottom; anchors.topMargin: 12
               width: 600; wrapMode: Text.WordWrap; horizontalAlignment: Text.Center; color: "#e8e8e8"
               text: "Full Debian 13 core. Every apt, dpkg and systemctl command works exactly as on Debian." }
    }
    Slide {
        Image { id: s2; source: "slide2.png"; width: 640; height: 288
                fillMode: Image.PreserveAspectFit; anchors.centerIn: parent }
        Text { anchors.horizontalCenter: s2.horizontalCenter; anchors.top: s2.bottom; anchors.topMargin: 12
               width: 600; wrapMode: Text.WordWrap; horizontalAlignment: Text.Center; color: "#e8e8e8"
               text: "Full hardware access: firmware, microcode, kernel headers and build tools included." }
    }
    Slide {
        Image { id: s3; source: "slide3.png"; width: 640; height: 288
                fillMode: Image.PreserveAspectFit; anchors.centerIn: parent }
        Text { anchors.horizontalCenter: s3.horizontalCenter; anchors.top: s3.bottom; anchors.topMargin: 12
               width: 600; wrapMode: Text.WordWrap; horizontalAlignment: Text.Center; color: "#e8e8e8"
               text: "Clean KDE Plasma in graphite and arc-reactor blue. Change anything in System Settings." }
    }
}
