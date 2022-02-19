# EPUB Generator

HTMLファイルやテキストファイルから電子書籍用の.epubファイルを生成します。

## 使い方

電子書籍として使用するテキストファイルや画像ファイルを使用し、テンプレートとなるHTMLファイルに埋め込む形式で電子書籍ファイルを生成します。

以下のファイルを準備してください。

- 電子書籍に使用するファイル（テキスト／画像）
- ページのテンプレートとなるHTMLファイル
- 設定ファイル（後述）

以下のパラメータを指定して実行すると.epubファイルが作成されます。

- -i: 設定ファイルのパス
- -o: 出力する電子書籍ファイルのパス

```
python epub_generator.py -i C:/setting.yaml -o C:/sample.epub
```

準備するファイルについては以下のガイドを参照してください。

### 電子書籍に使用するファイル（テキスト／画像）

電子書籍として使用する以下のようなファイルを用意してください。

- カバー画像ファイル
- 本文のテキストファイル
- 本文の画像ファイル

本文のテキストファイルは設定ファイル（後述）によって文字列の置換が可能です。
xxxという文字列をyyyに置換する等の単純な置換の他、正規表現による置換も行えます。
以下のような目的で使用できます。

- ルビを振る
- 画像を差し込む

### コンテンツとなるHTMLファイル

電子書籍リーダーシステムが解釈できるHTMLファイルを用意してください。

以下はサンプルです。

```html:title.xhtml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="ja" xml:lang="ja">

<head>
	<title>タイトル</title>
	<meta charset="UTF-8" />
	<link rel="stylesheet" type="text/css" href="{$setting.resources.styleSheets.1.filePath}" />
</head>

<body class="fix">
	<div class="title">
		<h1>{$setting.title}</h1>
		<hr class="under-title" />
		<span>{$setting.authorName}</span>
	</div>
</body>

</html>
```

HTMLファイル中に{$setting.xxxx}形式で設定ファイル（後述）のデータを埋め込むことができます。
この仕組みにより異なる電子書籍においても同一のテンプレートを使用することで、同じようなレイアウトでの出版を可能にしています。

### 設定ファイル

生成する電子書籍に関する情報が記載されたYAML形式のファイルです。
以下のサンプルは全ての設定項目を盛り込んでおり、説明はファイル中のコメントを参照してください。

