import re
import sys
import os
import copy
import csv
try:
    import color_print
except:
    from python import color_print

class forCreatingCsv:
    def __init__(self):
        # 色と共に出力できるクラスをインスタンス化
        self.Color = color_print.ColorPrint()
        
    def detectLinesCommentOut(self, lines: list):
        self.lines = copy.deepcopy(lines)
        begin_comment_list = [i for i, s in enumerate(self.lines) if not re.search("(?<!%)\\\\begin\{comment\}", s.replace(" ","")) is None]
        end_comment_list = [i for i, s in enumerate(self.lines) if not re.search("(?<!%)\\\\end\{comment\}", s.replace(" ", "")) is None]
        comment_out_list = [i for i, s in enumerate(self.lines) if s.strip().startswith('%')]
        comment_list = []
        if not len(begin_comment_list) == len(end_comment_list):
            self.Color.printRed("Error: {comment}環境の数がおかしいです。begin及びendの位置を確認してください")
        for i, s in enumerate(begin_comment_list):
            if end_comment_list[i] < s:
                self.Color.printRed("Error: end{comment}がbegin{comment}より前にあります")
                sys.exit()
            elif end_comment_list[i] == s:
                print("yes")
                print(self.lines[s].find("begin") , self.lines[s].find("end"))
                if self.lines[s].find("begin") > self.lines[s].find("end"):
                    self.Color.printRed("Error: end{comment}がbegin{comment}より前にあります")
                    sys.exit()
            else:
                comment_list.extend(list(range(s, end_comment_list[i])))
        comment_list.extend(comment_out_list)
        comment_list = copy.deepcopy(list(set(comment_list)))
        comment_list.sort(reverse=True)
        return comment_list

    def generateRefCsv(self, lines: list, package: list, comment_list: list, file_name: str, wake_error_when_no_ref):
        self.lines = copy.deepcopy(lines)
        self.package = copy.deepcopy(package)
        ref_list = [[] for _ in range(2)]
        cite_list = [[] for _ in range(2)]
        label_list = [[] for _ in range(2)]
        key_list = [[] for _ in range(2)]
        ref_list_b = [[i for i, s in enumerate(self.lines) if not re.search("(\\\\|\\\\page)ref\{", s) is None],
                        [re.finditer("(?<=ref)\{[^\}]+\}", s) for i, s in enumerate(self.lines) if not re.search("(\\\\|\\\\page)ref\{", s) is None]]
        cite_list_b = [[i for i, s in enumerate(self.lines) if not re.search("\\\\cite\{", s) is None],
                        [re.finditer("(?<=cite)\{[^\}]+\}", s) for i, s in enumerate(self.lines) if not re.search("\\\\cite\{", s) is None]]
        label_list_b = [[i for i, s in enumerate(self.lines) if not re.search("\\\\label\{", s) is None],
                        [re.finditer("(?<=label)\{[^\}]+\}", s) for i, s in enumerate(self.lines) if not re.search("\\\\label\{", s) is None]]
        label_list_b[0].extend([i for i, s in enumerate(self.lines) if not re.search("begin\{lstlisting\}\[[^\]]+label\=[^\]]+]", s) is None])
        label_list_b[1].extend([re.finditer("(?<=label\=)[^\]]+\]", s) for i, s in enumerate(self.lines) if not re.search("begin\{lstlisting\}\[[^\]]+label\=[^\]]+]", s) is None] )
                
        key_list_b = []
        sentence = []
        with open(file_name + ".bib", mode = 'r', encoding = "utf-8_sig") as bib_f:
            for line in bib_f:
                sentence.append(line)
        key_list_b = [i + 1 for i, s in enumerate(sentence) if not re.search("@.+\{", s) is None]
        # (page)ref
        for i, s in enumerate(ref_list_b[1]):
            for m in s:
                if not ref_list_b[0][i] in comment_list:
                    ref_list[0].append(ref_list_b[0][i])
                    ref_list[1].append(m.group().replace('{', '').replace('}', ''))
        # cite
        for i, s in enumerate(cite_list_b[1]):
            for m in s:
                if not cite_list_b[0][i] in comment_list:
                    cite_list[0].append(cite_list_b[0][i])
                    cite_list[1].append(m.group().replace('{', '').replace('}', ''))
        # label
        for i, s in enumerate(label_list_b[1]):
            for m in s:
                if not label_list_b[0][i] in comment_list:
                    label_list[0].append(label_list_b[0][i])
                    label_list[1].append(m.group().replace('{', '').replace('}', '').replace(']', ''))
        # bib
        for i, s in enumerate(key_list_b):
            key_list[0].append(s)
            key_list[1].append(sentence[s].strip().replace(",", ""))
        # labelの重複がある場合はエラーを起こす
        label_duplicate_list = [s for s in set(label_list[1]) if label_list[1].count(s) > 1]
        if label_duplicate_list:
            for label_duplicate in label_duplicate_list:
                match = [label_list[0][i] for i, s in enumerate(label_list[1]) if s == label_duplicate]
                self.Color.printRed("Error: \label{" + label_duplicate + "}の定義が重複しています↓")
                print(match)
            sys.exit()
        # keyの重複がある場合はエラーを起こす
        key_duplicate_list = [s for s in set(key_list[1]) if key_list[1].count(s) > 1]
        if key_duplicate_list:
            for key_duplicate in key_duplicate_list:
                match = [key_list[0][i] for i, s in enumerate(key_list[1]) if s == key_duplicate]
                self.Color.printRed("Error: " + file_name +" .bib内で" + key_duplicate + "の定義が重複しています↓")
                print(match)
            sys.exit()
        with open(file_name + "_ref.csv", mode = 'w', encoding = "utf-8_sig") as f:
            writer = csv.writer(f, lineterminator="\n")
            # cite - keyの関係を洗い出す
            writer.writerow(["<key-citeの関係>"])
            writer.writerow(["key", ".bibでの定義場所", "citeでの参照場所(mergeされた後の.tex)"])
            cite_key_relation_list_b = []
            for i, key in enumerate(key_list[1]):
                cite_key_relation_list_b.append([key, key_list[0][i] + 1, [cite_list[0][j] for j, s in enumerate(cite_list[1]) if s == key]])
            cite_key_relation_list = self.sortForCsv(cite_key_relation_list_b)
            for i, s in enumerate(cite_key_relation_list):
                writer.writerow(s)
                for j in s[2]:
                    writer.writerow([j, self.lines[j].replace("\r", "").replace("\n", "")])
                    writer.writerow([])
            writer.writerow([])
            # (page)ref - labelの関係を洗い出す
            writer.writerow(["<label-refの関係>"])
            writer.writerow(["label", "mergeされた後の.texでの定義場所", "(page)refでの参照場所(mergeされた後の.tex)"])
            ref_label_relation_list_b = []
            for i, label in enumerate(label_list[1]):
                ref_label_relation_list_b.append([label, label_list[0][i] + 1, [ref_list[0][j] for j, s in enumerate(ref_list[1]) if s == label]])
            ref_label_relation_list = self.sortForCsv(ref_label_relation_list_b)
            for i, s in enumerate(ref_label_relation_list):
                writer.writerow(s)
                for j in s[2]:
                    writer.writerow([j, self.lines[j].replace("\r", "").replace("\n", "")])
                    writer.writerow([])
            writer.writerow([])
            writer.writerow(["参照先がないもの"])
            self.reference = True
            # labelのないrefでの参照を探す
            for i, ref in enumerate(ref_list[1]):
                if not ref in label_list[1]:
                    writer.writerow([ref, ref_list[0][i] + len(self.package) + 3])
                    writer.writerow([self.lines[ref_list[0][i]].replace("\r", "").replace("\n", "")])
                    writer.writerow([])
                    self.Color.printYellow("Warning:", ref, "の\\refまたは\\pagerefは参照元がありません")
                    print(self.lines[ref_list[0][i]].replace("\r", "").replace("\n", ""))
                    self.reference = False
            # keyのないciteでの参照を探す
            for i, cite in enumerate(cite_list[1]):
                if not cite in key_list[1]:
                    writer.writerow([ref, cite_list[0][i] + len(self.package) + 3])
                    writer.writerow([self.lines[cite_list[0][i]].replace("\r", "").replace("\n", "")])
                    writer.writerow([])
                    self.Color.printYellow("Warning:", cite, "の\\citeは参照元がありません")
                    print(self.lines[cite_list[0][i]].replace("\r", "").replace("\n", ""))
                    self.reference = False
            if not self.reference:
                if wake_error_when_no_ref:
                    self.Color.printRed("参照元がないpagerefまたはrefまたはciteがありました")
            else:
                writer.writerow(["なし"])
            return self.reference
    def sortForCsv(self, before_sort: list):
        list_for_sort = []
        sorted_list = []
        for s in before_sort:
            list_for_sort.append(s[0])
        list_for_sort.sort()
        for sorted in list_for_sort:
            for s in before_sort:
                if sorted == s[0]:
                    sorted_list.append(s)
                    break
        return sorted_list