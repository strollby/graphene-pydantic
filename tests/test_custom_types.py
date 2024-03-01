import sys
from typing import Any, Callable
from typing import List

import graphene
import pydantic
import pytest
from bson import ObjectId
from pydantic import TypeAdapter
from pydantic_core import core_schema

from graphene_pydantic import PydanticInputObjectType, PydanticObjectType


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires >= python3.9")
def test_query():
    from typing import Annotated

    class _ObjectIdPydanticAnnotation:
        """JSON Serializable ObjectId"""

        @classmethod
        def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,  # noqa: ANN401
            _handler: Callable[[Any], core_schema.CoreSchema],  # noqa: ANN401
        ) -> core_schema.CoreSchema:
            def validate_from_str(input_value: str) -> ObjectId:
                return ObjectId(input_value)

            return core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.no_info_plain_validator_function(validate_from_str),
                ],
                serialization=core_schema.to_string_ser_schema(),
            )

    PyObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]

    class Foo(pydantic.BaseModel):
        name: str
        field1: list[PyObjectId]
        field2: PyObjectId

    class FooBarOutput(PydanticObjectType):
        class Meta:
            model = Foo

    class FooBarInput(PydanticInputObjectType):
        class Meta:
            model = Foo
            exclude_fields = ["field2"]

    foo_bars: List[Foo] = []

    class Query(graphene.ObjectType):
        list_foo_bars = graphene.List(FooBarOutput, match=FooBarInput())

        @staticmethod
        def resolve_list_foo_bars(parent, info, match: FooBarInput = None):
            if match is None:
                return foo_bars
            return [f for f in foo_bars if f == Foo.model_validate(match)]

    foo_bars = [
        Foo(field1=[ObjectId()], field2=str(ObjectId()), name="john doe"),
        Foo(field1=[ObjectId()], field2=ObjectId(), name="john doe"),
    ]

    schema = graphene.Schema(query=Query)
    query = """
        query {
            listFooBars {
                name
                field1
                field2
            }
        }
    """
    result = schema.execute(query)

    assert result.errors is None
    assert result.data is not None
    assert (
        TypeAdapter(List[Foo]).validate_python(result.data["listFooBars"]) == foo_bars
    )
