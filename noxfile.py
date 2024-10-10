import sys
import nox


@nox.session
@nox.parametrize(
    "pydantic",
    ("2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6"),
)
@nox.parametrize("graphene", ("2.1.8", "2.1.9", "3.0", "3.1", "3.2", "3.3"))
@nox.parametrize("bson", ("0.5.10",))
def tests(session, pydantic, graphene, bson) -> None:
    """Tests on different combinations of pydantic, graphene & bson"""
    if sys.version_info > (3, 10) and graphene <= "3":
        # Graphene 2.x doesn't support Python 3.11
        session.skip()
    if sys.version_info >= (3, 12) and pydantic == "2.0":
        # Poetry build fails for python 3.12 and above
        # due to building wheel for pydantic-core for pydantic 2.0
        session.skip()

    session.install(f"pydantic=={pydantic}")
    session.install(f"graphene=={graphene}")
    session.install(f"bson=={bson}")
    session.install("pytest", "pytest-cov", ".")
    session.run(
        "pytest", "-v", "tests/", "--cov-report=term-missing", "--cov=graphene_pydantic"
    )
