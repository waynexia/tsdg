from abc import ABC, abstractmethod
import random
import math


class Distribution(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def all(self) -> list:
        raise ValueError(f"This distribution is not enumerable")

    @abstractmethod
    def generator(self):
        pass

    def from_config(config: dict):
        dist_type = config["type"]
        if dist_type == "mono_inc":
            return MonoInc(config["step"])
        elif dist_type == "mono_dec":
            return MonoDec(config["step"])
        elif dist_type == "random":
            return Random(config["upper_bound"], config["lower_bound"])
        elif dist_type == "normal":
            return Normal(config["mean"], config["stddev"])
        elif dist_type == "uniform":
            return Uniform(config["upper_bound"], config["lower_bound"])
        elif dist_type == "noise":
            return Noise(config["max_fluctuation"])
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
    def __init__(self, step: float):
        self.step = step

    def generator(self):
        current = 0
        while True:
            yield current
            current += self.step


class MonoDec(Distribution):
    def __init__(self, step: float):
        self.step = step

    def generator(self):
        current = 0
        while True:
            yield current
            current -= self.step


class Random(Distribution):
    def __init__(self, upper_bound: float, lower_bound: float):
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def generator(self):
        while True:
            yield random.uniform(self.lower_bound, self.upper_bound)


class Normal(Distribution):
    def __init__(self, mean: float, std_dev: float):
        self.mean = mean
        self.std_dev = std_dev

    def generator(self):
        while True:
            yield random.normalvariate(self.mean, self.std_dev)


class Uniform(Distribution):
    def __init__(self, upper_bound: float, lower_bound: float):
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def generator(self):
        while True:
            yield random.uniform(self.lower_bound, self.upper_bound)


class Noise(Distribution):
    def __init__(self, max_fluctuation: float):
        self.max_fluctuation = max_fluctuation

    def generator(self):
        current = 0
        while True:
            current += random.uniform(-self.max_fluctuation, self.max_fluctuation)
            yield current


class Periodic(Distribution):
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
    def __init__(self, value: str):
        self.value = value

    def all(self) -> list:
        return [self.value]

    def generator(self):
        while True:
            yield self.value


class ConstantInt(Distribution):
    def __init__(self, value: int):
        self.value = value

    def all(self) -> list:
        return [self.value]

    def generator(self):
        while True:
            yield self.value


class ConstantFloat(Distribution):
    def __init__(self, value: float):
        self.value = value

    def all(self) -> list:
        return [self.value]

    def generator(self):
        while True:
            yield self.value


class Weight:
    def __init__(self, value: str, weight: float):
        self.value = value
        self.weight = weight

    def from_config(config: dict):
        return Weight(config["value"], config["weight"])


class WeightedPreset(Distribution):
    def __init__(self, presets: list):
        self.presets = presets

    def all(self) -> list:
        return [p.value for p in self.presets]

    def from_config(config: list):
        return WeightedPreset([Weight.from_config(p) for p in config])

    def generator(self):
        while True:
            yield random.choices(
                [p.value for p in self.presets], [p.weight for p in self.presets]
            )[0]
