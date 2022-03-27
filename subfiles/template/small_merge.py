
# https://qiita.com/PaSeRi/items/22e7609b90af2d9379e1 
# にて考案されたtexファイルをマージするためのプログラムに変更を加えたもの
# ファイル分割にはsubfileを用いる

import os
import sys
import pathlib
import re
import glob
sys.path.append('../../')
from python import fix_tex
from python import tex_reader
from python import typeset
from python import color_print
import copy

class smallMerger:

    # 引数として，root.texのフルパスとroot.texが含まれるディレクトリのパスが必要
    def __init__(self, root_dir: str, root_tex: str, set_pic_dir, set_pdf_dir):
        self.root_tex = root_tex
        self.root_dir = root_dir
        self.set_pic_dir = set_pic_dir
        self.set_pdf_dir = set_pdf_dir

        # \usepackage{}など，\begin{document}より前に書かれる内容のリスト
        self.package = list()
        # \begin{document} から \end{document}までの内容
        self.lines = list()
        # 各子ファイルが含まれるフォルダに存在する.bibファイルの絶対パス
        self.biblist = list()
        # 色と共に出力できるクラスをインスタンス化
        self.Color = color_print.ColorPrint()
    
    def start(self):
        fixTexC = fix_tex.fixTex()
        Reader = tex_reader.TexReader(self.root_tex, self.root_dir, fixTexC)
        Reader.readRoot()
        self.biblist = copy.deepcopy(Reader.biblist)
        # ref.csvは強制的に作らせない
        fixTexC.c_dic["generate ref.csv"] = False
        fixTexC.fixTex(Reader.lines, Reader.package)
        self.lines = copy.deepcopy(fixTexC.lines)
        self.package = copy.deepcopy(fixTexC.package)
        # picのパスを変更する
        temp_line = list()
        for line in self.lines:
            temp_line.append(line.replace('pic/', self.set_pic_dir).replace('pdf/', self.set_pdf_dir))
        self.lines = copy.deepcopy(temp_line)
        self.createTex(fixTexC.file_name())
        if fixTexC.typeset():
            if (not fixTexC.check_ref()) or (fixTexC.check_ref() and fixTexC.reference):
                typesetC = typeset.typeset(fixTexC.file_name())
                if not typesetC.typeset(fixTexC.display_typeset_log(), fixTexC.display_typeset_small(), False):
                    sys.exit()
                if fixTexC.generate_pdf():
                    if not typesetC.tex2pdf(True, False, fixTexC.generate_pdf()):
                        sys.exit()
                else:
                    if not typesetC.typeset(True, False, True):
                        sys.exit()
            elif fixTexC.check_ref() and (not fixTexC.reference):
                self.Color.printRed("参照元がないものが発見されたため、タイプセットを行いませんでした。")

    def createTex(self, file_name):
        # 統合後のファイル(file_name).texを作成する.
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
                self.Color.printGreen(file_name + ".tex have generated")
                break
        print("本文スタート:", len(self.package)+3, "全文:", len(self.lines) + len(self.package) + 5)
        self.Color.printGreen('Finish!!!')

   
            

if __name__ == '__main__':
    Color = color_print.ColorPrint()
    # picディレクトリ
    set_pic_dir_search = '**/pic/'
    pic_dir_nominatin = list()
    for i in range(5):
        pic_dir_nominatin = glob.glob(('..//' * i) + set_pic_dir_search, recursive=True)
        print(pic_dir_nominatin)
        if pic_dir_nominatin:
            break
    if not pic_dir_nominatin:
        Color.printYellow("picディレクトリを発見できません")
    elif len(pic_dir_nominatin) > 1:
        Color.printRed("picディレクトリが複数あります。")
        sys.exit()
    set_pic_dir = pic_dir_nominatin[0].replace("\\", "/").replace("//", "/") # 該当するものは一つのみ
    print(set_pic_dir)

    # pdfディレクトリ
    set_pdf_dir_search = '**/pdf/'
    pdf_dir_nominatin = list()
    for i in range(5):
        pdf_dir_nominatin = glob.glob(('..//' * i) + set_pdf_dir_search, recursive=True)
        print(pdf_dir_nominatin)
        if pdf_dir_nominatin:
            break
    if not pdf_dir_nominatin:
        Color.printYellow("pdfディレクトリを発見できません")
    elif len(pdf_dir_nominatin) > 1:
        Color.printRed("pdfディレクトリが複数あります。")
        sys.exit()
    set_pdf_dir = pdf_dir_nominatin[0].replace("\\", "/").replace("//", "/") # 該当するものは一つのみ
    print(set_pdf_dir)

    # 標準入力でroot.texの絶対パスをもらう
    root_nomination_files = glob.glob('root_?*.tex')
    if len(root_nomination_files) > 1:
        Color.printRed("root_と先頭につくものは一つにしてください。")
        sys.exit()
    elif len(root_nomination_files) == 0:
        Color.printRed("root_と先頭につくものを用意してください。")
        sys.exit()
    root_file = root_nomination_files[0] # 該当するものは一つのみ
    root_tex = os.path.join(os.getcwd(), root_file)
    print(root_tex)
    # root.texの絶対パスから，親フォルダのパスだけ取得
    root_dir = os.path.dirname(root_tex)
    print(root_dir)
    # root.texの絶対パスと親フォルダのパスを引数に初期化
    smallMerger = smallMerger(root_dir, root_tex, set_pic_dir, set_pdf_dir)
    smallMerger.start()

