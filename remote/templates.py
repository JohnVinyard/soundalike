import urlparse

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Soundalike</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script type="text/javascript">
        $(function() {{

            $('.spectrogram img').click(function() {{
                $(this).siblings('audio')[0].play();
            }});

            function isScrolledIntoView(elem)
            {{
                var docViewTop = $(window).scrollTop();
                var docViewBottom = docViewTop + $(window).height();

                var elemTop = $(elem).offset().top;
                var elemBottom = elemTop + $(elem).height();

                return elemTop <= docViewBottom;
            }}

            function loadResults() {{
                $('.search-result').not('.loaded').each(function(index) {{
                    var elem = $(this).get(0);
                    if(isScrolledIntoView(elem)) {{
                        $(this)
                            .find('audio, .spectrogram img')
                            .attr('src', function() {{
                                return $(this).attr('data-src');
                            }});
                        $(this).addClass('loaded');
                    }}
                }});
            }}

            loadResults();
            $(window).scroll(loadResults);
        }});
    </script>
    <style type="text/css">
        body {{
            font-family: Sans-serif;
            color: #333;
            background-color: #f2eee2;
            padding:0;
            border:0;
            margin:0;
        }}
        header, footer {{
            background-color: #43c0f6;
            color: #f2eee2;
            padding: 20px;
        }}
        header {{
            position: fixed;
            width:100%;
            z-index:9999;
            top: 0;
            font-weight:1000;

        }}
        header button {{
            float: right;
            margin-right:40px;
        }}
        main {{
            padding: 20px;
        }}
        a {{
            color: #f81b84;
        }}
        ul.search-results {{
            margin-top: 60px;
            list-style: none;
            padding:0;
        }}
        .search-result-item {{
            padding: 10px;
            margin-bottom: 10px;
            background-color: #f8f7e8;
            border-bottom: solid 2px #ddd;
        }}
        .spectrogram img {{
            cursor: pointer;
        }}
        .spectrogram {{
            background-color: #fcfbf2;
            border-top: solid 1px: #eee;
            border-bottom: solid 1px #eee;
            padding: 10px;
        }}
        #no-results {{
            text-align: center;
            margin-top:50px;
        }}
    </style>
  </head>
  <body>
    <header>Soundalike <button><a href="{random_search}">Random Search</button</a></header>
    <main>
        <ul class="search-results">
            {items}
        </ul>
    </main>
  </body>
</html>
'''

ITEM_TEMPLATE = '''
<li class="search-result-item">
    <div class="search-result">
        <h3><a href={web_url}>{origin}</a></h3>
        <div class="spectrogram">
            <img data-src={bark} height=200 />
            <audio data-src={audio} tabindex={tabindex}></audio>
        </div>
        <div>from {start:.2f} to {end:.2f} seconds</div>
        <ul>
            <li><a href="{search}">similar to this</a></li>
            <li><a href={_id}>download</a></li>
        </ul>
    </div>
</li>
'''

NO_RESULTS_TEMPLATE = '''
<div id="no-results"><h3>No Results</h3></div>
'''


def item_template(args):
    i, data = args
    parsed = urlparse.urlparse(data['web_url'])
    data['origin'] = parsed.netloc
    return ITEM_TEMPLATE.format(
        tabindex=i + 1, **dict(**data))


def render_html(results, end, random_search):
    items = ''.join(map(item_template, enumerate(results)))
    if not items:
        items = NO_RESULTS_TEMPLATE
    return HTML_TEMPLATE.format(**locals())
