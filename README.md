# tex_merge
このリポジトリでは`\subfile`を使用した分割ファイルによって一つのpdfファイルを生成する。

ファイルのmergeにはhttps://qiita.com/PaSeRi/items/22e7609b90af2d9379e1 にて公開されているmerge.pyを改良したものを利用している。

## ファイル構成
()内は現在のコミットでは存在しないが必要となるディレクトリである。
├─root.tex　// 親ファイル<br>
├─  subfiles　// 子ファイルを保存するディレクトリ<br>
│ ├─  template<br>
| | ├─  small_merge.py<br> // 小規模で子ファイルをマージする 
│ │ └─  template.tex<br>
│ ├─  (hoge)<br>
│ │ ├─  (hoge.tex)<br>
│ │ └─  (hoge.bib)<br>
│ │<br>
│<br>
│<br>
├─  (pic) // 写真を保存するディレクトリ<br>
├─  python<br>
│     ├─  fix_tex.py // .texを校正する<br>
│     ├─  for_creating_csv.py // fix_tex.pyで使うcsvファイルを作成するコードをまとめる<br>
│     ├─  punctuation.py // ,や.を整える(全角)<br>
│     ├─  tex_reader.py // root.texや子ファイルを読む<br>
│     └─  typeset.py // タイプセットする<br>
│     
└─  merge.py // 子ファイルをマージしたりなんやかんやする

## フォーマットについて

### 親ファイル
**親ファイルはroot.texでなければならない**。`\subfile`で子ファイルを読み込みマージさせる。
基本的に、root.tex単体でタイプセットすることは不可能。
`\bibliography{}`と書いた位置に参考文献が表示される。
`\end{document}`の後に`\setting`コマンド(自作)を指定することでmergeの際の設定をすることができる。このコマンドはroot.texでのみ指定可能である。
```
% 例
\documentclass[12pt]{jarticle}
\usepackage[dvipdfmx]{graphicx}
......

\begin{document}
......
\subfile{subfiles/hoge/hoge.tex}
......
\bibliography{} % 参考文献を表示する

\end{document}
\setting{typeset after merge}
```


### 子ファイル
子ファイルはsubfilesの中に格納する。子ファイルごとにディレクトリを作ることを推奨する。子ファイルはそれ単体でタイプセットすることができる。`\usepackage{showkeys}`を`\begin{document}`の前に置く。これをすることで、子ファイルのみでタイプセットをした際には相互参照によるエラーが起きず、mergeした後のファイルでは正しく相互参照ができる(`\usepackage{showkeys}`はmergeの際に無視される)。root.texの``\begin{document}``より前と同じコードがかかれている場合はmergeされない。子ファイルの中に`\subfile`コマンドを指定することは可能。写真を指定する場合は、`../../pic/`で指定する。mergeする際には`pic/`に変換される。`\newcommand`を使用しており、他の子ファイルでも同じものを使っている場合はmergeする際に、一つのみ残る。

**子ファイルに`\makeatother`はroot.tex以外で指定していないコマンドを除いて指定してはいけない**。

```
% 例
\documentclass[12pt]{jarticle} % root.texで指定している場合は無視される
\usepackage{comment} % root.texで指定されてない場合はmergeされる
......
%\makeatother
%\left\@makecaption\Mycaption % root.texで指定していないのであれば基本的に指定しない
%\makeatother
\usepackage{showkeys} % 確定で無視される
\begin{document}
......
% 図を挿入する
\begin{figure}[htbp]
  \centering
  \includegraphics[width = 10cm]{../../pic/hoge.png} % ../../pic/で指定する
  \caption{fuga}
  \label{fig: piyo}
\end{figure}
......
\ref{sec: 別の子ファイルのセクション}節で挙げた問題点は...... % 別の子ファイルで定義しているものでもOK
......
\end{document}
%\setting{typeset after merge} \settingコマンドは子ファイルでは使えない
```

