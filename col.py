from enum import Enum

from distribution import Distribution

# define properties of one Column


# enum of data types
class DataType(Enum):
    INTEGER = "INTEGER"
    STRING = "STRING"
    FLOAT = "FLOAT"


class Column:
    def __init__(
        self, name: str, type: DataType, nullability: float, dist: Distribution
    ):
        self.name = name
        self.type = type
        self.nullability = nullability
        self.dist = dist

    def __str__(self):
        return f"{self.name} {self.type} {self.nullability} {self.dist} "

    def from_config(config: dict):
        return Column(
            config["name"],
            DataType(config["type"]),
            config["nullability"],
            Distribution.from_config(config["dist"]),
        )
