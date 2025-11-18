import socket
import sys
import select



def validParentheses(word: str) -> bool:
    open = 0
    for s in word:
        if s == '(':
            open += 1
        elif s == ')':
            if open == 0:
                return False
            open -= 1
        else:
            return False
    return open == 0

def lcm(X: int, Y: int) -> int:
    smaller = min(X, Y)
    bigger = max(X, Y)
    for i in range(bigger, X * Y + 1, bigger):
        if i % smaller == 0:
            return i
    return X * Y

def caesar(plaintext: str, num: int) -> str:
    start = num
    res = []
    n = len(plaintext)
    for i in range(n):
        cur = plaintext[i]
        if 65 <= ord(cur) <= 90: # uppercase
            res.append(chr((ord(cur) - 65 + num) % 26 + 65))
        elif 97 <= ord(cur) <= 122: # lowercase
            res.append(chr((ord(cur) - 97 + num) % 26 + 97))
        elif ord(cur) == 32: # space
            res.append(" ")            
        else:
            return "invalid input"
    return "".join(res)

def send_all(sock: socket.socket, message: str):
    try:
        sock.sendall(message.encode())
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    if len(sys.argv) < 2:
        print("Not enough arguments given :(")
        sys.exit(1)

    users_file = sys.argv[1]
    valid_users = {}
    port = 1337
    # There is an optional port
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number.")
            sys.exit(1)
    try:
        with open(users_file, "r") as file:
            for line in file:
                if not line:
                    continue
                if "\t" in line:
                    parts = line.split("\t")
                if len(parts) != 2:
                    continue
                username = parts[0]
                password = parts[1]
                valid_users[username] = password
    except FileNotFoundError:
        print(f"Users file '{users_file}' not found.")
        sys.exit(1)

    # TCP listening socket creating
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen()

    inputs = [server_socket]
    clients = {}

    while True:
        client_sockets, _, _ = select.select(inputs, [], [])
        for sock in client_sockets:

            # new client connection
            if sock is server_socket:
                client_socket, addr = server_socket.accept()
                inputs.append(client_socket)
                clients[client_socket] = {'state': 'awaiting_username'}
                welcome_message = "Welcome! Please log in.\n"
                send_all(client_socket, welcome_message)
                continue

            # existing client message
            data = sock.recv(4096).decode()
            if not data:
                inputs.remove(sock)
                del clients[sock]
                sock.close()
                continue
                
            client_info = clients[sock]
            state = client_info['state']
            
             # quit connection
            if data.strip() == "quit":
                inputs.remove(sock)
                del clients[sock]
                sock.close()

            if state == 'awaiting_username':
                if data.startswith("User: "):
                    username = data[len("User: "):].strip()
                    client_info['username'] = username
                    client_info['state'] = 'awaiting_password'
                else:
                    error_message = "Failed to login\n"
                    sock.sendall(error_message.encode())
            
            elif state == 'awaiting_password':
                if data.startswith("Password: "):
                    password = data[len("Password: "):].strip()
                    username = client_info.get('username')
                    if username in valid_users and valid_users[username] == password:
                        success_message = "Hi " + username + ", good to see you\n"
                        sock.sendall(success_message.encode())
                        client_info['state'] = 'authenticated'
                    else:
                        failure_message = "Failed to login.\n"
                        sock.sendall(failure_message.encode())
                else:
                    error_message = "Failed to login.\n"
                    sock.sendall(error_message.encode())

            # authenticated state, commad phase
            elif state == 'authenticated':
                if data.startswith("caesar: "):
                    try:
                        command_content = data[len("caesar: "):].strip()
                        plaintext, shift_str = command_content.split(" ", 1)
                        shift = int(shift_str)
                        ciphertext = caesar(plaintext, shift)
                        if ciphertext == "invalid input":
                            error_message = "error: invalid input.\n"
                            sock.sendall(error_message.encode())
                            inputs.remove(sock)
                            del clients[sock]
                            sock.close()
                            continue
                        response = "Ciphertext: " + ciphertext + "\n"
                        sock.sendall(response.encode())
                    except Exception as e:
                        error_message = "Error\n"
                        sock.sendall(error_message.encode())
                        inputs.remove(sock)
                        del clients[sock]
                        sock.close()
                        continue

                if data.startswith("lcm: "):
                    try:
                        command_content = data[len("lcm: "):].strip()
                        x_str, y_str = command_content.split("   ")
                        x = int(x_str)
                        y = int(y_str)
                        result = lcm(x, y)
                        response = "LCM: " + str(result) + "\n"
                        sock.sendall(response.encode())
                    except Exception as e:
                        error_message = "Error processing LCM command.\n"
                        sock.sendall(error_message.encode())
                        inputs.remove(sock)
                        del clients[sock]
                        sock.close()

                if data.startswith("parentheses: "):
                    try:
                        command_content = data[len("parentheses: "):].strip()
                        result = validParentheses(command_content)
                        response = "Parentheses: " + str(result) + "\n"
                        sock.sendall(response.encode())
                    except Exception as e:
                        error_message = "Error processing Parentheses command.\n"
                        sock.sendall(error_message.encode())
                        inputs.remove(sock)
                        del clients[sock]   
                        sock.close()


            
            else:
                error_message = "Error processing Parentheses command.\n"
                sock.sendall(error_message.encode())
                inputs.remove(sock)
                del clients[sock]   
                sock.close()


        

                    




