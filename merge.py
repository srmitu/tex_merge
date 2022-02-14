
# https://qiita.com/PaSeRi/items/22e7609b90af2d9379e1 
# にて考案されたtexファイルをマージするためのプログラムに変更を加えたもの
# ファイル分割にはsubfileを用いる

import os
import sys
import pathlib
import re
from python import fix_tex
from python import tex_reader
from python import typeset
import copy

class merger:

    # 引数として，root.texのフルパスとroot.texが含まれるディレクトリのパスが必要
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

        self.red = '\033[31m'
        self.green = '\033[32m'
        self.yellow = '\033[33m'
        self.blue = '\033[34m'
        self.end = '\033[0m'

        # \usepackage{}など，\begin{document}より前に書かれる内容のリスト
        self.package = list()
        # \begin{document} から \end{document}までの内容
        self.lines = list()
        # 各子ファイルが含まれるフォルダに存在する.bibファイルの絶対パス
        self.biblist = list()
    
    def start(self):
        fixTexC = fix_tex.fixTex()
        Reader = tex_reader.TexReader("root.tex", self.root_dir, fixTexC)
        Reader.readRoot()
        self.biblist = copy.deepcopy(Reader.biblist)
        self.createBib(fixTexC.file_name())
        fixTexC.fixTex(Reader.lines, Reader.package)
        self.lines = copy.deepcopy(fixTexC.lines)
        self.package = copy.deepcopy(fixTexC.package)
        self.createTex(fixTexC.file_name())
        if fixTexC.typeset():
            if (not fixTexC.check_ref()) or (fixTexC.check_ref() and fixTexC.reference):
                typesetC = typeset.typeset(fixTexC.file_name())
                typesetC.start_all(fixTexC.display_typeset_log(), fixTexC.display_typeset_small(), fixTexC.generate_pdf())
            elif fixTexC.check_ref() and (not fixTexC.reference):
                print(self.red + "参照元がないものが発見されたため、タイプセットを行いませんでした。", self.end)


    def createBib(self, file_name):
        # 統合後のbibファイル(file_name).bibを作成する.
        for i in range(2):
            try:
                with open(str(file_name) + '.bib', mode='x', encoding="utf-8_sig") as merged_bib_f:
                    for j in range(len(self.biblist)):
                        with open(self.root_dir + '/' + str(self.biblist[j]) + '.bib', mode='r', encoding="utf-8-sig") as sub_bib_f:
                            merged_bib_f.write('\n%%from ' + str(self.biblist[j]) + '.bib\n')
                            for bib_line in sub_bib_f:
                                merged_bib_f.write(bib_line)
            except FileExistsError:
                if i != 0:
                    print(self.yellow + '>>' + file_name + '.bib already exists. Please delete it first.' + self.end)
                merged_bib = os.path.join(self.root_dir, str(file_name) + '.bib')
                if os.path.isfile(merged_bib):
                    os.remove(merged_bib)
            except Exception as e:
                print(self.red + e + self.end)
                break
            else:
                print(self.green + file_name + ".bib have generated" + self.end)
                break

    def createTex(self, file_name):
        # 統合後のファイル(file_name).texを作成する.
        print_bibtex_list = [i for i, x in enumerate(self.lines) if "\\bibliography{}" in x]
        if print_bibtex_list:
            print("参考文献の表示")
            print_bibtex = print_bibtex_list[len(print_bibtex_list) - 1]

            self.lines[print_bibtex:print_bibtex+1] = ['\\clearpage\n', 
                self.lines[print_bibtex].replace('\\bibliography{}', '').replace('\n','') + '\n',
                '\\bibliographystyle{junsrt}\n', '\\bibliography{' + str(file_name) + '.bib}\n']
            #  違反している(最後以外の参考文献表示)を削除し、コメントアウトで警告する
            for index, value in enumerate(self.lines):
                if "\\bibliography{}" in value:
                    self.lines[index] = "% この文書内に参考文献を2回以上表示しようとしています" + value
                    print("Warning:", "この文書内に参考文献を2回以上表示しようとしています", value, index)
        else:
            print(self.blue + "自動的に参考文献を文末につけます" + self.end)
            self.lines.extend(['\\clearpage\n', 
                '\\section*{参考文献}\n', '\\bibliographystyle{junsrt}\n', 
                '\\bibliography{' + str(file_name) + '.bib}\n'])

        for i in range(2):
            try:
                with open(self.root_dir + '/' + str(file_name) + '.tex', mode='x', encoding="utf-8_sig") as merged_tex_f:
                    merged_tex_f.write(''.join(self.package))
                    merged_tex_f.write('\n')
                    merged_tex_f.write('\\begin{document}\n')
                    merged_tex_f.write(''.join(self.lines))
                    merged_tex_f.write('\n')
                    merged_tex_f.write('\\end{document}\n')
            except FileExistsError:
                if i != 0:
                    print('>>' + file_name + '.tex already exists. Please delete it first.')
                merged_tex = os.path.join(self.root_dir, str(file_name) + '.tex')
                if os.path.isfile(merged_tex):
                    try:
                        os.remove(merged_tex)
                    except:
                        pass
            except Exception as e:
                print(e)
                break
            else:
                print(self.green + file_name + ".tex have generated" + self.end)
                break
        print("本文スタート:", len(self.package)+3, "全文:", len(self.lines) + len(self.package) + 5)
        print(self.green + 'Finish!!!' + self.end)

   
            

if __name__ == '__main__':
    # 標準入力でroot.texの絶対パスをもらう
    root_tex = os.path.join(os.getcwd(), "root.tex")
    print(root_tex)
    # root.texの絶対パスから，親フォルダのパスだけ取得
    root_dir = os.path.dirname(root_tex)
    print(root_dir)
    # root.texの絶対パスと親フォルダのパスを引数に初期化
    merger = merger(root_dir)
    merger.start()

