import schemathesis
from hypothesis import settings

schema = schemathesis.graphql.from_url("http://0.0.0.0:8003/graphql")

# def my_check(response, case):
#     print(response.json())
#     if response.json()['data'] is None:
#         raise AssertionError("The ultimate answer not found!")

@schema.parametrize()
@settings(deadline=None)
def test(case):
    case.headers = case.headers or {}
    case.headers["Authorization"] = f"Bearer {'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDIyODc2NzUsInN1YiI6eyJsb2dpbiI6Ijc5MjExMTExMTExIiwicGFzc3dvcmQiOiIkMmIkMTIkdk5TUWZ2UEk3cFhCcmRGMklJbmdSLjl2WE4yVHM3V25DVzFUdDRzYWFrUmJ0Nmt6OFNham0ifX0.2mt8Be7xYZiWejuPVF4qh2gJwMKM-_vnG2qIJlJwRoA'}"
    case.call_and_validate()
    # response = case.call()
    # print(response)
    # case.validate_response(response, additional_checks=(my_check,))
