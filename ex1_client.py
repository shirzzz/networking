#!/usr/bin/python3

import socket
import sys


def parse_arguments():
    """
    Parse command-line arguments for hostname and port.
    Defaults: hostname = "localhost", port = 1337
    If one is provided, both must be provided.
    """
    hostname = "localhost"
    port = 1337
    
    if len(sys.argv) == 1:
        # No arguments - use defaults
        pass
    elif len(sys.argv) == 2:
        # Only one argument provided - invalid
        print("Error: If hostname is provided, port must also be provided.")
        sys.exit(1)
    elif len(sys.argv) == 3:
        # Both hostname and port provided
        hostname = sys.argv[1]
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Error: Port must be a valid integer.")
            sys.exit(1)
    else:
        # Too many arguments
        print("Error: Too many arguments.")
        print("Usage: ./ex1_client.py [hostname [port]]")
        sys.exit(1)
    
    return hostname, port


def receive_message(sock, buffer_size=4096):
    """
    Receive a complete message from the socket.
    Returns the decoded string, or None if connection is closed.
    """
    data = sock.recv(buffer_size)
    if not data:  # Empty bytes means connection closed
        return None
    return data.decode()


def send_message(sock, message):
    """
    Send a complete message to the socket.
    """
    sock.sendall(message.encode())


def authenticate(sock):
    """
    Handle the authentication flow:
    1. Receive welcome message
    2. Prompt user for username and password
    3. Send credentials
    4. Receive and handle login response
    Returns True if authentication successful, False otherwise.
    """
    # Receive welcome message
    welcome = receive_message(sock)
    if welcome is None:
        return False
    
    print(welcome.rstrip())
    while True:
        # Prompt for username
        username = input("User: ").strip()
        
        # Prompt for password
        password = input("Password: ").strip()
        
        # Send credentials
        send_message(sock, f"User: {username}\n")
        send_message(sock, f"Password: {password}\n")
        
        # Receive login response
        response = receive_message(sock)
        if response is None:
            return False
        
        print(response.rstrip())
        
        # Check if login was successful
        if not "Failed to login." in response:
            return True
    


def main():
    """Main function to run the client."""
    # Parse command-line arguments
    hostname, port = parse_arguments()
    
    # Create TCP socket and connect
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((hostname, port))
    except OSError as e:
        print(f"Error connecting to server: {e}")
        client_socket.close()
        sys.exit(1)
    
    # Authenticate
    if not authenticate(client_socket):
        client_socket.close()
        sys.exit(1)
    
    # Command loop
    try:
        while True:
            # Read user input
            user_input = input().strip()
            
            # Send command to server
            send_message(client_socket, user_input + "\n")
            
            # Handle quit command
            if user_input == "quit":
                break
            
            # Receive and display response
            response = receive_message(client_socket)
            if response is None:
                break
            
            print(response.rstrip())
    
    except (KeyboardInterrupt, EOFError, OSError):
        pass
    finally:
        # Close socket
        client_socket.close()


if __name__ == "__main__":
    main()

