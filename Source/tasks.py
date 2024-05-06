from queue import Queue
from threading import Thread
from time import sleep

training_queue = Queue()

def process_training_queue():
    while True:
        task = training_queue.get()
        print(f"Processing training request: {task}")
        # Simulate processing with a sleep
        sleep(5)  # This should be replaced with actual processing logic
        training_queue.task_done()

def enqueue_training_task(data):
    training_queue.put(data)  # Add data to the queue

# Thread to process training tasks
training_thread = Thread(target=process_training_queue, daemon=True)
training_thread.start()