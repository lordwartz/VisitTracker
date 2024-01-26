import pickle
from datetime import datetime
from VisitTracker import VisitTracker
from aiohttp import web
from jinja2 import Environment, FileSystemLoader, select_autoescape


async def handle(request):
    ip = request.remote
    current_day = datetime.now().date()

    try:
        with open('stats.pickle', 'rb') as f:
            stats = pickle.load(f)
    except FileNotFoundError:
        stats = {}
    tracker = VisitTracker(stats)
    tracker.update(current_day, ip)
    with open('stats.pickle', 'wb') as f:
        pickle.dump(tracker.stats, f)

    statistics = '\n'.join(f"{key}: {value}"
                           for key, value in tracker.stats.items())
    try:
        statistics_date = current_day  # datetime(2022, 1, 1).date()
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
