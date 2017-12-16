from itertools import repeat, izip

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
            $('.spectrogram').click(function() {{
                $(this).siblings('audio')[0].play();
            }});
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
        main {{
            padding: 20px;
        }}
        a {{
            color: #f81b84;
        }}
        ul {{
            list-style: none;
            padding:0;
        }}
        li {{
            border-bottom: solid 1px #f5ce2b;
            padding: 10px;
            margin-bottom: 10px;
        }}
    </style>
  </head>
  <body>
    <header>Soundalike</header>
    <main>
        <ul>
            {items}
        </ul>
    </main>
    <footer>search completed in {end:.2f}ms</footer>
  </body>
</html>
'''

ITEM_TEMPLATE = '''
<li>
    <div>
        <h3><a href={web_url}>{web_url}</a></h3>
        <h4><a href={_id}>{_id}</a></h4>
        <img class="spectrogram" src={bark} height=200 />
        <div>from {start:.2f} to {end:.2f} seconds</div>
        <br/>
        <audio src={audio} controls tabindex={tabindex}></audio>
        <div>
            <a href="{search}">similar to this</a>
        </div>
        <div>
            <a href="{_id}">source file</a>
        </div>
        <div>
            <a href="{random_search}">random search</a>
        </div>
    </div>
</li>
'''


def item_template(args):
    i, data = args
    result, rs = data
    return ITEM_TEMPLATE.format(
        tabindex=i + 1, **dict(random_search=rs, **result))


def render_html(results, did_initialize, end, random_search):
    rs = repeat(random_search)
    data = izip(results, rs)
    items = ''.join(map(item_template, enumerate(data)))
    return HTML_TEMPLATE.format(**locals())