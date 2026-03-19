import pytest

from ims.engine.context import SimulationContext, ensure_context_rng
from ims.model.bav_updates import BAVUpdateResult, update_bav_central_state
from ims.model.entities import BAV, Insurer, Policyholder


def test_update_bav_without_rng_updates_counts_and_time_fields() -> None:
    context = SimulationContext(period=2, logtime=5)
    bav = BAV(entity_id=100, name="Basis-BAV")
    insurers = [Insurer(entity_id=200, name="Aktive VU", active=True)]
    policyholders = [
        Policyholder(entity_id=300, name="Aktiver VN", active=True, insurer_id=200),
        Policyholder(entity_id=301, name="Inaktiver VN", active=False, insurer_id=200),
    ]

    result = update_bav_central_state(context, bav, insurers, policyholders)

    assert result == BAVUpdateResult(
        period=2,
        logtime=5,
        active_insurer_count=1,
        active_policyholder_count=1,
        sample_token=None,
    )
    assert bav.last_update_period == 2
    assert bav.last_update_logtime == 5
    assert bav.last_active_insurer_count == 1
    assert bav.last_active_policyholder_count == 1
    assert bav.last_sample_token is None


def test_update_bav_with_deterministic_rng_uses_context_rng() -> None:
    context = SimulationContext(period=1, logtime=3, rng_seed=42)
    ensure_context_rng(context)
    bav = BAV(entity_id=100, name="Basis-BAV")

    result = update_bav_central_state(
        context,
        bav,
        [Insurer(entity_id=200, name="Aktive VU", active=True)],
        [Policyholder(entity_id=300, name="Aktiver VN", active=True, insurer_id=200)],
        use_rng_sample=True,
    )

    assert result.sample_token == 0.6394267984578837
    assert bav.last_sample_token == 0.6394267984578837


def test_update_bav_with_rng_sample_requires_context_rng() -> None:
    context = SimulationContext(period=1, logtime=1, rng_seed=7)
    bav = BAV(entity_id=100, name="Basis-BAV")

    with pytest.raises(ValueError, match="context.rng is required"):
        update_bav_central_state(context, bav, [], [], use_rng_sample=True)


def test_update_bav_counts_only_active_entities() -> None:
    context = SimulationContext(period=4, logtime=9)
    bav = BAV(entity_id=100, name="Basis-BAV")
    insurers = [
        Insurer(entity_id=200, name="Aktive VU", active=True),
        Insurer(entity_id=201, name="Inaktive VU", active=False),
    ]
    policyholders = [
        Policyholder(entity_id=300, name="Aktiver VN", active=True, insurer_id=200),
        Policyholder(entity_id=301, name="Inaktiver VN", active=False, insurer_id=200),
        Policyholder(entity_id=302, name="Aktiver unzugeordnet", active=True, insurer_id=None),
    ]

    result = update_bav_central_state(context, bav, insurers, policyholders)

    assert result.active_insurer_count == 1
    assert result.active_policyholder_count == 2
