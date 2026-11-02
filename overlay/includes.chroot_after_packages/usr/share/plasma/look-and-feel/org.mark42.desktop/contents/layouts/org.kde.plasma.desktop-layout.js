// MARK 42 default desktop layout (Plasma 6)
// Clean v1.2: thin solid top bar + floating solid icon dock.

// ---- wallpaper on every desktop ----
var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    var d = desktopsArray[j];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/MARK42/");
    d.writeConfig("FillMode", 2);
}

// ---- top bar ----
var top = new Panel;
top.location = "top";
top.height = 2 * Math.floor(gridUnit * 1.7 / 2);
top.floating = false;
top.opacity = "opaque";

var menu = top.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "mark42");
menu.writeConfig("switchCategoryOnHover", true);

top.addWidget("org.kde.plasma.panelspacer");

var clock = top.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateFormat", "shortDate");
clock.writeConfig("dateDisplayFormat", 1);   // date beside time

top.addWidget("org.kde.plasma.panelspacer");
top.addWidget("org.kde.plasma.systemtray");
top.addWidget("org.kde.plasma.lock_logout");

// ---- floating dock ----
var dock = new Panel;
dock.location = "bottom";
dock.height = 2 * Math.floor(gridUnit * 2.8 / 2);
dock.lengthMode = "fit";
dock.alignment = "center";
dock.floating = true;
dock.hiding = "dodgewindows";
dock.opacity = "opaque";

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:firefox-esr.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:libreoffice-writer.desktop",
    "applications:vlc.desktop",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
]);
tasks.writeConfig("showOnlyCurrentDesktop", false);
tasks.writeConfig("iconSpacing", 1);
