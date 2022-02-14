import os
import subprocess
import traceback
import re
import sys
import time

class typeset:
    def __init__(self, project_name: str):
        print(project_name)
        self.file_name = project_name
        self.red = '\033[31m'
        self.green = '\033[32m'
        self.yellow = '\033[33m'
        self.blue = '\033[34m'
        self.end = '\033[0m'

    def remove_auto_generated_files(self, extensions: list):
        return_list = []
        for extension in extensions:
            try:
                os.remove(self.file_name + extension)
            except:
                return_list.append(extension)
                print("Warning: Failure to delete " + extension)
            time.sleep(0.1)
        return return_list

    def typeset(self, print_enable=False, small_display=False):
        end_count = 0
        end_flag = False
        return_d = 0
        try:
            # シェルコマンドを非同期で実行
            if os.name == "nt":
                # Windowsの場合
                print(self.blue + "platex " + self.file_name + ".tex" + self.end)
                proc = subprocess.Popen("platex " + self.file_name + ".tex", shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            else:
                proc = subprocess.Popen("exec platex " + self.file_name + ".tex", shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

            last_word = "" 
            while True:
                if not (end_count == 0 and end_flag):
                    line = proc.stdout.readline()
                else:
                    print(self.red + "Error: platex " + self.file_name + ".tex" + self.end)
                    proc.kill()
                    return_d = -1
                    break
                if line:
                    line_str = line.decode('utf-8')
                    m = re.search('( \.\.\.)|(\! Undefined control sequence\.)|\<inserted text\>', line_str)
                    if not m is None:
                        # エラーがあると停止するため、エラーの所を表示してからシェルコマンドを停止させる
                        end_count = 4
                        end_flag = True
                    m = re.search('\(Press Enter to retry, or Control-Z to exit\)', line_str)
                    if not m is None:
                        end_count = 1
                        end_flag = True
                    if end_flag:
                        print(self.red + line_str.replace('\r', '').replace('\n', '') + self.end)
                    else:
                        if print_enable and small_display:
                            if line_str == '\r\n' or line_str == '\n' or ' []' in line_str or len(line_str) < 8:
                                pass
                            else:
                                if line_str.strip().startswith("Underfull") or line_str.strip().startswith("Overfull") or line_str.strip().startswith("LaTeX Warning:"):
                                    word = self.yellow + line_str.replace('\r', '').replace('\n', '') + self.end
                                elif line_str.strip().startswith("(guessed encoding:"):
                                    word = self.green + line_str.replace('\r', '').replace('\n', '') + self.end
                                else:
                                    word = line_str.replace('\r', '').replace('\n', '')
                                space = " " * (len(last_word) + 10)
                                print(space, end='\r')
                                print(word, end='\r')
                                last_word = word
                        elif print_enable and not small_display:
                            if line_str.strip().startswith("Underfull") or line_str.strip().startswith("Overfull") or line_str.strip().startswith("LaTeX Warning"):
                                print(self.yellow + line_str.replace('\r', '').replace('\n', '') + self.end)
                            elif line_str.strip().startswith("(guessed encoding:"):
                                print(self.green + line_str.replace('\r', '').replace('\n', '') + self.end)
                            else:
                                print(line_str.replace('\r', '').replace('\n', ''))
                if end_count > 0:
                    end_count = end_count - 1
                if not line and proc.poll() is not None:
                    break
        except:
            traceback.print_exc()
            print(self.red + "Error: platex " + self.file_name + ".tex" + self.end)
            return_d = -1
        print('\n')
        return return_d

    def bibset(self, print_enable):
        return_d = 0
        try:
            # シェルコマンドを非同期で実行
            print(self.blue + "pbibtex " + self.file_name + self.end)
            proc = subprocess.Popen("pbibtex " + self.file_name, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            while True:
                line = proc.stdout.readline()
                if line:
                    line_str = line.decode('utf-8')
                    m = re.search('warning|Warning', line_str)
                    if not (m is None or m.span() != (0, 0)):
                            # リファレンスがないWarningと表示されるものがあった時にFalseを返すようにする
                            return_d = -1
                            print(self.yellow + line_str.replace('\r', '').replace('\n', '') + self.end)
                    else:
                        m = re.search('error', line_str)
                        if not m is None:
                            # リファレンスがないWarningと表示されるものがあった時にFalseを返すようにする
                            return_d = -1
                            print(self.red + line_str.replace('\r', '').replace('\n', '') + self.end)
                        elif print_enable:
                            print(line_str.replace('\r', '').replace('\n', ''))
                if not line and proc.poll() is not None:
                    break
        except:
            traceback.print_exc()
            print(self.red + "Error: pbibtex " + self.file_name + self.end)
            return_d = -1
        return return_d
    
    def dvipdfmx(self):
        return_d = 0
        try:
            # シェルコマンドを非同期で実行
            print(self.blue + "dvipdfmx " + self.file_name + self.end)
            proc = subprocess.Popen("dvipdfmx " + self.file_name, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            while True:
                line = proc.stdout.readline()
                if line:
                    line_str = line.decode('utf-8')
                    m = re.search('dvipdfmx:fatal', line_str)
                    if not m is None:
                        # 既にpdfを開いているので閉じる必要がある
                        return_d = -1
                        print(self.red + line_str.replace('\r', '').replace('\n', '') + self.end)
                        m = re.search('Unable to open ', line_str)
                        if type(m) is None and m.span() != (0, 0):
                            print(self.red + "pdfファイルを開いている可能性があります。閉じてください。" + self.end)
                    else:
                        print(line_str.replace('\r', '').replace('\n', ''))
                if not line and proc.poll() is not None:
                    break
        except:
            print("error")
            traceback.print_exc()
            print(self.red + "Error: pbibtex " + self.file_name + self.end)
            return_d = -1
        return return_d

    def tex2pdf(self, print_enable=False, small_display=False):
        end_count = 0
        end_flag = False
        return_d = 0
        try:
            # シェルコマンドを非同期で実行
            if os.name == "nt":
                # Windowsの場合
                print(self.blue + "ptex2pdf -l " + self.file_name + self.end)
                proc = subprocess.Popen("ptex2pdf -l " + self.file_name, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            else:
                proc = subprocess.Popen("exec ptex2pdf -l " + self.file_name, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

            last_word = "" 
            while True:
                if not (end_count == 0 and end_flag):
                    line = proc.stdout.readline()
                else:
                    print(self.red + "Error: platex " + self.file_name + ".tex" + self.end)
                    proc.kill()
                    return_d = -1
                    break
                if line:
                    line_str = line.decode('utf-8')
                    m = re.search('( \.\.\.)|(\! Undefined control sequence\.)', line_str)
                    if not m is None:
                        # エラーがあると停止するため、エラーの所を表示してからシェルコマンドを停止させる
                        end_count = 4
                        end_flag = True
                    m = re.search('\(Press Enter to retry, or Control-Z to exit\)', line_str)
                    if not m is None:
                        end_count = 1
                        end_flag = True
                    if end_flag:
                        print(self.red + line_str.replace('\r', '').replace('\n', '') + self.end)
                    else:
                        if print_enable and small_display:
                            if line_str == '\r\n' or line_str == '\n' or ' []' in line_str or len(line_str) < 8:
                                pass
                            else:
                                if line_str.strip().startswith("Underfull") or line_str.strip().startswith("Overfull") or line_str.strip().startswith("LaTeX Warning:"):
                                    word = self.yellow + line_str.replace('\r', '').replace('\n', '') + self.end
                                elif line_str.strip().startswith("(guessed encoding:"):
                                    word = self.green + line_str.replace('\r', '').replace('\n', '') + self.end
                                else:
                                    word = line_str.replace('\r', '').replace('\n', '')
                                space = " " * (len(last_word) + 10)
                                print(space, end='\r')
                                print(word, end='\r')
                                last_word = word
                        elif print_enable and not small_display:
                            print(line_str.replace('\r', '').replace('\n', ''))
                if end_count > 0:
                    end_count = end_count - 1
                if not line and proc.poll() is not None:
                    break
        except:
            traceback.print_exc()
            print(self.red + "Error: platex " + self.file_name + ".tex" + self.end)
            return_d = -1
        return return_d

    def start_all(self, print_enable=False, small_display=False, generate_pdf=False):
        remove_list = ['.aux', '.dvi', '.lof', '.log', '.toc']
        self.remove_auto_generated_files(remove_list)
        #if self.typeset(False):
        if self.typeset(True if small_display else False, small_display):
            return -1
        if self.bibset(print_enable and (not small_display)):
            return -1
        print_list = [True if small_display else False, print_enable]
        small_list = [small_display, False]
        return_d = 0
        #'''
        for i in range(2):
            if self.typeset(print_list[i], small_list[i]):
                return_d = 0
                break
        #'''
        if generate_pdf:
            if return_d == 0 and self.dvipdfmx():
                return -1
        return return_d

if __name__ == '__main__':
    file_name = sys.argv[1]
    typesetC = typeset(file_name)
    simple = False
    if "--simple" in sys.argv:
        simple = True
    if "--tex2pdf" in sys.argv:
        typesetC.tex2pdf(True, simple)
    else:
        typesetC.start_all(True, simple, True)
