#boyer-moore pattern matching
#intended for ctrl+f functionality for mailing list app
from PyQt5.QtWidgets import QApplication

NO_OF_CHARS = 256

def bad_char_heuristic(string, size):
    bad_char = [-1]*NO_OF_CHARS

    for i in range(size):
        bad_char[ord(string[i])] = i

    return bad_char

def search(text, pattern):
    pattern_size = len(pattern)
    text_size = len(text)

    bad_char = bad_char_heuristic(pattern, pattern_size)

    shift = 0
    while shift <= text_size - pattern_size:
        j = pattern_size - 1

        while j >= 0 and pattern[j] == text[shift + j]:
            j -= 1

        if j < 0:
            return True
            shift += (pattern_size - bad_char[ord(text[shift + pattern_size])] if shift + pattern_size < text_size else 1)
        else:
            shift += max(1, j-bad_char[ord(text[shift + j])])

    return False




def main():
    txt = "ABAAABCD"
    pattern = "ABC"
    search(txt, pattern)

if __name__ == "__main__":
    main()