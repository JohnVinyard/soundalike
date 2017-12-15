
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>title</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script type="text/javascript">
        $(function() {{
            $('.spectrogram').click(function() {{
                $(this).siblings('audio')[0].play();
            }});
        }});
    </script>
    <link
        rel="stylesheet"
        href="https://unpkg.com/purecss@1.0.0/build/pure-min.css"
        integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w"
        crossorigin="anonymous">
  </head>
  <body>
    <h1>{did_initialize}</h1>
    <h1>{end}</h1>
    <h2><a href="{random_search}">{random_search}</a></h2>
    <ul>
        {items}
    </ul>
  </body>
</html>
'''

ITEM_TEMPLATE = '''
<li>
    <div>
        <h3><a href={_id}>{_id}</a></h3>
        <div>{start} - {end}</div>
        <div>
            <a href="{search}">{search}</a>
        </div>
        <img class="spectrogram" src={bark} height=200 />
        <img src={hashed} height=200 width=200 />
        <br/>
        <audio src={audio} controls tabindex={tabindex} />
        <hr>
    </div>
</li>
'''


def item_template(args):
    i, template = args
    return ITEM_TEMPLATE.format(tabindex=i + 1, **template)


def render_html(results, did_initialize, end, random_search):
    items = ''.join(map(item_template, enumerate(results)))
    return HTML_TEMPLATE.format(**locals())