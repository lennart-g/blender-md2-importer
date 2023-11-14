from util.prepare_skin_paths import get_existing_skin_path, get_path_from_skin_name


def test_get_path_from_skin_name() -> None:
    obj_path = "blender-md2-importer/tests/data/car.md2"
    skin_name = "'models/sk89q/w_sitters/car.jpg\x00ght.jpg\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
                "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    skin_path = get_path_from_skin_name(obj_path, skin_name)
    print(skin_path)
    assert skin_path == "blender-md2-importer/tests/data/car.jpg\x00ght.jpg"


def test_get_existing_skin_path() -> None:
    args = {
        'skin_path': 'tests/data/car.jpg\x00ght.jpg'}
    out = get_existing_skin_path(**args)
    assert out is None

    args = {
        'skin_path': 'tests/data/car.bmp'}
    out = get_existing_skin_path(**args)
    assert out == "tests/data/car.jpg"
