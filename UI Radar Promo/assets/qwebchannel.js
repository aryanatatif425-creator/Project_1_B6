"use strict";
var QWebChannelMessageTypes = {
    signal: 1,
    propertyUpdate: 2,
    init: 3,
    idle: 4,
    debug: 5,
    invokeMethod: 6,
    connectToSignal: 7,
    disconnectFromSignal: 8,
    setProperty: 9,
    response: 10,
};
var QWebChannel = function(transport, initCallback) {
    if (typeof transport !== "object" || typeof transport.send !== "function") {
        console.error("QWebChannel expects transport with send and onmessage");
        return;
    }
    var channel = this;
    this.transport = transport;
    this.send = function(data) {
        if (typeof data !== "string") data = JSON.stringify(data);
        channel.transport.send(data);
    };
    this.transport.onmessage = function(message) {
        var data = message.data;
        if (typeof data === "string") data = JSON.parse(data);
        switch (data.type) {
            case QWebChannelMessageTypes.signal: channel.handleSignal(data); break;
            case QWebChannelMessageTypes.response: channel.handleResponse(data); break;
            case QWebChannelMessageTypes.propertyUpdate: channel.handlePropertyUpdate(data); break;
            default: console.error("invalid message:", message.data); break;
        }
    };
    this.execCallbacks = {};
    this.execId = 0;
    this.exec = function(data, callback) {
        if (!callback) { channel.send(data); return; }
        if (data.hasOwnProperty("id")) { console.error("exec with id"); return; }
        data.id = this.execId++;
        this.execCallbacks[data.id] = callback;
        this.send(data);
    };
    this.objects = {};
    this.handleSignal = function(message) {
        var obj = channel.objects[message.object];
        if (obj) obj.signalEmitted(message.signal, message.args);
    };
    this.handleResponse = function(message) {
        if (!message.hasOwnProperty("id")) return;
        this.execCallbacks[message.id](message.data);
        delete this.execCallbacks[message.id];
    };
    this.handlePropertyUpdate = function(message) {
        for (var i in message.data) {
            var d = message.data[i];
            var obj = channel.objects[d.object];
            if (obj) obj.propertyUpdate(d.signals, d.properties);
        }
        channel.exec({type: QWebChannelMessageTypes.idle});
    };
    channel.exec({type: QWebChannelMessageTypes.init}, function(data) {
        for (var n in data) new QObject(n, data[n], channel);
        for (var n in channel.objects) channel.objects[n].unwrapProperties();
        if (initCallback) initCallback(channel);
        channel.exec({type: QWebChannelMessageTypes.idle});
    });
};
function QObject(name, data, webChannel) {
    this.__id__ = name;
    webChannel.objects[name] = this;
    this.__objectSignals__ = {};
    this.__propertyCache__ = {};
    var object = this;
    this.unwrapQObject = function(response) {
        if (response instanceof Array) {
            var ret = new Array(response.length);
            for (var i = 0; i < response.length; ++i) ret[i] = object.unwrapQObject(response[i]);
            return ret;
        }
        if (!response || !response["__QObject*__"] || response.id === undefined) return response;
        var id = response.id;
        if (webChannel.objects[id]) return webChannel.objects[id];
        if (!response.data) { console.error("unwrap error", id); return; }
        var q = new QObject(id, response.data, webChannel);
        q.destroyed.connect(function() { delete webChannel.objects[id]; });
        q.unwrapProperties();
        return q;
    };
    this.unwrapProperties = function() {
        for (var p in object.__propertyCache__) object.__propertyCache__[p] = object.unwrapQObject(object.__propertyCache__[p]);
    };
    function addSignal(sd, isProp) {
        var sname = sd[0], sidx = sd[1];
        object[sname] = {
            connect: function(cb) {
                object.__objectSignals__[sidx] = object.__objectSignals__[sidx] || [];
                object.__objectSignals__[sidx].push(cb);
                if (!isProp && sname !== "destroyed") webChannel.exec({type: QWebChannelMessageTypes.connectToSignal, object: object.__id__, signal: sidx});
            },
            disconnect: function(cb) {
                var arr = object.__objectSignals__[sidx] || [];
                var idx = arr.indexOf(cb);
                if (idx !== -1) arr.splice(idx, 1);
                if (!isProp && arr.length === 0) webChannel.exec({type: QWebChannelMessageTypes.disconnectFromSignal, object: object.__id__, signal: sidx});
            }
        };
    }
    this.propertyUpdate = function(sigs, pmap) {
        for (var p in pmap) object.__propertyCache__[p] = pmap[p];
        for (var s in sigs) {
            var cbs = object.__objectSignals__[s];
            if (cbs) cbs.forEach(function(cb) { cb.apply(cb, sigs[s]); });
        }
    };
    this.signalEmitted = function(sname, sargs) {
        var cbs = object.__objectSignals__[sname];
        if (cbs) cbs.forEach(function(cb) { cb.apply(cb, sargs); });
    };
    function addMethod(md) {
        var mname = md[0], midx = md[1];
        object[mname] = function() {
            var args = [], cb;
            for (var i = 0; i < arguments.length; ++i) {
                if (typeof arguments[i] === "function") cb = arguments[i];
                else args.push(arguments[i]);
            }
            webChannel.exec({type: QWebChannelMessageTypes.invokeMethod, object: object.__id__, method: midx, args: args}, function(r) {
                if (r !== undefined) {
                    var res = object.unwrapQObject(r);
                    if (cb) cb(res);
                }
            });
        };
    }
    function bindGS(pi) {
        var pname = pi[1], psig = pi[2];
        object.__propertyCache__[pi[0]] = pi[3];
        if (psig) {
            if (psig[0] === 1) psig[0] = pname + "Changed";
            addSignal(psig, true);
        }
        Object.defineProperty(object, pname, {
            configurable: true,
            get: function() { return object.__propertyCache__[pi[0]]; },
            set: function(v) {
                if (v === undefined) { console.warn("undefined set", pname); return; }
                object.__propertyCache__[pi[0]] = v;
                webChannel.exec({type: QWebChannelMessageTypes.setProperty, object: object.__id__, property: pi[0], value: v});
            }
        });
    }
    data.methods.forEach(addMethod);
    data.properties.forEach(bindGS);
    data.signals.forEach(function(s) { addSignal(s, false); });
    for (var e in data.enums) object[e] = data.enums[e];
}
if (typeof module === "object") module.exports = { QWebChannel: QWebChannel };