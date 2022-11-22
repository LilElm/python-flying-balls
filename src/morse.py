

        
ENGLISH_TO_MORSE = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
                    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
                    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
                    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', ' ': '/', ',': '--..--', 
                    '.': '.-.-.-', '?': '..--..', '"': '.-..-.', ':': '---...', "'": '.----.', '-': '-....-',
                    '/': '-..-.', '(': '-.--.', ')': '-.--.-'}
    



MORSE_TO_ENGLISH = {}
for key, value in ENGLISH_TO_MORSE.items():
    MORSE_TO_ENGLISH[value] = key
    


def english_to_morse(message):
    message = message.upper()
    morse = []
    for char in message:
        if char in ENGLISH_TO_MORSE:
            morse.append(ENGLISH_TO_MORSE[char])
    return " ".join(morse)



def morse_to_english(message):
    message = message.split(" ")
    english = []
    for code in message:
        if code in MORSE_TO_ENGLISH:
            english.append(MORSE_TO_ENGLISH[code])
    return " ".join(english)



def morse_to_sig(message):
    
    """The dit duration is the basic unit of time measurement in Morse code transmission.
    The duration of a dah is three times the duration of a dit.
    
    Each dit or dah within an encoded character is followed by a period of signal absence,
    called a space, equal to the dit duration. The letters of a word are separated by a space
    of duration equal to three dits, and words are separated by a space equal to seven dits.[1]
    Until 1949, words were separated by a space equal to five dits.[5]"""
    
    #dit = 1
    #dah = dit * 3
    
    output = []
    
    for char in message:
        if char=='.':
           #signal on for dit
           #signal off for dit
           output.extend([True, False])
           pass
        elif char=='-':
            #signal on for dah
            #signal off for dit
            output.extend([True,True, True, False])
            pass
        elif char==' ':
            #signal off for dah
            output.extend([False, False, False])
            pass
        elif char=='/':
            #signal off for dit
            output.append(False)
            pass
            
    return output


