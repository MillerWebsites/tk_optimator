from typing import List
import random
 

VOWELS = ["ee", "oo", "aa", "eo", "ai", "uo", "uuu", "ooaa", "ru"]
CONSONANTS = ["t", "k", "p", "b", "d", "g", "m", "n", "h", "w", "y", "r", "s", "l"]
VOWEL = ["a", "e", "i", "o", "u", "y", "w"]

CONSONANT_COMBINATIONS = [
    "ch", "st", "sh", "th", "ph", "wh", "ch", "sh", "th", "ph", "wh", "ch", "sh", "th", "ph", "wh"
]

def generate_section(length: int) -> str:
    """Generates a section of the melody."""
    section = []
    for _ in range(length):
        vowel_combo = random.choice(VOWELS)
        if vowel_combo in ("ai", "eo", "ru"):
            vowel_combo += random.choice(VOWEL)
        consonant = random.choice(CONSONANT_COMBINATIONS) + random.choice(VOWEL)
        if consonant in ("h", "l"):
            consonant += random.choice(VOWEL)
            consonant += random.choice(CONSONANTS)
        suffix = random.choice(VOWEL) + " " + random.choice(CONSONANTS) + random.choice(VOWEL)
        section.append(consonant+vowel_combo + " "+ suffix)
    return " ".join(section)



def generate_variation() -> str:
    """Generates a half-length section."""
    section = []
    for _ in range(10):
        vowel_combo = random.choice(VOWELS)
        if vowel_combo in ("ai", "eo", "ru"):
            vowel_combo += random.choice(CONSONANTS) + " " +  random.choice(VOWEL)
        consonant = random.choice(CONSONANTS)
        if consonant == "h":
            consonant += random.choice(VOWEL)
            consonant += random.choice(CONSONANTS)
        elif consonant == "w":
            consonant += random.choice(VOWEL)
        suffix = random.choice(VOWEL) + " " + random.choice(CONSONANTS) + random.choice(VOWEL)
        section.append(consonant+vowel_combo+suffix)
    return " ".join(section)


def halve_length(melody: List[str]) -> List[str]:
    """Halves the length of the melody."""
    return [melody[i] for i in range(len(melody)) if i % 2 == 0]

def remove_letters(melody: List[str]) -> List[str]:
    """Removes the letters from the melody."""
    return [melody[i] for i in range(len(melody)) if not i % 2 == 0]


def generate_melody() -> List[str]:
    """Generates the melody."""
    return [generate_section(10) for _ in range(10)]

def transpose_letters(melody: List[str]) -> List[str]:
    """Transposes the letters in the melody."""
    return [melody[i].upper() for i in range(len(melody))]

def main() -> None:
    """Main function."""
    melody = generate_melody()      
    transposed_melody = transpose_letters(melody)
    halved_melody = halve_length(transposed_melody)
    removed_melody = remove_letters(melody)
    removed_halved_melody = remove_letters(halved_melody)
    removed_encore = remove_letters(generate_melody())

    final_melody = f"{removed_melody}, {removed_halved_melody}, {removed_encore}"


    print(melody)
    print(transposed_melody)
    print(halved_melody)
    print(removed_melody)
    print(removed_halved_melody)
    print(final_melody)


if __name__ == "__main__":
    main()


