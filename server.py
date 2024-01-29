import json
import pickle
from collections import defaultdict, Counter
from datetime import datetime
from VisitTracker import VisitTracker
from aiohttp import web
from jinja2 import Environment, FileSystemLoader, select_autoescape


def defaultdict_decoder(dct):
    if isinstance(dct, dict):
        decoded_dict = {}
        for k, v in dct.items():
            try:
                k = int(k)
            except ValueError:
                pass
            if isinstance(v, dict):
                decoded_dict[k] = defaultdict(
                    lambda: defaultdict(lambda: defaultdict(Counter)),
                    v)
            else:
                decoded_dict[k] = v
        return decoded_dict
    return dct


async def handle(request):
    ip = request.remote
    current_time = datetime.now()

    try:
        with open('stats.json', 'r') as f:
            stats = json.load(f, object_hook=defaultdict_decoder)
    except FileNotFoundError:
        stats = defaultdict(lambda: defaultdict(
            lambda: defaultdict(lambda: defaultdict(Counter))))
    tracker = VisitTracker(stats)
    # with open('stats.pickle', 'wb') as f:
    # pickle.dump(tracker.stats, f)
    tracker.update(current_time, ip)
    with open('stats.json', 'w') as f:
        json.dump(stats, f, default=lambda o:
        {int(k): v for k, v in o.items()}, ensure_ascii=False,indent=4)


    statistics = '\n'.join(f"{key}: {value}"
                           for key, value in tracker.stats.items())
    try:
        statistics_date = current_time  # datetime(2022, 1, 1)
        output = (template
                  .render(date=statistics_date,
                          statistics=statistics,
                          day_total=tracker.get_day_total(statistics_date),
                          month_total=tracker.get_month_total(statistics_date),
                          year_total=tracker.get_yearly_total(statistics_date),
                          total=tracker.get_total_count(),
                          day_unique=tracker.get_day_unique(statistics_date),
                          month_unique=tracker.get_month_unique(
                              statistics_date),
                          year_unique=tracker.get_yearly_unique(
                              statistics_date),
                          total_unique=tracker.get_unique_count()))

        return web.Response(text=output, content_type='text/html')
    except Exception as e:
        return web.Response(text=f"Internal server Error: {e}",
                            content_type='text/html',
                            status=500)


env = Environment(loader=FileSystemLoader("."),
                  autoescape=select_autoescape(["html", "xml"]))
template = env.get_template("index.html")
app = web.Application()
app.router.add_get('/', handle)

if __name__ == '__main__':
    web.run_app(app)
