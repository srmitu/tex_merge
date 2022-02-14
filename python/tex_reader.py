import os
import re
try:
    import fix_tex
except:
    from python import fix_tex

class TexReader():
    def __init__(self, root_tex: str, root_dir: str, fix_tex_class: fix_tex):
        self.root_tex = root_tex
        self.root_dir = root_dir
        self.fix_tex_class = fix_tex_class

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

    # self.root_texを読む
    def readRoot(self):
        with open(self.root_tex, mode='r',encoding="utf-8_sig") as root_tex_f:
            # \begin{document}以下の内容かどうか
            indoc_flag = False
            enddoc_flag = False

            for row, line in enumerate(root_tex_f):
                # subfileを読み込んでいる場合
                if line.strip().startswith('\\subfile'):
                    subfile_name = self.subfileCheck(line)
                    if subfile_name:
                        self.subfile(subfile_name)
                
                # 特殊コマンドが来た場合
                elif enddoc_flag and line.strip().startswith('\\setting{'):
                    command = re.sub('.+setting\{', '', line)
                    command = re.sub('\} *.*', '', command)
                    self.fix_tex_class.detectCommand(command.replace('\r', '').replace('\n', ''))

                elif not (enddoc_flag or re.search('newcommand', line) is None):
                    command = re.sub('( *%.*\n)|( *\n)', '', line)
                    new_command_list = [re.sub('( *%.*\n)|( *\n)', '', s) for s in self.lines if not re.search('newcommand', s) is None]
                    if not command in new_command_list:
                        self.lines.append(line)

                else:
                    # \begin{document}がきたら
                    if line.strip() == '\\begin{document}':
                        indoc_flag = True
                    # \end{document}がきたら
                    elif line.strip() == '\\end{document}':
                        indoc_flag = False
                        enddoc_flag = True
                    # \begin{document}~\end{document}の外
                    elif indoc_flag:
                        self.lines.append(line)
                    # \begin{document}~\end{document}の中
                    elif not (indoc_flag and enddoc_flag):
                        self.package.append(line)

      # root.texの\subfile{}を処理する部分
    def subfileCheck(self, line: str):
        # ディレクトリの構造が先にあげたようになっていないと正しく動かない
        subfile_name = re.split('[{}]', line)[1]
        subfile_name = subfile_name.replace('./' ,"")
        subfile_name = subfile_name.replace('.tex',"")
        subfile_tex = '{0}.tex'.format(subfile_name)

        print(self.blue + subfile_tex + self.end)
        # ファイルがない場合
        if not os.path.isfile(subfile_tex):
            print(self.red + "no file" + self.end)
            return -1
        else:
            return subfile_tex
    
    def subfile(self, subfile_tex: str):
        # \begin{docunemt}~\end{document}の中か
        is_inDocument: bool = False

        with open(subfile_tex, 'r', encoding="utf-8_sig") as subfile_tex_f:
            self.package.append('% ' + subfile_tex + ' で追加されたパッケージ\n')
            for line in subfile_tex_f:
                # \begin{document}~\end{document}内
                if is_inDocument:
                    # \end{}がきたら
                    if line.strip() == '\\end{document}':
                        self.lines.extend(['%------------------------------\n', '%\n', '% end ' + subfile_tex + '\n', 
                            '%\n', '%------------------------------\n'])
                        is_inDocument = False

                    # subfileを読み込んでいる場合
                    elif line.strip().startswith('\\subfile'):
                        subsubfile_tex = self.subfileCheck(line)
                        if subsubfile_tex and subfile_tex != subsubfile_tex:
                            self.subfile(subsubfile_tex)

                    # bibtexの設定に関する部分もスキップ(親でやるので)
                    elif line.strip().startswith('\\bib'):
                        pass
                    # それ以外は全てコピー
                    else:
                        line = line.replace('../../pic/', 'pic/') #merge.pyのビルドの都合
                        self.lines.append(line)

                # \begin{}~\end{}の外
                else:
                    # /begin{}が来るまで待機
                    if line.strip() == '\\begin{document}':
                        self.lines.extend(['%------------------------------\n', '%\n', '% start ' + subfile_tex + '\n', 
                            '%\n', '%------------------------------\n'])
                        is_inDocument = True
                    # 親で指定していないものがきた場合は追加 ただしshowkeysは無視, makeatother
                    elif not line.strip().startswith('%'):
                        package_no_comment = [re.sub('%.*', "", t.strip()) for t in self.package if t.find('%') != 0]
                        line_no_comment = re.sub('%.*| *%.*', "", line.strip())
                        if not (line_no_comment in package_no_comment or line_no_comment == '\\usepackage{showkeys}'):
                            print('add package', line.strip(), 'from', subfile_tex)
                            self.package.append(line_no_comment + "\n")

        # サブファイルのディレクトリのパス
        subfile_dir = os.path.dirname(subfile_tex)

        # subfileのディレクトリにbibファイルがある場合は，その絶対パスを取得
        for bib in os.listdir(subfile_dir):
            if os.path.splitext(bib)[1] == '.bib':
                self.biblist.append('{0}/{1}'.format(subfile_dir, bib.replace(".bib","")))