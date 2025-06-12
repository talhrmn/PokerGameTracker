from bson import ObjectId
from pydantic_core import core_schema, PydanticCustomError


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        # Validate input, then produce a string
        def validate_to_str(v):
            if isinstance(v, ObjectId):
                return str(v)
            if isinstance(v, str) and ObjectId.is_valid(v):
                return v
            raise PydanticCustomError("value_error", "Invalid ObjectId")

        # After validation, the field’s Python type is str; so schema is str
        return core_schema.chain_schema([
            core_schema.no_info_plain_validator_function(validate_to_str),
            core_schema.str_schema()
        ])

    @classmethod
    def __get_pydantic_json_schema__(cls, schema_type, handler):
        return {"type": "string"}

    def __str__(self):
        return super().__str__()
