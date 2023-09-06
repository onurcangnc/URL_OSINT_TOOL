# Read the word list from the file into a list
with open("wordlist.txt", "r") as file:
    word_list = [line.strip() for line in file]

# Remove duplicates using a set
unique_words = list(set(word_list))

# Write the unique words back to the file
with open("wordlist.txt", "w") as file:
    file.write("\n".join(unique_words))
