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

function isScrolledIntoView(elem)
{
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();

    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();

    return elemTop <= docViewBottom;
}

$(function() {

    $('.spectrogram img').click(function() {
        $(this).siblings('audio')[0].play();
    });

    function loadResults() {
        $('.search-result').not('.loaded').each(function(index) {
            var elem = $(this).get(0);
            if(isScrolledIntoView(elem)) {
                $(this)
                    .find('audio, .spectrogram img')
                    .attr('src', function() {
                        return $(this).attr('data-src');
                    });
                $(this).addClass('loaded');
            }
        });
    }

    loadResults();
    $(window).scroll(loadResults);
});