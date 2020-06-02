#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlComponent>
#include <QSurfaceFormat>
#include <QDebug>

int main(int argc, char *argv[])
{
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QGuiApplication app(argc, argv);

    //сглаживание
    QSurfaceFormat format;
    format.setSamples(10);
    QSurfaceFormat::setDefaultFormat(format);

    QQmlApplicationEngine engine;
    const QUrl url(QStringLiteral("qrc:/main.qml"));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreated,
                     &app, [url](QObject *obj, const QUrl &objUrl) {
        if (!obj && url == objUrl)
            QCoreApplication::exit(-1);
    }, Qt::QueuedConnection);

    /// This isn't needed if QQmlComponent::create invoked
    //    engine.load(url);

    QQmlComponent comp(&engine, url);
    QObject* pobj = comp.create();

    QObject* speed = pobj->findChild<QObject*>("speed");
    QObject* acc = pobj->findChild<QObject*>("acceleration");
    QObject* dec = pobj->findChild<QObject*>("deceleration");
    QObject* pos = pobj->findChild<QObject*>("position");

    speed->setProperty("value", 0.9); // 0-1.0
    acc->setProperty("value", 0.0); // 0-1.0
    dec->setProperty("value", 0.7); // 0-1.0
    pos->setProperty("value", -8); // 0-1.0

    //настройки конечных точек
    QObject* endpoints = pobj->findChild<QObject*>("endpoints"); //активация
    QObject* endpoints_stop = pobj->findChild<QObject*>("endpoints_stop"); //останов
    QObject* endpoints_revers = pobj->findChild<QObject*>("endpoints_revers"); //реверс
    //условия останова
    QObject* impact = pobj->findChild<QObject*>("impact_sensor");
    QObject* ultrasound = pobj->findChild<QObject*>("ultrasound_sensor");
    // при потере связи
    QObject* lost_stop = pobj->findChild<QObject*>("lost_stop");
    QObject* lost_home = pobj->findChild<QObject*>("lost_home");
    // время потери связи
    QObject* lost_time = pobj->findChild<QObject*>("lost_time");

    qDebug() << endpoints->property("checked");
    qDebug() << lost_time->property("value");

    return app.exec();
}
