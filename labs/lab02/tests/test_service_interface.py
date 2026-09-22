from labs.lab02.common.service_client import TARGET_HOST, TARGET_PORT


def test_local_target_is_fixed_to_the_course_service() -> None:
    assert TARGET_HOST == "lab02-target"
    assert TARGET_PORT == 8080
