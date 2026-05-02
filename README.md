# Cocapn Barracks

Task execution and queue management for agent fleets.

## Install

```bash
pip install cocapn-barracks
```

## Usage

```python
from cocapn_barracks import Task, TaskQueue, Executor

queue = TaskQueue()
queue.enqueue(Task(name="my-task", payload={"data": 42}))

executor = Executor()
executor.register("my-task", lambda x: x["data"] * 2)

task = queue.dequeue()
result = executor.execute(task)
print(result.result.output)  # 84
```

## License

MIT