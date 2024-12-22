import socket
import threading

# Client settings
ServerIP = "127.0.0.1"
ServerPort = 5689
BufferSize = 1024

# Prompt the user for a player name
Name = input("Enter Player Name: ").strip()

# Create UDP socket
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Connect to the server by sending the username
ClientSocket.sendto(Name.encode(), (ServerIP, ServerPort))
print(f"Registered with the Trivia Game server at IP {ServerIP}, Port {ServerPort}.")
print("Waiting for the game to Start...\n")

# Flag to control the running of the client
running = True


def ListenToServer():
    """Listen for messages from the server and display them."""
    global running
    while running:
        try:
            # Receive a message from the server
            message, _ = ClientSocket.recvfrom(BufferSize)
            DecodedMessage = message.decode()

            # Display the server's message
            print(f"\nServer: {DecodedMessage}")

            # Handle question prompts
            if "Question" in DecodedMessage:
                # Prompt the user for an answer
                answer = input("Your Answer (or type 'exit' to quit): ").strip()
                if answer.lower() == "exit":
                    running = False
                    ClientSocket.close()
                    print("You have left the game.")
                    break
                ClientSocket.sendto(answer.encode(), (ServerIP, ServerPort))
                print("Answer submitted!")
        except socket.error:
            print("Error communicating with the server.")
            running = False
            break


# Start a thread to listen for server messages
thread = threading.Thread(target=ListenToServer, daemon=True)
thread.start()

try:
    while running:
        pass  # Keep the main thread running
except KeyboardInterrupt:
    print("Exiting the game.")
    running = False
    ClientSocket.close()