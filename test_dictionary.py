from dictionary_api import DictionaryAPI


def main():
    dictionary = DictionaryAPI()

    result = dictionary.search("hello")

    if result["success"]:
        print("Word:", result["word"])
        print("Phonetic:", result["phonetic"])
        print("Audio:", result["audio"])

        print("\nMeanings:")

        for meaning in result["meanings"]:
            print("\nPart of speech:", meaning["part_of_speech"])
            print("Definition:", meaning["definition"])
            print("Example:", meaning["example"])
            print("Synonyms:", meaning["synonyms"])
            print("Antonyms:", meaning["antonyms"])

    else:
        print("Error:", result["error"])


if __name__ == "__main__":
    main()
    