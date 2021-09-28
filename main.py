# M/D/1 queue
import scipy.stats as sts
import heapq

class Event:
    '''
    Store the properties of one event in the Schedule class defined below. Each
    event has a time at which it needs to run, a function to call when running
    the event, along with the arguments and keyword arguments to pass to that
    function.
    '''
    def __init__(self, timestamp, function, *args, **kwargs):
        self.timestamp = timestamp
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __lt__(self, other):
        '''
        This overloads the less-than operator in Python. We need it so the
        priority queue knows how to compare two events. We want events with
        earlier (smaller) times to go first.
        '''
        return self.timestamp < other.timestamp

    # 関数を実行する。
    def run(self, schedule):
        '''
        Run an event by calling the function with its arguments and keyword
        arguments. The first argument to any event function is always the
        schedule in which events are being tracked. The schedule object can be
        used to add new events to the priority queue.
        '''
        self.function(schedule, *self.args, **self.kwargs)


class Schedule:
    '''
    Implement an event schedule using a priority queue. You can add events and
    run the next event.

    The `now` attribute contains the time at which the last event was run.
    '''

    def __init__(self):
        # 現在のシミュレーションの時間
        self.now = 0  # Keep track of the current simulation time
        self.priority_queue = []  # The priority queue of events to run

    def add_event_at(self, timestamp, function, *args, **kwargs):
        # Add an event to the schedule at a particular point in time.
        # priority_queueにイベントの内容を格納する。
        heapq.heappush(
            self.priority_queue,
            Event(timestamp, function, *args, **kwargs))

    def add_event_after(self, interval, function, *args, **kwargs):
        # Add an event to the schedule after a specified time interval.
        self.add_event_at(self.now + interval, function, *args, **kwargs)

    # 一番小さい時間のイベント時間を返す。
    def next_event_time(self):
        return self.priority_queue[0].timestamp

    # イベントの実行を行う。
    def run_next_event(self):
        # Get the next event from the priority queue and run it.
        # 一番小さい時間のイベントを取り出す。
        event = heapq.heappop(self.priority_queue)
        # 現在の時間を更新する。
        self.now = event.timestamp
        event.run(self)

class Queue:
    def __init__(self):
        # We start with an empty queue and the server not busy
        self.people_in_queue = 0
        self.people_being_served = 0

    # 乗客を並べる関数
    def add_customer(self, schedule):
        # Add the customer to the queue
        self.people_in_queue += 1
        print(
            f'{schedule.now:5.2f}: Add customer to queue.  '
            f'Queue length: {self.people_in_queue}')
        # 収容人数の限界値
        if self.people_being_served < 130:
            # This customer can be served immediately
            # 第一引数へ収容するのにかかる時間を設定する。
            # 参考 : https://py4etrics.github.io/5_SciPy_stats.html
            schedule.add_event_after(sts.norm.rvs(scale=0.01 * 1, loc=0.05), self.start_serving_customer)

    # 乗客の収容を開始する関数
    def start_serving_customer(self, schedule):
        # Move the customer from the queue to a server
        self.people_in_queue -= 1
        self.people_being_served += 1
        print(
            f'{schedule.now:5.2f}: Start serving customer. '
            f'Queue length: {self.people_in_queue}')
        # Schedule when the server will be done with the customer.
        # Generate a random service time from the service distribution.
        # 参考 : https://py4etrics.github.io/5_SciPy_stats.html
        schedule.add_event_after(
            sts.norm.rvs(scale=0.01 * 1, loc=0.03),
            self.finish_serving_customer)

    # 乗客の降ろす関数
    def finish_serving_customer(self, schedule):
        # Remove the customer from the server
        self.people_being_served -= 1
        print(
            f'{schedule.now:5.2f}: Stop serving customer.  '
            f'Queue length: {self.people_in_queue}')
        if self.people_in_queue > 0:
            # There are more people in the queue so serve the next customer
            # 第一引数へ収容するのにかかる時間を設定する。
            # 参考 : https://py4etrics.github.io/5_SciPy_stats.html
            schedule.add_event_after(sts.norm.rvs(scale=0.01 * 1, loc=0.05), self.start_serving_customer)

class BusSystem:
    def __init__(self, arrival_distribution):
        self.queue = Queue()
        self.arrival_distribution = arrival_distribution

    def add_customer(self, schedule):
        # Add this customer to the queue
        self.queue.add_customer(schedule)
        # Schedule when to add another customer
        schedule.add_event_after(
            self.arrival_distribution.rvs(),
            self.add_customer)

    def run(self, schedule):
        # Schedule when the first customer arrives
        schedule.add_event_after(
            self.arrival_distribution.rvs(),
            self.add_customer)

def run_simulation(arrival_distribution, run_until):
    schedule = Schedule()
    bus_system = BusSystem(arrival_distribution)
    bus_system.run(schedule)
    # シミュレーションの数が終わるまで続ける。
    while schedule.next_event_time() < run_until:
        schedule.run_next_event()
    return bus_system

# 指数分布
arrival_distribution = sts.expon(scale=1)

# Run the simulation once
# シミュレーションの時間まで
duration = 100
bus_system = run_simulation(arrival_distribution, duration)
print(f'There are {bus_system.queue.people_in_queue} people in the queue')
