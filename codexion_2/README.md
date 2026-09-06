```markdown
*This project has been created as part of the 42 curriculum by [snaimi].*

# Codexion

## Description
**Codexion** is a concurrent multi-threaded simulation inspired by the classic Dining Philosophers problem, adapted to represent software engineers (coders) sharing limited physical hardware authorization dongles required to compile their projects[cite: 1]. 

In this simulation, $N$ coders share $N$ dongles arranged in a ring buffer/topology[cite: 1, 5]. To initiate a compilation step, a coder must acquire both their left and right adjacent dongles[cite: 1, 5]. After compiling, coders proceed to debug their code and refactor it before attempting to acquire dongles for their next compilation[cite: 1, 9]. 

The primary objective of Codexion is to manage shared resources efficiently without causing **deadlocks**, **starvation**, or **race conditions**, while preventing coders from reaching **burnout** (starving due to extended periods without starting a compilation)[cite: 1, 7, 8]. The simulation incorporates scheduling policies (FIFO and Earliest Deadline First / EDF)[cite: 1, 8] and enforces strict hardware cooldown periods on dongles post-release[cite: 1, 2, 8].

---

## Instructions

### Compilation
The project includes a `Makefile` that compiles all source files with `cc` using the mandatory flags `-Wall -Wextra -Werror -pthread`[cite: 6].

To build the executable:
```bash
make

```

To recompile or clean object files:

```bash
make clean    # Removes object files (.o)
make fclean   # Removes object files and the 'codexion' binary
make re       # Recompiles the entire project

```

### Execution

Run the program by passing the simulation parameters in the following format:

```bash
./codexion number_of_coders time_to_burnout time_to_compile time_to_debug time_to_refactor [number_of_compiles_required] [dongle_cooldown] scheduler

```

#### Parameter Breakdown:

* `number_of_coders`: Number of coder threads (and corresponding hardware dongles).


* `time_to_burnout`: Max time (in ms) a coder can go without starting a compilation before burning out.


* `time_to_compile`: Duration (in ms) spent compiling (requires holding 2 dongles).


* `time_to_debug`: Duration (in ms) spent debugging.


* `time_to_refactor`: Duration (in ms) spent refactoring.


* `number_of_compiles_required`: *(Optional)* Number of successful compilations each coder must complete to finish simulation (-1 or omitted for infinite).


* `dongle_cooldown`: *(Optional)* Cooldown duration (in ms) applied to a dongle upon release before it can be used again.


* `scheduler`: Scheduling strategy (`fifo` or `edf`).



#### Example Execution:

```bash
./codexion 4 800 200 200 200 5 100 edf

