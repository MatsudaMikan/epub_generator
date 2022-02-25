# encoding: utf-8
from calendar import month
from datetime import datetime
from imp import find_module
import os
from this import d
import unittest
import pathlib
import shutil
import time
import uuid
import subprocess
import re
import platform
from epub_generator import Utility, FileSystem, Convert, DateTimeHelper, BatchBase, Batch

EPUB_CHECKER_PATH = r'..\epub-checker\epubcheck.jar'

def exist_epub_errors(epub_filepath):

    result = {'check_skipped': False, 'status': False}

    os.chdir(os.path.dirname(__file__))
    path = os.path.abspath(EPUB_CHECKER_PATH)
    if not os.path.exists(path):
        print('電子書籍チェックツールが見つからないためスキップします')
        result['check_skipped'] = True
        return result

    command = 'java -Xss1024k -jar {0} {1}'.format(path, epub_filepath)
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    find_message = 'メッセージ'
    status = True
    while True:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        needs_check = False
        if platform.system() == 'Windows':
            print(line.decode('sjis'))
            if re.match('^メッセージ:', line.decode('sjis')):
                needs_check = True
        else:
            print(line.decode('utf8'))
            if re.match('^メッセージ:', line.decode('utf8')):
                needs_check = True
        if needs_check:
            # メッセージ: 0 件の致命的エラー / 0 件のエラー / 0 件の警告 / 0 件の情報
            matched = None
            if platform.system() == 'Windows':
                matched = re.match('メッセージ: ([0-9]+) 件の致命的エラー \/ ([0-9]+) 件のエラー', line.decode('sjis'))
            else:
                matched = re.match('メッセージ: ([0-9]+) 件の致命的エラー \/ ([0-9]+) 件のエラー', line.decode('utf8'))
            if matched and len(matched.groups()) == 2:
                if int(matched.group(1)) > 0 or int(matched.group(2)) > 0:
                    status = False
            status = False

    result['status'] = status

    return result

def create_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)

def create_temp_directory():
    dir = os.path.join(os.path.dirname(__file__), 'data', str(uuid.uuid4().int))
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
    return dir

def remove_temp_directory(dir):

    retry_count = 0
    while (True):
        retry_count += 1
        has_error = False
        try:
            shutil.rmtree(dir)
        except Exception as e:
            has_error = True
            if retry_count >= 5:
                break
            time.sleep(1)
        if not has_error:
            break

class TestUtility(unittest.TestCase):
#     def test_is_empty(self):
#         # ------------------------------
#         # 空文字
#         # ------------------------------
#         value = ''
#         self.assertEqual(True, Utility.is_empty(value))
#         # ------------------------------
#         # None
#         # ------------------------------
#         value = None
#         self.assertEqual(True, Utility.is_empty(value))
#         # ------------------------------
#         # 文字列
#         # ------------------------------
#         value = 'test'
#         self.assertEqual(False, Utility.is_empty(value))
#         # ------------------------------
#         # 数値
#         # ------------------------------
#         value = 1
#         self.assertEqual(False, Utility.is_empty(value))


# class TestFileSystem(unittest.TestCase):

#     def test_collect_filepaths(self):
#         temp_dir = create_temp_directory()
#         pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
#         pathlib.Path(os.path.join(temp_dir, 'dir2')).mkdir(parents=True, exist_ok=True)
#         pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()
#         pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp2.dat')).touch()
#         pathlib.Path(os.path.join(temp_dir, 'dir2', 'temp1.txt')).touch()
#         pathlib.Path(os.path.join(temp_dir, 'dir2', 'temp2.dat')).touch()
#         pathlib.Path(os.path.join(temp_dir, 'dir2', 'temp3.obj')).touch()

#         # ------------------------------
#         # 全てのパスをリスト
#         # ------------------------------
#         file_list = []
#         try:
#             FileSystem.collect_filepaths(temp_dir, file_list)
#         except Exception as e:
#             print(e)
#         self.assertEqual(8, len(file_list))

#         # ------------------------------
#         # 名前でフィルタしたリスト
#         # ------------------------------
#         file_list = []
#         try:
#             FileSystem.collect_filepaths(temp_dir, file_list, name_filter_regex='.*temp1.*')
#         except Exception as e:
#             print(e)
#         self.assertEqual(5, len(file_list))

#         # ------------------------------
#         # 拡張子でフィルタしたリスト
#         # ------------------------------
#         file_list = []
#         try:
#             FileSystem.collect_filepaths(temp_dir, file_list, name_filter_regex='.*\.obj$')
#         except Exception as e:
#             print(e)
#         self.assertEqual(4, len(file_list))

