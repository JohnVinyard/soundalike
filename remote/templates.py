import urlparse

file_cache = dict()


def load_file(relative_path):
    with open(relative_path, 'r') as f:
        return f.read()


def get_file_contents(relative_path):
    try:
        return file_cache[relative_path]
    except KeyError:
        contents = load_file(relative_path)
        file_cache[relative_path] = contents
        return contents


def item_template(args):
    i, data = args
    parsed = urlparse.urlparse(data['web_url'])
    data['origin'] = parsed.netloc
    template = get_file_contents('static/templates/result.html')
    return template.format(
        tabindex=i + 1, **dict(**data))


def render_html(results, end, random_search):
    main = get_file_contents('static/templates/main.html')
    js = get_file_contents('static/main.js')
    css = get_file_contents('static/main.css')
    items = ''.join(map(item_template, enumerate(results)))
    if not items:
        items = get_file_contents(
            'static/templates/no_results.html')
    return main.format(**locals())
