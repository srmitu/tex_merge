import os
import sys
import re
import copy
try:
    import punctuation
except:
    from python import punctuation
try:
    import for_creating_csv
except:
    from python import for_creating_csv
try:
    import color_print
except:
    from python import color_print


class fixTex:
    def __init__(self):
        self.c_dic = {'typeset after merge': False, 'print comment': False, 'set comma': False, 'set period': False,
                        'clearpage before chapter': False, 'clearpage before section': False,
                        'clearpage before subsection': False, 'clearpage before subsubsection': False,
                        'clearpage before chapter*': False, 'clearpage before section*': False,
                        'clearpage before subsection*': False, 'clearpage before subsubsection*': False,
                        'generate ref.csv': False, 'fix punctuation': False, 'merged name: ': "thesis",
                        'error when there is no reference': False, 'display typeset log small': False,
                        'generate pdf after typeset': False}
        # \usepackage{}など，\begin{document}より前に書かれる内容のリスト
        self.package = list()
        # \begin{document} から \end{document}までの内容
        self.lines = list()
        # 参照元があるかのチェック用
        self.reference = True
        # 色と共に出力できるクラスをインスタンス化
        self.Color = color_print.ColorPrint()
    
    # 文書を校閲する
    def fixTex(self, lines: list, package: list):
        self.package = copy.deepcopy(package)
        self.lines = copy.deepcopy(lines)
        lines_use_command = [i for i, s in enumerate(self.lines) if '\\' in s and not '\\item' in s and not '$' in s]
        for i in lines_use_command:
            self.lines[i] = re.sub(' +{', '{', self.lines[i], 1)
            pass

        # 、や， 。や．を整える
        if self.c_dic['fix punctuation']:
            fix_punctuation = punctuation.fixPunctuationJapan(self.c_dic["set comma"], self.c_dic["set period"])
            self.lines = copy.deepcopy(fix_punctuation.fix(self.lines))
            self.package = copy.deepcopy(fix_punctuation.fix(self.package))

        # sectionなどの節目に改ページする(文書クラスの仕様は考慮していない)
        section_list = ['chapter', 'chapter*', 'section', 'section*', 'subsection', 'subsection*', 'subsubsection', 'subsubsection*'] 
        for section_name in section_list:
            if self.c_dic["clearpage before " + section_name]:
                section_list = [i for i, s in enumerate(self.lines) if s.strip().startswith("\\" + section_name +"{")]
                section_list.reverse()
                for section in section_list:
                    try:
                        if not '\\clearpage' in self.lines[section-1]:
                            raise ""
                    except:
                        self.lines.insert(section, "\\clearpage\n")
        
        if self.c_dic["generate ref.csv"]:
            LinesCommentOut = for_creating_csv.forCreatingCsv()
            comment_list = LinesCommentOut.detectLinesCommentOut(self.lines)
            self.reference = LinesCommentOut.generateRefCsv(self.lines, self.package, comment_list, self.file_name(), self.c_dic["error when there is no reference"])

        # コメントアウト(%から始まる行)を表示しない
        if not self.c_dic["print comment"]:
            LinesCommentOut = for_creating_csv.forCreatingCsv()
            comment_list = LinesCommentOut.detectLinesCommentOut(self.lines)
            for comment in comment_list:
                self.lines.pop(comment)
            comment_list = [i for i, s in enumerate(self.package) if s.strip().startswith('%')]
            comment_list.reverse()
            for comment in comment_list:
                self.package.pop(comment)

    # 特殊コマンド(\\setting)を認識する
    def detectCommand(self, command:str):
        if not self.c_dic.get(command) is None:
            self.c_dic[command] = True 
        elif command[0] == '!' and not self.c_dic.get(command[1:]) is None:
            self.c_dic[command[1:]] = False 
        # stringを入力するもの、何かの反転をするものを処理する
        else:
            return_d = -1
            if 'merged name: ' in command:
                self.c_dic['merged name: '] = command[12+1:] # "merged name: "を省く
                return_d = 0
            elif 'set toten' in command:
                self.c_dic['set comma'] = False if command[0] != '!' else True
                return_d = 0
            elif 'set kuten' in command:
                self.c_dic['set period'] = False if command[0] != '!' else True
                return_d = 0
            elif 'display typeset small log' in command:
                self.c_dic['display typeset log small'] = True if command[0] != '!' else False
                return_d = 0
            section_list = ['chapter', 'section', 'subsection', 'subsubsection'] 
            for section_name in section_list:
                if return_d != 0 and ('clearpage before ' + section_name + '* and ' + section_name in command or 'clearpage before ' + section_name + ' and ' + section_name + '*' in command):
                    self.c_dic['clearpage before ' + section_name] = True if command[0] != '!' else False
                    self.c_dic['clearpage before ' + section_name + '*'] = True if command[0] != '!' else False
                    return_d = 0
            if return_d:
                self.Color.printYellow("undefined command: " + command)
                return
        print("enable setting: " + self.Color.blue + command + self.Color.end)
    
    def file_name(self):
        return self.c_dic['merged name: ']
    def typeset(self):
        return self.c_dic['typeset after merge']
    def check_ref(self):
        return self.c_dic['error when there is no reference']
    def display_typeset_small(self):
        return self.c_dic['display typeset log small']
    def generate_pdf(self):
        return self.c_dic['generate pdf after typeset']

if __name__ == '__main__':
    file_name = sys.argv[1]
    fixTexC = fixTex()
    print("file_name:", file_name)
    if "--setting" in sys.argv:
        set_command_start = sys.argv.index("--setting")
        command_list = [s for i, s in enumerate(sys.argv) if i > set_command_start]
        for command in command_list:
            fixTexC.detectCommand(command)
    fixTexC.detectCommand('merged name: ' + file_name)
    print(sys.argv, fixTexC.c_dic)
    lines = []
    package = []
    in_document = False
    with open(file_name, mode = 'r', encoding = "utf-8_sig") as root_tex_f:
        for line in root_tex_f:
            if in_document:
                if not line.strip() == '\\end{document}':
                    lines.append(line)
                else:
                    break
            else:
                if line.strip() == '\\begin{document}':
                    in_document = True
                else:
                    package.append(line)
 
    fixTexC.fixTex(lines, package)
    
    lines_trimed = fixTexC.lines
    package_trimed = fixTexC.package
    with open(file_name, mode = 'w', encoding = "utf-8_sig") as root_tex_f:
        root_tex_f.write(''.join(package_trimed))
        root_tex_f.write('\n')
        root_tex_f.write('\\begin{document}\n')
        root_tex_f.write(''.join(lines_trimed))
        root_tex_f.write('\n')
        root_tex_f.write('\\end{document}\n')