#         remove_temp_directory(temp_dir)

#     def test_create_directory(self):
#         temp_dir = create_temp_directory()
        
#         # ------------------------------
#         # ディレクトリツリーを作成できるか
#         # ------------------------------
#         try:
#             FileSystem.create_directory(os.path.join(temp_dir, 'dir1', 'dir2'))
#         except Exception as e:
#             print(e)
#         self.assertEqual(True, os.path.exists(os.path.join(temp_dir, 'dir1', 'dir2')))

#         remove_temp_directory(temp_dir)

#     def test_create_directory(self):
#         temp_dir = create_temp_directory()

#         # ------------------------------
#         # ディレクトリツリーを削除できるか
#         # ------------------------------
#         try:
#             pathlib.Path(os.path.join(temp_dir, 'dir1', 'dir2')).mkdir(parents=True, exist_ok=True)
#             FileSystem.remove_directory(os.path.join(temp_dir, 'dir1', 'dir2'))
#         except Exception as e:
#             print(e)
#         self.assertEqual(False, os.path.exists(os.path.join(temp_dir, 'dir1', 'dir2')))

#         # ------------------------------
#         # 存在しないディレクトリツリー削除時にエラーが起きないか
#         # ------------------------------
#         occuerred_exception = False
#         try:
#             pathlib.Path(os.path.join(temp_dir, 'dir1', 'dir2')).mkdir(parents=True, exist_ok=True)
#             FileSystem.remove_directory(os.path.join(temp_dir, 'dir1', 'dir2'))
#         except Exception:
#             occuerred_exception = True
#         self.assertEqual(False, occuerred_exception)        

#         remove_temp_directory(temp_dir)
        
#     def test_move_file(self):
#         temp_dir = create_temp_directory()
#         pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
#         pathlib.Path(os.path.join(temp_dir, 'dir2')).mkdir(parents=True, exist_ok=True)
#         pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()

#         # ------------------------------
#         # ファイルを移動したか
#         # ------------------------------
#         try:
#             FileSystem.move_file(os.path.join(temp_dir, 'dir1', 'temp1.txt'), os.path.join(temp_dir, 'dir2', 'temp1.txt'))
#         except Exception as e:
#             print(e)
#         self.assertEqual(False, os.path.exists(os.path.join(temp_dir, 'dir1', 'temp1.txt')))
#         self.assertEqual(True, os.path.exists(os.path.join(temp_dir, 'dir2', 'temp1.txt')))

#         remove_temp_directory(temp_dir)
        
#     def test_copy_file(self):
#         temp_dir = create_temp_directory()
#         pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
#         pathlib.Path(os.path.join(temp_dir, 'dir2')).mkdir(parents=True, exist_ok=True)
#         pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()

#         # ------------------------------
#         # ファイルをコピーしたか
#         # ------------------------------
#         try:
#             FileSystem.copy_file(os.path.join(temp_dir, 'dir1', 'temp1.txt'), os.path.join(temp_dir, 'dir2', 'temp1.txt'))
#         except Exception as e:
#             print(e)
#         self.assertEqual(True, os.path.exists(os.path.join(temp_dir, 'dir1', 'temp1.txt')))
#         self.assertEqual(True, os.path.exists(os.path.join(temp_dir, 'dir2', 'temp1.txt')))

#         remove_temp_directory(temp_dir)
        
#     def test_remove_file(self):
#         temp_dir = create_temp_directory()
#         pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
#         pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()

#         # ------------------------------
#         # ファイルを削除したか
#         # ------------------------------
#         try:
#             FileSystem.remove_file(os.path.join(temp_dir, 'dir1', 'temp1.txt'))
#         except Exception as e:
#             print(e)
#         self.assertEqual(False, os.path.exists(os.path.join(temp_dir, 'dir1', 'temp1.txt')))

#         remove_temp_directory(temp_dir)
        
#     def test_remove_file(self):
#         temp_dir = create_temp_directory()
#         pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
#         pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()

#         # ------------------------------
#         # ファイルが存在するか
#         # ------------------------------
#         self.assertEqual(True, FileSystem.exists_file(os.path.join(temp_dir, 'dir1', 'temp1.txt')))

