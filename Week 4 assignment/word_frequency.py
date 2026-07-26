text = """
Nepal is a beautiful country. Nepal has Mount Everest.
Everest is the highest mountain in the world. Many tourists
visit Nepal every year to see Everest and other mountains.
Nepal is known for its mountains and natural beauty.
"""

def word_frequency(text):

    text = text.lower()

    for symbol in [".", ",", "!", "?", "\n"]:
        text = text.replace(symbol, " ")

    words = text.split()

    frequency = {}

    for word in words:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1

    sorted_words = sorted(
        frequency.items(),
        key=lambda item: item[1],
        reverse=True
    )

    print("Top 3 words:")

    for word, count in sorted_words[:3]:
        print(f"{word} - {count} times")

word_frequency(text)