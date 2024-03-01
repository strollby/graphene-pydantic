import sys

from nox import parametrize, session


@session
@parametrize(
    "pydantic",
    ("2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6"),
)
@parametrize("graphene", ("2.1.8", "2.1.9", "3.0", "3.1", "3.2", "3.3"))
@parametrize("bson", ("0.5.10",))
def tests(session, pydantic, graphene, bson):
    if sys.version_info > (3, 10) and pydantic in ("1.7", "1.8"):
        return session.skip()
    if sys.version_info > (3, 10) and graphene <= "3":
        # Graphene 2.x doesn't support Python 3.11
        return session.skip()
    session.install(f"pydantic=={pydantic}")
    session.install(f"graphene=={graphene}")
    session.install(f"bson=={bson}")
    session.install("pytest", "pytest-cov", ".")
    session.run(
        "pytest", "-v", "tests/", "--cov-report=term-missing", "--cov=graphene_pydantic"
    )
