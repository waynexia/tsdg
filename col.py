from enum import Enum

from distribution import Distribution

# Enum of data types with descriptions
class DataType(Enum):
    """
    Enum for data types supported in columns.
    """
    INTEGER = "INTEGER"  # Represents integer data type
    STRING = "STRING"    # Represents string data type
    FLOAT = "FLOAT"      # Represents floating point data type


# Class representing properties of one Column
class Column:
    """
    Represents a column in a dataset, including its name, data type, nullability, and distribution.
    """
    def __init__(
        self, name: str, type: DataType, nullability: float, dist: Distribution
    ):
        """
        Initializes a new instance of the Column class.

        :param name: The name of the column.
        :param type: The data type of the column (DataType).
        :param nullability: The nullability of the column (0 to 1).
        :param dist: The distribution of the column values (Distribution).
        """
        self.name = name
        self.type = type
        self.nullability = nullability
        self.dist = dist

    def __str__(self):
        return f"{self.name} {self.type} {self.nullability} {self.dist} "

    @staticmethod
    def from_config(config: dict):
        """
        Creates a Column instance from a configuration dictionary.

        :param config: A dictionary containing the column configuration.
        :return: A Column instance.
        """
        return Column(
            config["name"],
            DataType(config["type"]),
            config["nullability"],
            Distribution.from_config(config["dist"]),
        )
