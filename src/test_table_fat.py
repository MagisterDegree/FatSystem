import pytest


@pytest.fixture
def first_fixture():
    print(f"First fixture")


@pytest.fixture(scope="class")
def class_fixture(request):
    def fin():
        print(f"\n Finalize from {request.scope} fixture!")

    print("\n_____________")
    print(f"{request.node}")
    print(f"{request.scope}")
    print(f"{request.cls}")
    print(f"{request.module}")
    print("_____________\n")

    request.addfinalizer(fin)


class TestFileSystem:
    def test_one(self, class_fixture):
        print("TestFileSystem - test_one")

    def test_two(self, class_fixture):
        print("TestFileSystem - test_two")


class TestFunction:
    def test_one_function(self, first_fixture):
        print("TestFunction - test_one_function")


@pytest.fixture(params=[11, 12, 13, 14])
def fixture_with_params(request):
    return request.param


def test_one_1(fixture_with_params):
    print(fixture_with_params)
