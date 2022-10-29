from dataclasses import dataclass
import time
from functools import wraps


@dataclass
class Duration:
    func_name: str
    description: str
    durations: list[float]
    average_duration: float = 0.0
    max_duration: float = 0.0
    min_duration: float = 0.0

    def __repr__(self) -> str:
        return self.func_name + "|" + self.description + ":\n" + f"Average duration [{self.average_duration}]\n" + \
               f"Min [{self.min_duration}]  |  Max [{self.max_duration}]"


class Statistics:
    def __init__(self) -> None:
        self.durations: list[Duration] = []

    def put_duration_storage(self, func_name: str, description: str, runtime: float, total: bool) -> None:
        if total:
            func_name = "___Total"
            description = "Total runtime:"
        if duration := self.get_duration_by_name(func_name):
            duration.durations.append(runtime)
        else:
            duration = Duration(func_name=func_name, description=description, durations=[runtime])
            self.durations.append(duration)
        self.calculate_duration(duration)

    def get_duration_by_name(self, func_name: str) -> Duration | None:
        for duration in self.durations:
            if duration.func_name == func_name:
                return duration
        return None

    @staticmethod
    def calculate_duration(duration: Duration) -> None:
        if len(duration.durations) > 100:
            duration.durations.sort()
            duration.durations.pop(49)
        duration.max_duration = max(duration.durations)
        duration.min_duration = min(duration.durations)
        duration.average_duration = sum(duration.durations) / len(duration.durations)

    def print_stat_in_table(self) -> str:
        total_dr = self.get_duration_by_name("___Total")
        if not total_dr:
            return "Not a single cycle was performed"
        """ Example
                                Statistic of runtime
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                                        |  AVR [ %total ]  |   MIN   |   MAX   
        _______________________________________________________________________
        Delay of new packet from socket | 123.123 [ 100% ] | 123.123 | 123.123 
        Time of data processing         | 123.123 [ 100% ] | 123.123 | 123.123 
        _______________________________________________________________________
        Total                           | 123.123 [ 100% ] | 123.123 | 123.123 
        """
        len_of_description = max([len(d.description) for d in self.durations])
        width = len_of_description + 40  # len_values := 40
        title = f"{{:^{width}}}".format("Statistic of runtime")
        del_plus = "+" * width
        del_minus = "-" * width
        headlines = " " * len_of_description + " |  AVR [ %total ]  |   MIN   |   MAX   "
        res = f"{title}\n{del_plus}\n{headlines}\n{del_minus}\n"
        for dr in self.durations:
            if dr.func_name == total_dr.func_name:
                continue
            res += f"{{:<{len_of_description}}}".format(dr.description)
            res += " | {:^7.3f} [{:^6.0%}] | {:^7.3f} | {:^7.3f} \n".format(
                dr.average_duration,
                dr.average_duration/total_dr.average_duration,
                dr.min_duration,
                dr.max_duration)
        res += f"{del_minus}\n"
        res += f"{{:<{len_of_description}}}".format(total_dr.description)
        res += " | {:^7.3f} [{:^6.0%}] | {:^7.3f} | {:^7.3f} \n".format(
            total_dr.average_duration,
            1,
            total_dr.min_duration,
            total_dr.max_duration)
        return res

    def timer(self, description: str = '', total: bool = False):
        def decorator(func):
            @wraps(func)
            def _wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                runtime = time.perf_counter() - start
                self.put_duration_storage(str(func), description, runtime, total)
                return result
            return _wrapper
        return decorator


statistic = Statistics()
