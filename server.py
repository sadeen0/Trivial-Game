import socket
import time
import threading
import random

# Server Settings
ServerIP = "127.0.0.1"
ServerPort = 5689  # Port Number
BufferSize = 1024  # The size of data that can be sent or received

# Client Data
Clients = {}  # A dictionary to store client data with IP address and port as keys
RoundInProgress = False  
LockGame = threading.Lock()  
WaitingClients = True  # Server waits for player connections
log = []  # To store logs of messages broadcast to all clients

# Pre-stored questions
questions = [
    {"question": "What does the abbreviation 'HTTP' stand for?", "answer": "HyperText Transfer Protocol"},
    {"question": "Who is known as the father of the computer?", "answer": "Charles Babbage"},
    {"question": "What year was the first iPhone released?", "answer": "2007"},
    {"question": "What does 'AI' stand for?", "answer": "Artificial Intelligence"},
    {"question": "What programming language is primarily used for web development on the front end?", "answer": "JavaScript"},
    {"question": "Which company developed the Windows operating system?", "answer": "Microsoft"},
    {"question": "What is the full form of 'USB'?", "answer": "Universal Serial Bus"},
    {"question": "Who founded the company Tesla?", "answer": "Elon Musk"},
    {"question": "What does 'Wi-Fi' stand for?", "answer": "Wireless Fidelity"},
    {"question": "What is the most popular social media platform in the world?", "answer": "Facebook"},
    {"question": "What is the name of the virtual assistant developed by Apple?", "answer": "Siri"},
    {"question": "What is the most popular web browser?", "answer": "Google Chrome"},
    {"question": "What does 'LOL' stand for?", "answer": "Laugh Out Loud"},
]

QuestionsPerRound = 3  # The number of questions in each round

# Function to broadcast a message to all clients
def broadcast(message):
    """Send a message to all connected clients and store it in the log"""
    log.append(message)  
    for client in Clients.keys():  # Iterate through all clients
        ServerSocket.sendto(message.encode(), client)  # Send the message to the client

# Function to format the scores for display
def FormatScores():
    """Format the scores to display them in an organized manner"""
    sorted_clients = sorted(Clients.values(), key=lambda x: x["score"], reverse=True)  # Sort clients by score
    scores = "\n".join([f"\t - {client['name']}: {client['score']} points" for client in sorted_clients])  # Format the scores
    return f"  Current Scores:\n{scores}"  

