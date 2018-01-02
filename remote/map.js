
var pendingRequests = [];

function SoundalikeClient() {

    this.fetchBinary = function(url) {
        return new Promise(function(resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', url);
            xhr.responseType = 'arraybuffer';
            xhr.onload = function() {
                if(this.status >= 200 && this.status < 300) {
                    resolve(xhr.response);
                } else {
                    reject(this.status, xhr.statusText);
                }
            };
            xhr.onerror = function() {
                reject(this.status, xhr.statusText);
            };
            xhr.send();
            pendingRequests.push(xhr);
        });
    };

    this.fetchAudio = function(url, context) {
        return this
            .fetchBinary(url)
            .then(function(data) {
                return new Promise(function(resolve, reject) {
                    context.decodeAudioData(data, function(buffer) {
                        resolve(buffer);
                    });
                });
            });
    }
}


var map;
var markers = [];

var soundalikeClient = new SoundalikeClient();
var context = new AudioContext();

function clearPoints() {
    markers.forEach(function(marker) { marker.setMap(null); });
    pendingRequests.forEach(function(req) { req.abort(); });
    markers = [];
    pendingRequests = [];
}

function loadPoints() {

    clearPoints();
    var bounds = map.getBounds();
    if(!bounds) { return; }
    console.log(bounds);

    var ne = bounds.getNorthEast();
    var sw = bounds.getSouthWest();
    console.log(ne, sw);

    var topLeft = `${ne.lat()}|${sw.lng()}`;
    var bottomRight = `${sw.lat()}|${ne.lng()}`;
    var queryData = {top_left: topLeft, bottom_right: bottomRight};

    $.getJSON('/map', queryData).then(function(data) {
        data.results.forEach(function(result) {
            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(
                    result.location[0], result.location[1]),
                map: map
            });
            markers.push(marker);
            soundalikeClient
                .fetchAudio(result.audio_uri, context)
                .then(function(audio) {
                    marker.addListener('click', function() {
                        var source = context.createBufferSource();
                        source.buffer = audio;
                        source.connect(context.destination);
                        source.start(0);
                    });
                });
        });
    });
}

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 2,
        center: new google.maps.LatLng(2.8, -187.3),
        mapTypeId: 'terrain'
    });

    window.map = map;

    map.addListener('idle', function() {
        loadPoints();
    });
}

$(function() {

    var resp = $
        .getJSON('/map')
        .then(function(data) {
            addPoints(data, soundalikeClient, audioContext);
        });
});