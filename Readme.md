# Network Programming Exercise 1: TCP Client-Server Application

A Python-based client-server application that provides computational services over TCP sockets. The server implements authentication and offers three main functions: LCM calculation, Caesar cipher encryption, and parentheses validation.

## Features

- **TCP-based communication** with reliable, ordered message delivery
- **User authentication** with username/password validation
- **Multiple computational services**:
  - **lcm (Least Common Multiple)**: Calculate the LCM of two integers
  - **Caesar Cipher**: Encrypt text using Caesar cipher with configurable shift
  - **Parentheses Validation**: Check if a string contains valid parentheses pairs
- **Concurrent client handling** using `select()` for I/O multiplexing
- **State-based protocol** for managing client authentication and command execution

## Project Structure

```
.
├── ex1_server.py          # Server implementation
├── ex1_client.py          # Client implementation
├── users_passwords.txt     # User credentials file (tab-separated)
└── README.md              # This file
```

## Requirements

- Python 3.x
- No external dependencies (uses only standard library)

## Usage

### Starting the Server

```bash
./ex1_server.py <users_file> [port]
```

**Arguments:**
- `users_file` (required): Path to a file containing username-password pairs (tab or space-separated)
- `port` (optional): Port number to listen on (default: 1337)

**Example:**
```bash
./ex1_server.py users_passwords.txt
./ex1_server.py users_passwords.txt 8080
```

### Running the Client

```bash
./ex1_client.py [hostname [port]]
```

**Arguments:**
- `hostname` (optional): Server hostname or IP address (default: localhost)
- `port` (optional): Server port number (default: 1337)

**Example:**
```bash
./ex1_client.py
./ex1_client.py localhost 1337
./ex1_client.py 192.168.1.100 8080
```

### Users File Format

The users file should contain username-password pairs, one per line, separated by tabs:

```
username1    password1
username2    password2
username3    password3
```

Example (`users_passwords.txt`):
```
g	1
f	2
a	3
```

## Protocol

### Authentication Flow

1. Client connects to server
2. Server sends: `"Welcome! Please log in.\n"`
3. Client sends: `"User: <username>\n"`
4. Client sends: `"Password: <password>\n"`
5. Server responds:
   - Success: `"Hi <username>, good to see you\n"`
   - Failure: `"Failed to login.\n"` (connection closed)

### Commands (After Authentication)

All commands must end with a newline (`\n`).

#### LCM Command
```
lcm: <x> <y>
```
- Calculates the Least Common Multiple of two integers
- Response: `"the lcm is: <result>\n"`

**Example:**
```
lcm: 4 6
LCM: 12
```

#### Caesar Cipher Command
```
caesar: <plaintext> <shift>
```
- Encrypts text using Caesar cipher with the specified shift value
- Supports uppercase, lowercase, and spaces
- Response: `"the ciphertext is: <encrypted>\n"` or `"error: invalid input.\n"`

**Example:**
```
caesar: hello 3
Ciphertext: khoor
```

#### Parentheses Validation Command
```
parentheses: <string>
```
- Validates if a string contains only valid parentheses pairs
- Response: `"the parentheses are balanced: yes"` or `"the parentheses are balanced: no"`

**Example:**
```
parentheses: (())
the parentheses are balanced: yes
```

#### Quit Command
```
quit
```
- Closes the connection gracefully

## Why TCP Instead of UDP?

This application uses **TCP (Transmission Control Protocol)** instead of UDP (User Datagram Protocol) for several critical reasons:

### 1. **Reliability and Data Integrity**
TCP provides **guaranteed delivery** of all packets. If a packet is lost, corrupted, or arrives out of order, TCP automatically retransmits it and ensures correct ordering. This is essential for:
- **Authentication**: Username and password must arrive correctly and in order
- **Command execution**: Commands like `lcm: 4 6` must be received completely and accurately
- **Results**: Server responses must be delivered reliably to the client

With UDP, there's no guarantee that messages will arrive, which could lead to:
- Authentication failures due to lost packets
- Incomplete commands causing errors
- Missing or corrupted results