# Function to start the round
def StartRound():
    """Initialize and start the game rounds"""
    global RoundInProgress
    RoundNum = 0  # Round number 

    while len(Clients) > 1:  # Continue the rounds until only one player is left
        RoundInProgress = True  # Indicate that the round is in progress
        RoundNum += 1  

        broadcast(f"Starting Round {RoundNum} in 30 seconds! Get ready!") 
        print(f"Starting Round {RoundNum} in 30 seconds! Get ready!")  
        time.sleep(30)  # Wait for 30 seconds before starting the round

        # Select random questions for this round
        SelectedQuestions = random.sample(questions, QuestionsPerRound)  # Select random questions

        for QuestionIndex, Q in enumerate(SelectedQuestions, start=1): 
            Question = Q["question"]  # The question
            TrueAnswer = Q["answer"]  # The correct answer
            broadcast(f"Question {QuestionIndex}: {Question}")  # Broadcast the question to all players
            print(f"\n\nQuestion {QuestionIndex}: {Question}")  # Print the question to the log

            StartTime = time.time()  
            AllAnswers = {}  # A dictionary to store answers from all players
            while time.time() - StartTime < 35:  # Wait for answers for 90 seconds
                try:
                    data, addr = ServerSocket.recvfrom(BufferSize)  # Receive the answer from the client
                    Answer = data.decode()  # Convert the answer to text

                    if Answer.lower() == "exit":  # If the player wants to exit the game
                        print(f"Player {Clients[addr]['name']} exited the game.")
                        del Clients[addr]  # Remove the player from the clients list
                        broadcast(f"{Clients[addr]['name']} has left the game.")  # Broadcast that the player left the game
                        continue

                    if addr not in Clients:  # If the player is new
                        Clients[addr] = {"name": Answer, "score": 0.0, "rounds_won": 0}  # Add the player to the clients
                        print(f"{Answer} joined the game from {addr}") 
                        broadcast(f"{Answer} has joined the game!")  # Broadcast that the player joined the game
                        broadcast(f"Current Number of Players: {len(Clients)}")  # Broadcast the current number of players

                        # Send the current question to the new player
                        ServerSocket.sendto(f"Question {QuestionIndex}: {Question}".encode(), addr)
                        continue

                    # Record the answers for all players
                    if addr not in AllAnswers:
                        AllAnswers[addr] = []

                    AllAnswers[addr].append(Answer)  # Add the answer to the recorded answers

                    # Determine if the answer is correct
                    IsCorrect = Answer.strip().lower() == TrueAnswer.lower()  # Check the answer
                    Time = time.time() - StartTime  # Calculate how much time the player took to answer
                    
                    # Award points: Bonus points if answered within 10 seconds
                    if IsCorrect:
                        if Time <= 10:
                            Clients[addr]["score"] += 1.4  # Award bonus points for quick answers
                            status = "Correct (Bonus)"
                        else:
                            Clients[addr]["score"] += 1  # Regular points for answers after 10 seconds
                            status = "Correct"
                    else:
                        status = "Incorrect"

                    # Print the answer status
                    print(f"Received answer from {Clients[addr]['name']} ({addr}): {Answer} - {status} s")
                except socket.timeout:
                    continue

            # After time is up, display the correct answers to all players
            broadcast(f"TIME'S UP! The correct answer was: {TrueAnswer}")
            print(f"\nCorrect Answer: {TrueAnswer}")  # Print the correct answer

            # Display the scores after each question
            broadcast(FormatScores())
            print("\nCurrent Scores after Question:")
            print(FormatScores())  # Print the scores after each question

        # Display the winner of the round based on the points
        RoundWinner = max(Clients.items(), key=lambda x: x[1]["score"])[1]  # Find the winner
        broadcast(f"Round {RoundNum} Winner: {RoundWinner['name']} with {RoundWinner['score']} points!")  # Broadcast the round winner
        print(f"Round {RoundNum} Winner: {RoundWinner['name']} with {RoundWinner['score']} points!")  
        RoundInProgress = False  # End the round
        
    # Handle the case when only one player is left
    if len(Clients) == 1:
        RemainingPlayer = list(Clients.values())[0]  # Get the remaining player
        broadcast(f"You are the Only Player Remaining, {RemainingPlayer['name']}. Wait!") 
        print(f" Player {RemainingPlayer['name']} is the only one left. Waiting for more players.") 

# Create a UDP socket for the server
ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ServerSocket.bind((ServerIP, ServerPort))  # Bind the server to the IP address and port
ServerSocket.settimeout(1)  # Set the timeout to 1 second
print(f"Server started on {ServerIP}:{ServerPort}")  # Print that the server has started

while True:
    try:
        data, addr = ServerSocket.recvfrom(BufferSize)  # Receive data from the client
        Message = data.decode()  # Convert the received data to text

        if addr not in Clients:  # If the client is new
            Clients[addr] = {"name": Message, "score": 0.0, "rounds_won": 0}  # Add the client to the list of clients
            print(f"{Message} joined the game from {addr}")  
            broadcast(f"{Message} has joined the game!")  #
            broadcast(f"Current Number Of Players: {len(Clients)}")  

            with LockGame:
                if len(Clients) >= 2 and not RoundInProgress:  # Start the round if there are at least two players
                    WaitingClients = False
                    threading.Thread(target=StartRound).start() 
    except socket.timeout:
        if len(Clients) < 2 and WaitingClients:  # Wait for players if there aren't enough players
            print("     Waiting for at least 2 Clients to join the game...")
            time.sleep(7)  # Wait for 7 seconds before retrying