```

---

## Blocking Cases Handled

The implementation robustly addresses and solves the core classical concurrency and scheduling issues:

### 1. Deadlock Prevention & Coffman's Conditions

A deadlock occurs when threads are indefinitely waiting on each other for resource acquisition. Codexion breaks the **Circular Wait** condition (one of Coffman's 4 conditions) through **Strict Resource Hierarchy Ordering**:

* Dongles are assigned unique integer IDs ($0, 1, \dots, N-1$).


* Regardless of a coder's position, the thread always attempts to acquire the dongle with the lower numerical ID first (`f = min(left, right)`), followed by the higher ID (`s = max(left, right)`).


* Because all threads request resources in the exact same global ordinal sequence, circular wait dependencies are mathematically impossible.



### 2. Starvation Prevention

Starvation is handled through thread staggering and scheduling:

* Even-indexed coders perform a microscopic initial delay (`precise_sleep(1, data)`), breaking symmetric initial acquisition requests.


* Under the `EDF` (Earliest Deadline First) and `FIFO` modes, priority metrics track coder waiting times and prevent faster threads from monopolizing adjacent dongles indefinitely.



### 3. Cooldown Handling

When a coder finishes compiling and calls `release_dongles()`, a timestamp parameter `cooldown_until` is attached to each released dongle calculated as `current_time + dongle_cooldown`. When another thread attempts to acquire a dongle in `acquire_one_dongle()`, it verifies both `!dongle->in_use` and `now >= dongle->cooldown_until`. If a dongle is on cooldown, acquisition is rejected, forcing the acquiring thread to yield/sleep briefly (`usleep(200)`).

### 4. Precise Burnout Detection

A dedicated background monitor thread (`monitor_routine`) continuously inspects all coders' status at sub-millisecond granularity (`usleep(500)`).

* `last_compile_start` is atomically protected via `state_mutex`.


* If `(get_time_ms() - coder.last_compile_start) >= time_to_burnout`, the monitor immediately sets `simulation_over = 1`, locks `write_mutex`, prints the precise burnout log, and terminates the simulation before any subsequent state changes occur.



### 5. Log Serialization

To avoid mixed/interleaved output lines when multiple threads log state transitions simultaneously, all status logging (`log_status()`) and terminal events are wrapped in a shared binary mutex (`write_mutex`). Furthermore, `log_status()` checks `simulation_over` under `state_mutex` before writing to ensure zero logs are printed after a burnout or simulation halt.

---

## Thread Synchronization Mechanisms

### Primitives Used

* `pthread_mutex_t`: Standard POSIX mutual exclusion locks used to protect internal data state, dongle availability, and stdout writing.


* `pthread_t`: POSIX thread handles for coders and the monitor.



### Coordinated Access to Shared Resources

1. **Dongle Protection (`t_dongle.mutex`)**:
Each dongle contains its own mutex `dongle.mutex`. Threads lock the individual dongle mutex to query or mutate `in_use` and `cooldown_until` attributes, preventing race conditions when two adjacent coders compete for the same hardware dongle.


2. **Simulation State & Metrics (`t_data.state_mutex`)**:
Coordinates global state reads/writes (`simulation_over`, `last_compile_start`, and `compiles_done`).


* **Coders** lock `state_mutex` to update `last_compile_start` and check if `simulation_over` has been set.


* **Monitor** locks `state_mutex` to check burnout thresholds across all coders or verify whether all coders completed `number_of_compiles_required`.




3. **Log Output (`t_data.write_mutex`)**:
Acts as an output bottleneck ensuring that console logging is fully thread-safe and linear.


4. **Thread-Safe Coder-Monitor Communication**:
Communication between coder threads and the monitor thread is entirely asynchronous and lock-guarded through memory flags rather than blocking signals.


* *Monitor $\rightarrow$ Coders*: When a burnout occurs or all compilations complete, the monitor sets `data->simulation_over = 1` under `state_mutex`. Coders check this flag before resource acquisition, during active waiting in `precise_sleep()`, and between routine states to exit cleanly.


* *Coders $\rightarrow$ Monitor*: Coders update their `last_compile_start` timestamp under `state_mutex` every time they acquire dongles. The monitor reads these timestamps under the same mutex to calculate exact burnout deltas.





---

## Resources

### References & Documentation

* [POSIX Threads (pthreads) Programming - Lawrence Livermore National Laboratory](https://www.google.com/search?q=https://hpc-tutorials.llnl.gov/posix/)
* [Operating System Concepts (Silberschatz, Galvin, Gagne)](https://www.google.com/search?q=https://www.os-book.com/) - Chapter on Deadlocks and Process Synchronization.
* [The Dining Philosophers Problem - Edsger W. Dijkstra](https://www.google.com/search?q=https://en.wikipedia.org/wiki/Dining_philosophers_problem)
* [Linux man pages for pthread_mutex](https://www.google.com/search?q=https://man7.org/linux/man-pages/man3/pthread_mutex_init.3p.html)

### Use of Artificial Intelligence

AI (Large Language Models) was utilized during the development of this project for the following specific tasks:

* **Code Formatting & Norminette Alignment**: Assisting in structuring function signatures and headers to strictly adhere to the 42 C Coding Standard (Norminette).
* **Documentation & README Generation**: Drafting and structuring comprehensive technical documentation, detailed explanations of concurrency primitives, and Coffman's condition analysis.
* **Edge Case Brainstorming**: Reviewing dynamic timing scenarios to identify potential race conditions in high-concurrency sleep loops.

---

## Acknowledgments

A special thank you to **1337 School**, part of the 42 Network, along with all the amazing staff members and fellow students. Thank you for cultivating an empowering, peer-learning environment and providing the tools, challenges, and support necessary to continuously grow as software engineers.

```

```