### small_merge.pyについて
templateディレクトリにあるsmall_merge.pyは、おおよそmerge.pyと同様の処理を行う。
違いとしては、親ファイルがroot.texによらないところ、及びプロジェクト内のディレクトリであればどこでも使用可能というところである。
このプログラムは子ファイル内で`\subfile`コマンドを使用している場合を想定して製作した。
ただし、以下の条件を守る必要がある。
 - 親ファイルの名前は先頭に`root_`がつく必要がある。
 - 親ファイルが存在するディレクトリにsmall_merge.pyを移動させ、使用する必要がある(プログラムごとコピペで可)

### 写真について
picというディレクトリを作成し、そこに保存して使用することを想定している。

### bibファイル
子ファイルごとに指定する。

```
@Misc{
  hoge,
  title = "fuga"
  howpublished = "piyo"
  author = "hogera"
}
......
```

## pdfファイルの生成(root.texで`\setting`コマンドを指定する場合)
root.texに以下を指定する
```
......
\end{document}
\setting{typeset after merge}
\setting{generate pdf after typeset}
```

## 指定することができる`\setting`コマンド
`\setting`の中にコマンドを入れることで指定できる。最初に!をつけることで一部コマンドは否定することができる
これらは一部をのぞいて初期設定はFalseである。

|コマンド|意味|否定|例|
| ---- | ---- | ---- | ---- |
|`typeset after merge`|マージした後にタイプセットする|〇||
|`generate pdf after typeset`|タイプセットした後にpdfの生成をする(`typeset after merge`を指定する必要がある)|〇||
|`display typeset log small`|タイプセットの時に出てくる表示を最小限にする※(`typeset after merge`を指定する必要がある)|〇||
|`display typeset small log`|`display typeset log small`と一緒|〇||
|`print comment`|コメントアウト及びコメント環境内も表示する|〇||
|`fix punctuation`|，や．を整える|〇||
|`set comma`|`fix punctuation`を指定している場合、"、"を"，"に変換する|〇||
|`set toten`|=`!set comma`, "，"を"、"に変換する。どちらか片方を指定すればよい(初期設定はTrue)|〇||
|`set period`|`fix punctuation`を指定している場合、"。"を"．"に変換する|〇||
|`set kuten`|=`!set period`, "．"を"。"に変換する。どちらか片方を指定すればよい(初期設定はTrue)|〇||
|`clearpage before {section}`|{section}内のコマンドを見つけたらその前に`\clearpage`を挿入する{section}には章や節を指定するコマンドを入れる|〇|\setting{clearpage before section*}<br>\setting{clearpage before subsection}|
|`generate ref.csv`|参照元の関係性を示す.csvを作成する|〇||
|`error when there is no reference`|`generate ref.csv`を指定していて、`\pageref`, `\ref`, `\cite`で参照元を見つけれない場合、typesetするのをやめる|〇||
|`merged name: `|このキーワードの後に指定したファイル名でマージする(初期設定ではmerged)|×|\setting{merged name: merged}|

※'typeset after merge'を指定したときに3回タイプセットするが、最後の一回のみにワーニングメッセージが出てくるようにして、それ以外のメッセージは一切出ないようにする。

## pdfファイルの生成(root.texで`\setting`コマンドを指定しない場合)
### Windows
TeXWorks Editorの使用を想定する。以下のコマンドにより、ソースコードをmergeした全体ファイルを生成可能である。
```
$ python3 merge.py
```
その後、1度タイプセットする。
そして、Windowsのコマンドプロントで以下のコマンドによりデータベース中の参考文献を反映させる。
```
$ pbibtex merge
```
その後、タイプセットをいくらかやると正しく反映される。
### Linux
(未検証だが......)
テキストファイルを使用して編集をし、生成はコマンドの使用を想定する。

mergeはWindowsと同様に以下のように行う
```
$ python3 merge.py
```
pdfファイルの生成は以下のように行う。
```
$ platex merge.tex
```
そして、以下のコマンドによりデータベース中の参考文献を反映させる。
```
$ pbibtex merge
```
その後、以下のコマンドを3回ほど実行する。(?)
```
$ platex merge.tex
```
正しい.dviファイルが生成されたのを確認したら以下のコマンドによりpdfファイルを生成する。
```
$ dvipdfmx merge
```
もし、参照など、間違っている場合があれば、``` $ platesx merge.tex ``` のコマンドをもう一回実行し上記のコマンドを実行する。
