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

    var audioCache = {};

    this.fetchAudio = function(url, context) {
        var cached = audioCache[url];
        if(cached !== undefined) {
            return cached;
        }

        var audioBufferPromise = this
            .fetchBinary(url)
            .then(function(data) {
                return new Promise(function(resolve, reject) {
                    context.decodeAudioData(data, function(buffer) {
                        resolve(buffer);
                    });
                });
            });
         audioCache[url] = audioBufferPromise;
         return audioBufferPromise;
    }
}

function isScrolledIntoView(elem)
{
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();

    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();

    return elemTop <= docViewBottom;
}

$(function() {

    var soundalikeClient = new SoundalikeClient();
    var context = new AudioContext();

    $('.spectrogram img').click(function() {
        $(this).siblings('audio')[0].play();
    });

    function loadResults() {
        $('.search-result').not('.loaded').each(function(index) {
            var elem = $(this).get(0);
            if(!isScrolledIntoView(elem)) { return; }

            var img = $(this)
                .find('.spectrogram img')
                .attr('src', function() {
                    return $(this).attr('data-src');
                });

            var audio = $(this).find('audio');
            var audioSrc = audio.attr('data-src');
            var start = parseFloat(audio.attr('data-start'));
            var duration = parseFloat(audio.attr('data-duration'));

            soundalikeClient
                .fetchAudio(audioSrc, context)
                .then(function(audioBuffer) {
                    img.click(function() {
                        var source = context.createBufferSource();
                        source.buffer = audioBuffer;
                        source.connect(context.destination);
                        source.start(0, start, duration);
                    });
                });

            $(this).addClass('loaded');
        });
    }

    loadResults();
    $(window).scroll(loadResults);
});