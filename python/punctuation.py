import sys

class fixPunctuationJapan:
    def __init__(self, use_comma: bool=False, use_period: bool=False):
        self.use_comma = use_comma
        self.use_period = use_period

    def trim(self, sentence: list):
        for i, line in enumerate(sentence):
            if '、' or '，' in line:
                if self.use_comma:
                    sentence[i] = line.replace('、', '，')
                else:
                    sentence[i] = line.replace('，', '、')
        for i, line in enumerate(sentence):
            if '。' or '．'in line:
                if self.use_period:
                    sentence[i] = line.replace('。', '．')
                else:
                    sentence[i] = line.replace('．', '。')
        return sentence

if __name__ == '__main__':
    file_name = str(sys.argv[1])
    use_comma = True
    use_period = False
    if "--comma" in sys.argv and not("--toten" in sys.argv):
        use_comma = True
    elif "--touten" in sys.argv and not("--comma" in sys.argv):
        use_comma = False
    if "--period" in sys.argv and not("--kuten" in sys.argv):
        use_period = True
    elif "--kuten" in sys.argv and not("--period" in sys.argv):
        use_period = False
    
    with open(file_name, mode = 'r', encoding = "utf-8_sig") as root_tex_f:
        sentence = []
        for line in root_tex_f:
            sentence.append(line)
    trimer = fixPunctuationJapan(use_comma, use_period)
    sentence_trimd = trimer.trim(sentence)
    with open(file_name, mode = 'w', encoding = "utf-8_sig") as root_tex_f:
        root_tex_f.write(''.join(sentence_trimd))
