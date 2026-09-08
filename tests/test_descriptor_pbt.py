"""V1, V2 — 직렬화 round-trip·digest 불변 (Hypothesis). 소유: CJ. 구현: S2."""

from hypothesis import given, settings
from hypothesis import strategies as st

from skillloop import descriptor as D

# JSON 호환 값(중첩 dict/list/스칼라). digest 입력 정규화 검증용.
json_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-(10**9), max_value=10**9),
    st.text(max_size=20),
)
json_values = st.recursive(
    json_scalars,
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(st.text(max_size=8), children, max_size=4),
    ),
    max_leaves=8,
)


def _content(origin, applicability, procedure, idv="skill-x", ver="1.0.0"):
    return {
        "id": idv,
        "version": ver,
        "origin": origin,
        "applicability": applicability,
        "procedure": procedure,
    }


@given(
    origin=st.dictionaries(st.text(max_size=8), json_values, max_size=4),
    applicability=st.dictionaries(st.text(max_size=8), json_values, max_size=4),
    procedure=st.dictionaries(st.text(max_size=8), json_values, max_size=4),
)
@settings(max_examples=100)
def test_serialize_roundtrip_preserves_digest(origin, applicability, procedure):
    # V1: serialize → deserialize 후 동일 객체·동일 digest, 재계산 digest도 일치.
    content = _content(origin, applicability, procedure)
    d = D.make_descriptor(content, actual_reuse=3, demo_seed=True)
    back = D.deserialize(D.serialize(d))
    assert back == d
    assert back.digest == d.digest
    assert D.compute_digest(D._content_of(back)) == d.digest


@given(
    origin=st.dictionaries(st.text(max_size=8), json_values, max_size=4),
    applicability=st.dictionaries(st.text(max_size=8), json_values, max_size=4),
    procedure=st.dictionaries(st.text(max_size=8), json_values, max_size=4),
    reuse=st.integers(min_value=0, max_value=10**6),
    seed=st.booleans(),
)
@settings(max_examples=100)
def test_digest_ignores_mutable_usage(origin, applicability, procedure, reuse, seed):
    # V2: 가변 usage(actual_reuse, demo_seed)가 달라도 digest는 불변.
    content = _content(origin, applicability, procedure)
    base = D.compute_digest(content)
    d = D.make_descriptor(content, actual_reuse=reuse, demo_seed=seed)
    assert d.digest == base


def test_key_order_does_not_change_digest():
    # 정규화: content dict의 키 삽입 순서가 달라도 canonical 표현·digest 동일.
    c1 = {"id": "a", "version": "1", "origin": {"x": 1, "y": 2},
          "applicability": {"a": [1, 2]}, "procedure": {"p": "q"}}
    c2 = {"procedure": {"p": "q"}, "applicability": {"a": [1, 2]},
          "origin": {"y": 2, "x": 1}, "version": "1", "id": "a"}
    assert D.compute_digest(c1) == D.compute_digest(c2)


def test_digest_input_excludes_digest_and_usage_fields():
    # 해시 입력에 digest·usage가 섞여 들어와도 무시(CONTENT_KEYS만 사용).
    c = {"id": "a", "version": "1", "origin": {}, "applicability": {}, "procedure": {}}
    polluted = dict(c, digest="deadbeef", actual_reuse=99, demo_seed=True)
    assert D.compute_digest(c) == D.compute_digest(polluted)
