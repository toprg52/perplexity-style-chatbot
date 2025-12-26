from services import generate_search_query

# Mock History: User asked about Quantum Physics
mock_history = [
    {"role": "user", "content": "Explain Quantum Physics"},
    {"role": "assistant", "content": "Quantum physics is a branch of physics that deals with the behavior of matter and light on the atomic and subatomic scale..."}
]

user_input = "explain in detail. give yt tutorials if any"

print(f"History Length: {len(mock_history)}")
print(f"User Input: {user_input}")

refined = generate_search_query(mock_history, user_input)

print("-" * 20)
print(f"Refined Query: {refined}")
print("-" * 20)
