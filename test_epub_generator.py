# encoding: utf-8
import unittest
import epub_generator

class TestBatch(unittest.TestCase):
 
    # TODO: テストケースはだいたい以下みたいなヤツで
    # - 設定ファイルがなかったら
    # - 設定ファイルがあっても空／YAMLじゃなかったら
    # - 設定ファイルにあるファイルがなかったら
    # - ファイル出力できない
    # - チャプターファイルがないケース
    # - 置換が使用されないケース
    # 他にもたくさんあると思う

    def test_xxx(self):
        epub_generator.Batch().execute()
        self.assertEqual(10, calc.add_num(6, 4)) 

