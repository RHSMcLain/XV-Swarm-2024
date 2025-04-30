import time

start_time = time.monotonic()

while True:
    current_time = time.monotonic()
    elapsed_time = current_time - start_time

    if elapsed_time >= 5:
        # Code to be executed after 10 seconds goes here
        print("This code ran after 10 seconds.")
        break
    # You can add other tasks or checks here if needed