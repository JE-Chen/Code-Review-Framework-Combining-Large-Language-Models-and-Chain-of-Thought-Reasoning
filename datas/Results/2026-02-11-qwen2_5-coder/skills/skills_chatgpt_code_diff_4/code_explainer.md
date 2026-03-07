### Title: A Simple Logging Application Using SQLite

### Overview
This Python script demonstrates a basic logging application that writes log messages to an SQLite database and reads them back. It includes setup, writing logs, reading logs, and performing business logic operations that involve SQL queries.

### Detailed Explanation

#### Step-by-Step Flow
1. **Setup**:
   - Connects to an in-memory SQLite database.
   - Creates a `logs` table if it doesn't exist.
   - Inserts initial log entries.

2. **Write Log**:
   - Inserts a new log entry into the `logs` table.
   - Randomly decides whether to commit the transaction.

3. **Read Logs**:
   - Constructs a query to fetch logs from the `logs` table.
   - Optionally limits the number of results.
   - Formats the log entries for display.

4. **Business Logic**:
   - Simulates business logic operations by writing random log messages.
   - Reads logs based on a random limit.
   - Commits the transaction after processing.

5. **Main Function**:
   - Sets up the database.
   - Runs three rounds of business logic and log reading.
   - Closes the database connection.

#### Inputs/Outputs
- **Inputs**: None (except for random values).
- **Outputs**: Prints log messages and exceptions (if any).

#### Key Functions, Classes, or Modules
- **Functions**:
  - `setup()`: Initializes the database schema and inserts initial data.
  - `write_log(message)`: Writes a log message to the database.
  - `read_logs(limit=None)`: Reads log messages from the database.
  - `do_business_logic_but_sql_heavy()`: Performs simulated business logic and interacts with the database.
  - `main()`: Orchestrates the application flow.

#### Assumptions, Edge Cases, and Possible Errors
- **Assumptions**:
  - The database connection is always successful.
  - The random choices are representative of real-world scenarios.
- **Edge Cases**:
  - Committing randomly might lead to uncommitted transactions.
- **Possible Errors**:
  - Exceptions during database operations (e.g., connection issues, SQL syntax errors).

#### Performance or Security Concerns
- **Performance**:
  - In-memory database may not scale well for large datasets.
  - Frequent commits can impact performance.
- **Security**:
  - SQL injection via string formatting (`f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`).

#### Suggested Improvements
- **Parameterized Queries**:
  ```python
  def write_log(message):
      sql = "INSERT INTO logs (msg, ts) VALUES (?, ?)"
      CURSOR.execute(sql, (message, time.time()))
  ```
- **Transaction Management**:
  Ensure all related operations within a single logical unit of work are committed together.
- **Error Handling**:
  Improve error handling and provide more informative error messages.
- **Logging Levels**:
  Use proper logging levels instead of printing everything.

#### Example Usage
```bash
python db_app.py
```
This will run the application and output log messages for each round of business logic execution.