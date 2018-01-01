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



function addPoints(data, client, context) {
    // get the minimum, maximum, and span of both dimensions
    var xMin = 0;
    var xMax = 0;
    var yMin = 0;
    var yMax = 0;

    for(var i = 0; i < data.results.length; i++) {
        var x = data.results[i].location[0];
        var y = data.results[i].location[1];
        if(x < xMin) { xMin = x; }
        if(x > xMax) { xMax = x; }
        if(y < yMin) {yMin = y; }
        if(y > yMax) { yMax = y; }
    }

    var xSpan = xMax - xMin;
    var ySpan = yMax - yMin;

    $('#main').attr({
        'viewBox': `${xMin} ${yMin} ${xSpan} ${ySpan}`,
        'preserveAspectRatio': "none"
    })

    var transformed = data.results;

    $('#main').empty();

    transformed.forEach(function(result) {
        var cx = result.location[0];
        var cy = result.location[1];
        var r = 10;
        var circle = document
            .createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', result.location[0]);
        circle.setAttribute('cy', result.location[1]);
        circle.setAttribute('r', 1);
        $('#main').append(circle);

        client
            .fetchAudio(result.audio_uri, context)
            .then(function(audio) {
                $(circle).click(function() {
                    var source = context.createBufferSource();
                    source.buffer = audio;
                    source.connect(context.destination);
                    source.start(0);
                });
            });
    });
}

$(function() {
    var soundalikeClient = new SoundalikeClient();
    var audioContext = new AudioContext();
    var resp = $
        .getJSON('/map')
        .then(function(data) {
            addPoints(data, soundalikeClient, audioContext);
        });
});