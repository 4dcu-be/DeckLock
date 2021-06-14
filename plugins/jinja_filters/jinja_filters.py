from pelican import signals
from json import dumps


def add_filter(pelican):
    """Add to_json filter to Pelican."""
    pelican.env.filters.update({"to_json": dumps})


def register():
    """Plugin registration."""
    signals.generator_init.connect(add_filter)
