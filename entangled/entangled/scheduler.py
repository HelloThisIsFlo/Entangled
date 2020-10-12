from threading import Thread
from time import sleep
from datetime import datetime, timedelta
from math import floor


class RunAtTime(Thread):
    def __init__(self, run_at: datetime, func_to_run, *func_args):
        super().__init__()
        self.run_at = run_at
        self.func_to_run = func_to_run
        self.func_args = func_args

    def run(self):
        def ensure_valid(time_until_scheduled_run):
            if time_until_scheduled_run < timedelta(0):
                raise ValueError(
                    f"Can not schedule in the past! Run at: '{self.run_at}' | Now: '{now}'"
                )
            if time_until_scheduled_run.days != 0:
                raise ValueError(
                    f"Can not schedule days in the future! Run at: '{self.run_at}' | Now: '{now}'"
                )

        def to_millisec(time_until_scheduled_run: timedelta):
            seconds_to_micro = time_until_scheduled_run.seconds * 1000 * 1000
            return floor(
                (seconds_to_micro + time_until_scheduled_run.microseconds) / 1000
            )

        def wait_until_scheduled_run(time_until_scheduled_run):
            sleep(to_millisec(time_until_scheduled_run) / 1000)

        now = datetime.now()
        time_until_scheduled_run = self.run_at - now
        ensure_valid(time_until_scheduled_run)

        print(
            f"Scheduled function '{self.func_to_run.__name__}' to run in '{to_millisec(time_until_scheduled_run) / 1000}' seconds"
        )
        wait_until_scheduled_run(time_until_scheduled_run)
        print(f"Running scheduled function '{self.func_to_run.__name__}'")
        self.func_to_run(*self.func_args)


def schedule_run(run_at, func_to_run, *func_args):
    RunAtTime(run_at, func_to_run, *func_args).start()