```yaml:setting.yaml
# ------------------------------
# 基本情報
# ------------------------------
bookId: f66fd2ea-02d9-b449-10f1-215c6a891743    # 書籍を一意に識別するIDです。opfファイルのidenfifierに設定する値になります。
language: ja-JP     # 書籍の言語を指定します。opfファイルのlanguageに設定する値になります。
modified: "2022-01-31T00:00:00Z"        # 書籍の更新日時を指定します。opfファイルのModifiedに設定する値になります。
title: 電子書籍のタイトル       # 電子書籍のタイトルを指定します。
authorName: ペンネーム1     # 電子書籍の著者名を指定します。opfファイルのroleに設定する値になります。
authorRole: aut     # 電子書籍の著者に関するロールを指定します。出版先のフォーマットに従ってください。opfファイルのroleに設定する値になります。
authorCopyRight: (C) ペンネーム1 2022   # 電子書籍の著者に関するコピーライトを指定します。
otherAuthors:   # その他の著者／寄与者がいる場合は以下のように追記してください。不要な場合はこの行と配下の設定を削除してください。
  - authorName: ペンネーム2     # その他の著者／寄与者の名前を指定します。opfファイルのroleに設定する値になります。
    authorRole: ill     # その他の著者／寄与者に関するロールを指定します。opfファイルのroleに設定する値になります。
  - authorName: ペンネーム3
    authorRole: ill
pageProgressionDirection: rtl   # 電子書籍の綴じ方を指定します。ltr:（左から右）／rtl（右から左）のいずれかを指定してください。
# ------------------------------
# リソース情報
# ------------------------------
resources:
  # スタイルシート
  styleSheets:
    - filePath: .\template\style.css        # 電子書籍のレイアウトに使用するスタイルシートファイルを指定してください。不要な場合は削除可能です。
  # 画像
  images:
    - filePath: .\resource\image\cover.png      # 電子書籍に使用する画像ファイルを指定してください。不要な場合は削除可能です。
      isCover: true     # 使用する画像ファイルが表紙画像かどうかを指定します。true（表紙画像として使用する）／false（表紙画像として使用しない）
  # チャプター
  chapters:
    replaces:       # 電子書籍に使用する本文データ共通の文字置換設定を複数指定できます。
      - type: regex     # 置き換え方式を指定します。simple（単純置換）／regex（正規表現による置換）
        placeHolder: (！？)     # 置換元となる文字列を指定します。
        replaceContent: <span class="tcu">!?</span>     # 置換する文字列を指定します。
      - type: regex
        placeHolder: (！！)
        replaceContent: <span class="tcu">!!</span>
      - type: regex
        placeHolder: (？？)
        replaceContent: <span class="tcu">??</span>
      - type: regex
        placeHolder: \n
        replaceContent: <br />\n
      - type: regex
        placeHolder: \{ruby\:(\w+)\{(\w+)\}\}
        replaceContent: <ruby>\1<rt>\2</rt></ruby>
    files:      # 電子書籍に使用する本文データの含まれたファイルを指定します。
      - title: はじめに     # 本文データのタイトルを指定します。
        fileType: text    # 本文データのファイルタイプを指定します。（text: テキストファイル／image: 画像ファイル）
        filePath: .\resource\content\00はじめに.txt     #　本文データのファイルパスを指定します。
      - title: 避けろ！
        fileType: text
        filePath: .\resource\content\01避けろ！.txt
      - title: あとがき
        fileType: text
        filePath: .\resource\content\01避けろ！_あとがき.txt
      - title: 誰も信じられない
        fileType: text
        filePath: .\resource\content\02誰も信じられない.txt
      - title: あとがき
        fileType: text
        filePath: .\resource\content\02誰も信じられない_あとがき.txt
      - title: ヒカゲノナシ
        fileType: text
        filePath: .\resource\content\03ヒカゲノナシ.txt
      - title: あとがき
        fileType: text
        filePath: .\resource\content\03ヒカゲノナシ_あとがき.txt
      - title: インヘリターズ
        fileType: text
        filePath: .\resource\content\04インヘリターズ.txt
        replaces:   # 本文データ共通の置換設定とは別に、この本文データファイルにだけ適用する置換設定を指定します。
          - type: regex
            placeHolder: ([0-9]{1,2})号
            replaceContent: <span class="tcu">\1</span>号
      - title: あとがき
        fileType: text
        filePath: .\resource\content\04インヘリターズ_あとがき.txt
        replaces:
          - type: regex
            placeHolder: ([0-9]{1,2})号
            replaceContent: <span class="tcu">\1</span>号
      - title: それでも生きていく
        fileType: text
        filePath: .\resource\content\05それでも生きていく.txt
      - title: あとがき
        fileType: text
        filePath: .\resource\content\05それでも生きていく_あとがき.txt
# ------------------------------
# コンテンツ情報
# ------------------------------
contents:   # 電子書籍のページとして生成するコンテンツを指定します。テンプレートとなるxhtmlファイルを指定し、本文コンテンツには紐づける本文データのインデックスを設定することによってその分のコンテンツファイルを自動生成します。
  # カバー
  - filePath: .\template\cover.xhtml        # コンテンツに使用するxhtmlファイルを指定します。
    isNavigationContent: false      # 目次コンテンツかどうかを指定します。true（目次コンテンツとして使用する）／false（目次コンテンツとして使用しない）
    createByChaptersCount: false        # 本文データの数だけコンテンツファイルを生成するかどうかを指定します。true（本文データの数だけコンテンツファイルを生成する）／false（しない）
  # タイトル
  - filePath: .\template\title.xhtml
    isNavigationContent: false
    createByChaptersCount: false
  # 目次
  - filePath: .\template\navigation.xhtml
    isNavigationContent: true
    createByChaptersCount: false
    replaces:       # 電子書籍に使用するコンテンツ中の文字置換設定を複数指定できます。
      - type: simple
        placeHolder: "{navigation}"
        replaceContent: |-
          <li><a href="{$setting.resources.chapters.files.1.filePath}">{$setting.resources.chapters.files.1.title}</a></li>
          <li><a href="{$setting.resources.chapters.files.2.filePath}">{$setting.resources.chapters.files.2.title}</a></li>
          <li><a href="{$setting.resources.chapters.files.4.filePath}">{$setting.resources.chapters.files.4.title}</a></li>
          <li><a href="{$setting.resources.chapters.files.6.filePath}">{$setting.resources.chapters.files.6.title}</a></li>
          <li><a href="{$setting.resources.chapters.files.8.filePath}">{$setting.resources.chapters.files.8.title}</a></li>
          <li><a href="{$setting.resources.chapters.files.10.filePath}">{$setting.resources.chapters.files.10.title}</a></li>
  # はじめに
  - filePath: .\template\readme.xhtml
    isNavigationContent: false
    createByChaptersCount: true
    useChapters:        # このコンテンツに使用する本文データのインデックスを指定します。
      - chapterIndex: 1
  # チャプター
  - filePath: .\template\chapter.xhtml
    isNavigationContent: false
    createByChaptersCount: true
    useChapters:
      - chapterIndex: 2
      - chapterIndex: 3
      - chapterIndex: 4
      - chapterIndex: 5
      - chapterIndex: 6
      - chapterIndex: 7
      - chapterIndex: 8
      - chapterIndex: 9
      - chapterIndex: 10
      - chapterIndex: 11
  # 著作権
  - filePath: .\template\rights.xhtml
    isNavigationContent: false
    createByChaptersCount: false
```

