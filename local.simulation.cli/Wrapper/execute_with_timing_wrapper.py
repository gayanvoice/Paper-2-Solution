import functools
import inspect
import logging
import os
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table


def execute_with_timing_wrapper(original_func):
    @functools.wraps(original_func)
    def wrapper(*args, **kwargs):
        class_name = None
        if inspect.ismethod(original_func):
            class_name = args[0].__class__.__name__  # Assumes the first argument is self/cls
        elif inspect.isfunction(original_func):
            class_name = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else None

        root_directory = os.path.dirname(os.path.abspath(__file__))
        file_name = inspect.getfile(original_func)
        relative_path = os.path.relpath(file_name, start=root_directory)
        start_time = time.time()

        try:
            result = original_func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            try:
                with open("local-simulation-cli-log.log", "a") as report_file:
                    console = Console(file=report_file, width=100)
                    table = Table(show_header=True)
                    table.add_column("file name")
                    table.add_column("class")
                    table.add_column("function")
                    table.add_column("start Time", justify="right")
                    table.add_column("end Time", justify="right")
                    table.add_column("elapsed Time", justify="right")

                    table.add_row(relative_path, class_name, original_func.__name__,
                                  str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))),
                                  str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))),
                                  f"{execution_time:.6f}s")
                    if original_func.__name__ == "__init__":
                        console.rule(f"started the local simulation cli {datetime.now().ctime()}")
                    logging.info("execute_with_timing_wrapper()")
                    console.print(table)
                    if original_func.__name__ == "do_exit" or original_func.__name__ == "do_quit":
                        console.rule(f"ended the local simulation cli {datetime.now().ctime()}")
            except Exception as e:
                print(f"error writing to local-simulation-cli-log.log {e}.")
    return wrapper
