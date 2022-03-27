
class ColorPrint:
    def __init__(self):
        self.red = '\033[31m'
        self.green = '\033[32m'
        self.yellow = '\033[33m'
        self.blue = '\033[34m'
        self.end = '\033[0m'
    def printRed(self, *string, end="\n"):
        s = [str(i) for i in string]
        print(self.red + ' '.join(s) + self.end, end=end)
    def printGreen(self, *string, end="\n"):
        s = [str(i) for i in string]
        print(self.green + ' '.join(s) + self.end, end=end)
    def printYellow(self, *string, end="\n"):
        s = [str(i) for i in string]
        print(self.yellow + ' '.join(s) + self.end, end=end)
    def printBlue(self, *string, end="\n"):
        s = [str(i) for i in string]
        print(self.blue + ' '.join(s) + self.end, end=end)

if __name__ == '__main__':
    Color = ColorPrint()
    while True:
        Color.printGreen(input())