### 2. **Ordered Delivery**
TCP guarantees that packets arrive **in the same order they were sent**. This is crucial for our state-based protocol:
- The server expects messages in a specific sequence: welcome → username → password → commands
- Commands must be processed in order to maintain correct state
- Multiple commands sent quickly must be processed sequentially

UDP does not guarantee ordering, which could cause:
- Password arriving before username
- Commands processed out of sequence
- State machine corruption

### 3. **Connection-Oriented Communication**
TCP establishes a **persistent connection** between client and server, which provides:
- **Session management**: The server can track client state (awaiting_username, awaiting_password, authenticated)
- **Stateful interactions**: Authentication state persists across multiple messages
- **Connection lifecycle**: Clear connection establishment and teardown

UDP is connectionless, meaning:
- No built-in session tracking
- Each packet is independent
- Would require implementing custom session management

### 4. **Flow Control and Congestion Control**
TCP includes built-in mechanisms to:
- Prevent overwhelming the receiver with data
- Adapt to network conditions
- Ensure fair bandwidth usage

This helps prevent:
- Server overload from multiple clients
- Network congestion
- Data loss under high load

### 5. **Error Detection and Correction**
TCP includes:
- Checksums for detecting corrupted data
- Automatic retransmission of lost packets
- Duplicate detection

UDP only provides checksums without retransmission, meaning corrupted or lost data would require custom error handling.

### 6. **Application Requirements Match TCP Characteristics**

Our application needs:
-  **Reliable authentication** → TCP guarantees delivery
-  **Stateful protocol** → TCP maintains connection state
-  **Ordered commands** → TCP ensures ordering
-  **Error-free computation** → TCP provides error detection/correction
-  **Multiple message exchanges** → TCP handles persistent connections efficiently

UDP would be more suitable for:
- Real-time streaming where occasional loss is acceptable
- Broadcasting to multiple recipients
- Low-latency applications where speed matters more than reliability
- Simple request-response where each request is independent

### Conclusion

For a client-server application requiring authentication, state management, and reliable command execution, **TCP is the appropriate choice**. The overhead of TCP's reliability mechanisms is justified by the need for guaranteed, ordered delivery of authentication credentials and computational commands.

## Implementation Details

### Server Architecture

- Uses `select()` for I/O multiplexing to handle multiple clients concurrently
- Implements message buffering to handle multiple messages arriving in a single `recv()` call
- State machine tracks client authentication status
- Processes commands only after successful authentication

### Client Architecture

- Simple synchronous client that connects, authenticates, and sends commands
- Handles user input and displays server responses
- Gracefully handles connection errors and server disconnections

## Error Handling

- Invalid credentials result in connection termination
- Invalid command formats are rejected with error messages
- Network errors are caught and reported
- Server handles client disconnections gracefully

# Protocol Choice: TCP

In this project, we chose to implement the communication between the client and server using the TCP (Transmission Control Protocol) rather than UDP (User Datagram Protocol).
 
-----------------------------------------------------------------------------------------------------------------

## Description of the Implemented Protocol

The client and server communicate over a TCP socket connection.
After establishing a reliable connection, the server guides the client through:

Username submission
Password submission
Command execution (Caesar cipher, lcm, parentheses validation)

Session termination via the quit command

Each message is sent as a full line terminated with \n, and the server processes messages in the exact order they are received.

# Explanation of the Choice: Why TCP?

1. Reliable Transmission for Credentials

User authentication is critical. The username and password must arrive:

completely, correctly, and in the right order.

If we used UDP, packets could be:
lost, dropped, duplicated, or received out of order.

This would cause failed login attempts or even accidental lockouts.
TCP ensures that credentials arrive exactly as the user typed them.

2. Guaranteed Accuracy of Commands

The server executes operations that require full, accurate input:

Caesar cipher
LCM calculation
Parentheses validation

With UDP, corrupted or missing data could lead to:

incorrect results, invalid commands, or unnecessary connection termination.

Using TCP guarantees that each command is delivered intact and in order, ensuring correct results.

3. Stream-Based Session

The interaction between client and server is not a single request, but an ongoing session.
TCP naturally supports a continuous, bidirectional stream of communication.

UDP, being connectionless, is not suitable for this type of structured session.