#         # ------------------------------
#         # ファイルが存在しないか
#         # ------------------------------
#         self.assertEqual(False, FileSystem.exists_file(os.path.join(temp_dir, 'dir1', 'temp2.txt')))
#         self.assertEqual(False, FileSystem.exists_file(os.path.join(temp_dir, 'dir2', 'temp1.txt')))

#         remove_temp_directory(temp_dir)
        

# class TestConvert(unittest.TestCase):
#     def test_format(self):

#         # ------------------------------
#         # 文字列
#         # ------------------------------
#         value = 'test'
#         self.assertEqual('test', Convert.format(value))
        
#         # ------------------------------
#         # 数値
#         # ------------------------------
#         value = 1
#         self.assertEqual('1', Convert.format(value, 'number'))
#         value = 1000
#         self.assertEqual('1,000', Convert.format(value, 'number'))
#         value = 1000.1234
#         self.assertEqual('1,000.1234', Convert.format(value, 'number'))

#         # ------------------------------
#         # 日付
#         # ------------------------------
#         value = '1'
#         self.assertEqual('1', Convert.format(value, 'date'))
#         value = '20220228235859'
#         self.assertEqual('20220228235859', Convert.format(value, 'date'))
#         value = '20220228'
#         self.assertEqual('2022-02-28', Convert.format(value, 'date'))
        
#         # ------------------------------
#         # 日付時刻
#         # ------------------------------
#         value = '1'
#         self.assertEqual('1', Convert.format(value, 'datetime'))
#         value = '20220228235859fff'
#         self.assertEqual('20220228235859fff', Convert.format(value, 'datetime'))
#         value = '20220228235859'
#         self.assertEqual('2022-02-28 23:58:59', Convert.format(value, 'datetime'))

#     def test_parse(self):

#         # ------------------------------
#         # 文字列
#         # ------------------------------
#         value = 'test'
#         self.assertEqual('test', Convert.parse(value))
        
#         # ------------------------------
#         # 数値
#         # ------------------------------
#         value = 1
#         self.assertEqual(1, Convert.parse(value))
#         value = '1'
#         self.assertEqual(1, Convert.parse(value, 'number'))
#         value = '1,000'
#         self.assertEqual(1000, Convert.parse(value, 'number'))
#         value = '1,000.1234'
#         self.assertEqual(1000.1234, Convert.parse(value, 'number'))

#         # ------------------------------
#         # 日付
#         # ------------------------------
#         value = '1'
#         self.assertEqual('1', Convert.parse(value, 'date'))
#         value = '2022-02-28x'
#         self.assertEqual('2022-02-28x', Convert.parse(value, 'date'))
#         value = '2022-02-28'
#         self.assertEqual('20220228', Convert.parse(value, 'date'))
        
#         # ------------------------------
#         # 日付時刻
#         # ------------------------------
#         value = '1'
#         self.assertEqual('1', Convert.parse(value, 'datetime'))
#         value = '2022-02-28 23:58:59x'
#         self.assertEqual('2022-02-28 23:58:59x', Convert.parse(value, 'datetime'))
#         value = '2022-02-28 23:58:59'
#         self.assertEqual('20220228235859', Convert.parse(value, 'datetime'))


# class TestDateTimeHelper(unittest.TestCase):
#     def test_now(self):

#         # ------------------------------
#         # エラーが起きないか
#         # ------------------------------
#         error_occurrerd = False
#         try:
#             DateTimeHelper.now()
#         except Exception as e:
#             print(e)
#             error_occurrerd = True
#         self.assertEqual(False, error_occurrerd)

#     def test_to_yyyy(self):

#         d = DateTimeHelper(year=9999, month=12, day=31, hour=23, minute=58, second=59, microsecond=999)
#         self.assertEqual('9999', d.to_yyyy())

#     def test_to_yyyymm(self):

#         d = DateTimeHelper(year=9999, month=12, day=31, hour=23, minute=58, second=59, microsecond=999)

#         # ------------------------------
#         # セパレータデフォルト
#         # ------------------------------
#         self.assertEqual('9999-12', d.to_yyyymm())

#         # ------------------------------
#         # セパレータ指定
#         # ------------------------------
#         self.assertEqual('9999/12', d.to_yyyymm(monthsep='/'))

#         # ------------------------------
#         # セパレータなし
#         # ------------------------------
#         self.assertEqual('999912', d.to_yyyymm(monthsep=''))

#     def test_to_yyyymmdd(self):

#         d = DateTimeHelper(year=9999, month=12, day=31, hour=23, minute=58, second=59, microsecond=999)

