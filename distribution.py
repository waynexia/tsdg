from abc import ABC, abstractmethod
import random
import math
import string


class Distribution(ABC):
    """
    Abstract base class for distributions. Defines the structure for distribution classes.
    """

    @abstractmethod
    def __init__(self):
        pass

    def all(self) -> list:
        raise ValueError(
            f"This distribution is not enumerable: " + self.__class__.__name__
        )

    @abstractmethod
    def generator(self):
        pass

    @classmethod
    def from_config(_cls, config: dict):
        """
        Selects the appropriate distribution class based on configuration and returns its instance.

        :param config: A dictionary containing the distribution configuration.
        :return: An instance of a Distribution subclass.
        """
        dist_type = config["type"]
        if dist_type == "mono_inc":
            return MonoInc(config["step"])
        elif dist_type == "mono_dec":
            return MonoDec(config["step"])
        elif dist_type == "random":
            return Random(config["upper_bound"], config["lower_bound"])
        elif dist_type == "random_int":
            return RandomInt(config["upper_bound"], config["lower_bound"])
        elif dist_type == "random_string":
            return RandomString(config["length"])
        elif dist_type == "normal":
            return Normal(config["mean"], config["stddev"])
        elif dist_type == "uniform":
            return Uniform(config["upper_bound"], config["lower_bound"])
        elif dist_type == "noise":
            return Noise(config["upper_bound"], config["lower_bound"])
        elif dist_type == "periodic":
            return Periodic(config["period"], config["amplitude"], config["bias"])
        elif dist_type == "constant_string":
            return ConstantString(config["value"])
        elif dist_type == "constant_int":
            return ConstantInt(config["value"])
        elif dist_type == "constant_float":
            return ConstantFloat(config["value"])
        elif dist_type == "weighted_preset":
            return WeightedPreset.from_config(config["preset"])
        else:
            raise ValueError(f"Unsupported distribution type: {dist_type}")


class MonoInc(Distribution):
    """
    Represents a monotonically increasing distribution.
    """

    def __init__(self, step: float):
        self.step = step

    def generator(self):
        current = 0
        while True:
            yield current
            current += self.step


class MonoDec(Distribution):
    """
    Represents a monotonically decreasing distribution.
    """

    def __init__(self, step: float):
        self.step = step

    def generator(self):
        current = 0
        while True:
            yield current
            current -= self.step


class Random(Distribution):
    """
    Represents a random distribution within specified bounds.
    """

    def __init__(self, upper_bound: float, lower_bound: float):
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def generator(self):
        while True:
            yield random.uniform(self.lower_bound, self.upper_bound)


class RandomInt(Distribution):
    def __init__(self, upper_bound: int, lower_bound: int):
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def all(self) -> list:
        return range(self.lower_bound, self.upper_bound)

    def generator(self):
        while True:
            yield random.randint(self.lower_bound, self.upper_bound)


class RandomString(Distribution):
    def __init__(self, length: int):
        self.length = length

    def generator(self):
        while True:
            yield "".join(
                random.choices(string.ascii_letters + string.digits, k=self.length)
            )


class Normal(Distribution):
    """
    Represents a normal (Gaussian) distribution.
    """

    def __init__(self, mean: float, std_dev: float):
        self.mean = mean
        self.std_dev = std_dev

    def generator(self):
        while True:
            yield random.normalvariate(self.mean, self.std_dev)


class Uniform(Distribution):
    """
    Represents a uniform distribution within specified bounds.
    """

    def __init__(self, upper_bound: float, lower_bound: float):
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def generator(self):
        while True:
            yield random.uniform(self.lower_bound, self.upper_bound)


class Noise(Distribution):
    """
    Represents a noise distribution with a random fluctuation in bound.
    """

    def __init__(self, upper_bound: float, lower_bound: float):
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def generator(self):
        current = 0
        while True:
            current += random.uniform(self.lower_bound, self.upper_bound)
            yield current


class Periodic(Distribution):
    """
    Represents a periodic distribution with specified period, amplitude, and bias.
    """

    def __init__(self, period: float, amplitude: float, bias: float):
        self.period = period
        self.amplitude = amplitude
        self.bias = bias

    def generator(self):
        current = 0
        while True:
            current = self.amplitude * math.sin(current / self.period) + self.bias
            yield current


class ConstantString(Distribution):
    """
    Represents a constant string distribution.
    """

    def __init__(self, value: str):
        self.value = value

    def all(self) -> list:
        return [self.value]

    def generator(self):
        while True:
            yield self.value


class ConstantInt(Distribution):
    """
    Represents a constant integer distribution.
    """

    def __init__(self, value: int):
        self.value = value

    def all(self) -> list:
        return [self.value]

    def generator(self):
        while True:
            yield self.value


class ConstantFloat(Distribution):
    """
    Represents a constant floating-point distribution.
    """

    def __init__(self, value: float):
        self.value = value

    def all(self) -> list:
        return [self.value]

    def generator(self):
        while True:
            yield self.value


class Weight:
    """
    Represents a weighted value for the WeightedPreset distribution.
    """

    def __init__(self, value: str, weight: float):
        self.value = value
        self.weight = weight

    @classmethod
    def from_config(_cls, config: dict):
        return Weight(config["value"], config["weight"])


class WeightedPreset(Distribution):
    """
    Represents a weighted preset distribution.
    """

    def __init__(self, presets: list):
        self.presets = presets

    def all(self) -> list:
        return [p.value for p in self.presets]

    @classmethod
    def from_config(_cls, config: list):
        return WeightedPreset([Weight.from_config(p) for p in config])

    def generator(self):
        while True:
            yield random.choices(
                [p.value for p in self.presets], [p.weight for p in self.presets]
            )[0]