## 置換について

### 設定ファイルのデータを使った置換について

本文データ／コンテンツファイル中に{$setting.xxxx}と指定することにより、設定ファイルのデータで置換することが可能です。

以下のように{$setting.title}／{$setting.authorName}と記述されたHTMLファイルを用意します。

```html:title.xhtml
<body class="fix">
	<div class="title">
		<h1>{$setting.title}</h1>
		<hr class="under-title" />
		<span>{$setting.authorName}</span>
	</div>
</body>
```

設定ファイルを以下のように記述します。

```yaml:setting.yaml
title: 電子書籍のタイトル
authorName: ペンネーム1
```

生成されたコンテンツファイルは以下のようになります。

```html:title.xhtml
<body class="fix">
	<div class="title">
		<h1>電子書籍のタイトル</h1>
		<hr class="under-title" />
		<span>ペンネーム1</span>
	</div>
</body>
```

階層構造を持つ設定の場合はドット（.）を使って指定します。また配列（複数指定している）場合は、指定順に1～の数値を使って指定します。

```yaml:setting.yaml
otherAuthors:
  - authorName: ペンネーム2
    authorRole: ill
  - authorName: ペンネーム3
    authorRole: ill
```

上記のような階層／配列構造を持つ設定を使用する場合、以下のように記載します。

```html
<div>{$setting.otherAuthors.1.authorName}</div>
<div>{$setting.otherAuthors.2.authorName}</div>
```

生成されたコンテンツファイルは以下のようになります。

```html
<div>ペンネーム2</div>
<div>ペンネーム3</div>
```

### 特殊な置換について

本文データを使用する設定にしたコンテンツの場合、以下の特殊な置換が利用できます。

- {$chapter.title}
  - 本文データのタイトルで置換します。
- {$chapter.body}
  - 本文データで置換します。
- {$chapter.filePath}
  - 本文データのファイルパスで置換します。主にコミックスの用途で使用します。