#         # ------------------------------
#         # セパレータデフォルト
#         # ------------------------------
#         self.assertEqual('9999-12-31', d.to_yyyymmdd())

#         # ------------------------------
#         # セパレータ指定
#         # ------------------------------
#         self.assertEqual('9999/12/31', d.to_yyyymmdd(datesep='/'))

#         # ------------------------------
#         # セパレータなし
#         # ------------------------------
#         self.assertEqual('99991231', d.to_yyyymmdd(datesep=''))

#     def test_to_yyyymmddhhmiss(self):

#         d = DateTimeHelper(year=9999, month=12, day=31, hour=23, minute=58, second=59, microsecond=999)

#         # ------------------------------
#         # セパレータデフォルト
#         # ------------------------------
#         self.assertEqual('9999-12-31 23:58:59', d.to_yyyymmddhhmiss())

#         # ------------------------------
#         # セパレータ指定
#         # ------------------------------
#         self.assertEqual('9999/12/31_23@58@59', d.to_yyyymmddhhmiss(datesep='/', datetimesep='_', timesep='@'))

#         # ------------------------------
#         # セパレータなし
#         # ------------------------------
#         self.assertEqual('99991231235859', d.to_yyyymmddhhmiss(datesep='', datetimesep='', timesep=''))

#     def test_add_years(self):

#         d = DateTimeHelper(year=9998, month=12, day=31, hour=23)

#         # ------------------------------
#         # 0年加算
#         # ------------------------------
#         self.assertEqual(9998, d.add_years(0).year)

#         # ------------------------------
#         # 1年加算
#         # ------------------------------
#         self.assertEqual(9999, d.add_years(1).year)

#         # ------------------------------
#         # 1年減算
#         # ------------------------------
#         self.assertEqual(9997, d.add_years(-1).year)

#     def test_add_months(self):

#         d = DateTimeHelper(year=9998, month=12, day=31, hour=23)

#         # ------------------------------
#         # 0年加算
#         # ------------------------------
#         self.assertEqual('999812', d.add_months(0).strftime('%Y%m'))

#         # ------------------------------
#         # 1ヶ月加算
#         # ------------------------------
#         self.assertEqual('999901', d.add_months(1).strftime('%Y%m'))

#         # ------------------------------
#         # 1ヶ月減算
#         # ------------------------------
#         self.assertEqual('999811', d.add_months(-1).strftime('%Y%m'))

#     def test_add_days(self):

#         d = DateTimeHelper(year=9998, month=12, day=31, hour=23)

#         # ------------------------------
#         # 0年加算
#         # ------------------------------
#         self.assertEqual('99981231', d.add_days(0).strftime('%Y%m%d'))

#         # ------------------------------
#         # 1日加算
#         # ------------------------------
#         self.assertEqual('99990101', d.add_days(1).strftime('%Y%m%d'))

#         # ------------------------------
#         # 1日減算
#         # ------------------------------
#         self.assertEqual('99981230', d.add_days(-1).strftime('%Y%m%d'))

#         # ------------------------------
#         # うるう年
#         # ------------------------------
#         d = DateTimeHelper(year=2022, month=2, day=28)
#         self.assertEqual('20220301', d.add_days(1).strftime('%Y%m%d'))
#         d = DateTimeHelper(year=2022, month=3, day=1)
#         self.assertEqual('20220228', d.add_days(-1).strftime('%Y%m%d'))


# class TestBatch(unittest.TestCase):
 
#     def test_invalid_parameter(self):
#         # TODO: パラメータがない
#         # argv = None
#         # Batch().execute(argv)
#         pass

#     def test_invalid_setting_file(self):
#         # ------------------------------
#         # 設定ファイルがない
#         # ------------------------------
#         temp_dir = create_temp_directory()
        
#         return_code = -1
#         try:
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         remove_temp_directory(temp_dir)

#         self.assertEqual(1, return_code)

#         # ------------------------------
#         # 設定ファイルはあるけど空
#         # ------------------------------
#         temp_dir = create_temp_directory()
        
#         create_file(os.path.join(temp_dir, 'test.yaml'), r'''''')
#         return_code = -1
#         try:
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         remove_temp_directory(temp_dir)
        
#         self.assertEqual(1, return_code)

#         # ------------------------------
#         # 設定ファイルはあるけどYAMLフォーマットじゃない
#         # ------------------------------
#         temp_dir = create_temp_directory()
        
