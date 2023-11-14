import os
from util import MD2
import pytest


def test_models():
    data_dir = "tests/data"
    models = os.listdir(data_dir)
    models = [x for x in models if x.lower().endswith(".md2")]

    for model in models:
        MD2.load_file(os.path.join(data_dir, model))
    assert True


def test_wrong_format():
    with pytest.raises(ValueError):
        MD2.load_file('tests/data/car.jpg')