#         create_file(os.path.join(temp_dir, 'test.yaml'), r'''
# [xxxx]
# yyyy = zzzz
#         ''')
#         return_code = -1
#         try:
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         remove_temp_directory(temp_dir)
        
#         self.assertEqual(1, return_code)

#         # ------------------------------
#         # 設定ファイルがYAMLフォーマットだけど設定なし
#         # ------------------------------
#         temp_dir = create_temp_directory()
        
#         create_file(os.path.join(temp_dir, 'test.yaml'), r'''
# xxxx: yyyy
#         ''')
#         return_code = -1
#         try:
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         remove_temp_directory(temp_dir)
        
#         self.assertEqual(1, return_code)

#         # ------------------------------
#         # 設定ファイル中のパスが空
#         # ------------------------------
#         temp_dir = create_temp_directory()
        
#         create_file(os.path.join(temp_dir, 'test.yaml'), r'''
# title: サンプル
# resources:
# contents:
#   - filePath: 
#     isNavigationContent: false
#     createByChaptersCount: false
#         ''')
#         return_code = -1
#         try:
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         self.assertEqual(1, return_code)

#         remove_temp_directory(temp_dir)
        
#         # ------------------------------
#         # 設定ファイル中のパスが無効
#         # ------------------------------
#         temp_dir = create_temp_directory()
        
#         create_file(os.path.join(temp_dir, 'test.yaml'), r'''
# title: サンプル
# resources:
# contents:
#   - filePath: .\/////.xhtml
#     isNavigationContent: false
#     createByChaptersCount: false
#         ''')
#         return_code = -1
#         try:
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         self.assertEqual(1, return_code)

#         remove_temp_directory(temp_dir)


#         # ------------------------------
#         # 設定ファイル中のパスのファイルが存在しない
#         # ------------------------------
#         temp_dir = create_temp_directory()
        
#         create_file(os.path.join(temp_dir, 'test.yaml'), r'''
# title: サンプル
# resources:
#   styleSheets:
#     - filePath: .\test.css
#   images:
#     - filePath: .\test.png
#       isCover: true
#   chapters:
#     files:
#       - title: 
#         fileType: image
#         filePath: .\test1.png
# contents:
#   - filePath: .\test.xhtml
#     isNavigationContent: false
#     createByChaptersCount: false
#         ''')
#         return_code = -1
#         try:
#             # 全てのファイルがない
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         self.assertEqual(1, return_code)

#         return_code = -1
#         try:
#             # test.css作成
#             pathlib.Path(os.path.join(temp_dir, 'test.css')).touch()
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         self.assertEqual(1, return_code)

#         return_code = -1
#         try:
#             # test.png作成
#             pathlib.Path(os.path.join(temp_dir, 'test.png')).touch()
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         self.assertEqual(1, return_code)

#         return_code = -1
#         try:
#             # test1.png作成
#             pathlib.Path(os.path.join(temp_dir, 'test1.png')).touch()
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         self.assertEqual(1, return_code)

#         return_code = -1
#         try:
#             # test1.xhtml作成
#             pathlib.Path(os.path.join(temp_dir, 'test.xhtml')).touch()
#             return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + os.path.join(temp_dir, 'test.epub')])
#         except Exception as e:
#             print(e)
#         self.assertEqual(0, return_code)

#         remove_temp_directory(temp_dir)

    def test_create_epub(self):

        temp_dir = create_temp_directory()
        
        # ------------------------------
        # TODO: 最小限のepubファイルを作成、epub_checkerでのチェックも行う
        # ------------------------------
        create_file(os.path.join(temp_dir, 'test.yaml'), r'''
title: サンプル
contents:
  - filePath: .\test.xhtml
    isNavigationContent: false
    createByChaptersCount: false
        ''')
        create_file(os.path.join(temp_dir, 'test.xhtml'), r'''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="ja" xml:lang="ja">
<head>
	<title>サンプル</title>
	<meta charset="UTF-8" />
</head>
<body>
    サンプルコンテンツ
</body>
</html>
        ''')
        return_code = -1
        epub_filepath = os.path.join(temp_dir, 'test.epub')
        try:
            return_code = Batch().execute(['-i=' + os.path.join(temp_dir, 'test.yaml'), '-o=' + epub_filepath])
        except Exception as e:
            print(e)

        self.assertEqual(0, return_code)

        result = exist_epub_errors(epub_filepath)




        # TODO: 
        # TODO: 
        # TODO: 
        # TODO: 
        # TODO: 

        remove_temp_directory(temp_dir)



if __name__ == '__main__':
    unittest.main()
