# encoding: utf-8
from calendar import month
from datetime import datetime
import os
from this import d
import unittest
import tempfile
import pathlib
import shutil
from epub_generator import Utility, FileSystem, Convert, DateTimeHelper, BatchBase, Batch


class TestUtility(unittest.TestCase):
    def test_is_empty(self):
        # 空文字
        value = ''
        self.assertEqual(True, Utility.is_empty(value))
        # None
        value = None
        self.assertEqual(True, Utility.is_empty(value))
        # 文字列
        value = 'test'
        self.assertEqual(False, Utility.is_empty(value))
        # 数値
        value = 1
        self.assertEqual(False, Utility.is_empty(value))


class TestFileSystem(unittest.TestCase):

    def test_collect_filepaths(self):
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name
        pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(temp_dir, 'dir2')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()
        pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp2.dat')).touch()
        pathlib.Path(os.path.join(temp_dir, 'dir2', 'temp1.txt')).touch()
        pathlib.Path(os.path.join(temp_dir, 'dir2', 'temp2.dat')).touch()
        pathlib.Path(os.path.join(temp_dir, 'dir2', 'temp3.obj')).touch()

        # 全てのパスをリスト
        file_list = []
        try:
            FileSystem.collect_filepaths(temp_dir, file_list)
        except:
            pass
        self.assertEqual(8, len(file_list))

        # 名前でフィルタしたリスト
        file_list = []
        try:
            FileSystem.collect_filepaths(temp_dir, file_list, name_filter_regex='.*temp1.*')
        except:
            pass
        self.assertEqual(5, len(file_list))

        # 拡張子でフィルタしたリスト
        file_list = []
        try:
            FileSystem.collect_filepaths(temp_dir, file_list, name_filter_regex='.*\.obj$')
        except:
            pass
        self.assertEqual(4, len(file_list))

        temp.cleanup()

    def test_create_directory(self):
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name
        
        # ディレクトリツリーを作成できるか
        try:
            FileSystem.create_directory(os.path.join(temp_dir, 'dir1', 'dir2'))
        except:
            pass
        self.assertEqual(True, os.path.exists(os.path.join(temp_dir, 'dir1', 'dir2')))

        temp.cleanup()

    def test_create_directory(self):
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name

        # ディレクトリツリーを削除できるか
        try:
            pathlib.Path(os.path.join(temp_dir, 'dir1', 'dir2')).mkdir(parents=True, exist_ok=True)
            FileSystem.remove_directory(os.path.join(temp_dir, 'dir1', 'dir2'))
        except:
            pass
        self.assertEqual(False, os.path.exists(os.path.join(temp_dir, 'dir1', 'dir2')))

        # 存在しないディレクトリツリー削除時にエラーが起きないか
        occuerred_exception = False
        try:
            pathlib.Path(os.path.join(temp_dir, 'dir1', 'dir2')).mkdir(parents=True, exist_ok=True)
            FileSystem.remove_directory(os.path.join(temp_dir, 'dir1', 'dir2'))
        except Exception:
            occuerred_exception = True
        self.assertEqual(False, occuerred_exception)        

        temp.cleanup()
        
    def test_move_file(self):
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name
        pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(temp_dir, 'dir2')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()

        # ファイルを移動したか
        try:
            FileSystem.move_file(os.path.join(temp_dir, 'dir1', 'temp1.txt'), os.path.join(temp_dir, 'dir2', 'temp1.txt'))
        except:
            pass
        self.assertEqual(False, os.path.exists(os.path.join(temp_dir, 'dir1', 'temp1.txt')))
        self.assertEqual(True, os.path.exists(os.path.join(temp_dir, 'dir2', 'temp1.txt')))

        temp.cleanup()
        
    def test_copy_file(self):
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name
        pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(temp_dir, 'dir2')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()

        # ファイルをコピーしたか
        try:
            FileSystem.copy_file(os.path.join(temp_dir, 'dir1', 'temp1.txt'), os.path.join(temp_dir, 'dir2', 'temp1.txt'))
        except:
            pass
        self.assertEqual(True, os.path.exists(os.path.join(temp_dir, 'dir1', 'temp1.txt')))
        self.assertEqual(True, os.path.exists(os.path.join(temp_dir, 'dir2', 'temp1.txt')))

        temp.cleanup()
        
    def test_remove_file(self):
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name
        pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()

        # ファイルを削除したか
        try:
            FileSystem.remove_file(os.path.join(temp_dir, 'dir1', 'temp1.txt'))
        except:
            pass
        self.assertEqual(False, os.path.exists(os.path.join(temp_dir, 'dir1', 'temp1.txt')))

        temp.cleanup()
        
    def test_remove_file(self):
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name
        pathlib.Path(os.path.join(temp_dir, 'dir1')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(temp_dir, 'dir1', 'temp1.txt')).touch()

        # ファイルが存在するか
        self.assertEqual(True, FileSystem.exists_file(os.path.join(temp_dir, 'dir1', 'temp1.txt')))

        # ファイルが存在しないか
        self.assertEqual(False, FileSystem.exists_file(os.path.join(temp_dir, 'dir1', 'temp2.txt')))
        self.assertEqual(False, FileSystem.exists_file(os.path.join(temp_dir, 'dir2', 'temp1.txt')))

        temp.cleanup()
        

class TestConvert(unittest.TestCase):
    def test_format(self):

        # 文字列
        value = 'test'
        self.assertEqual('test', Convert.format(value))
        
        # 数値
        value = 1
        self.assertEqual('1', Convert.format(value, 'number'))
        value = 1000
        self.assertEqual('1,000', Convert.format(value, 'number'))
        value = 1000.1234
        self.assertEqual('1,000.1234', Convert.format(value, 'number'))

        # 日付
        value = '1'
        self.assertEqual('1', Convert.format(value, 'date'))
        value = '20220228235859'
        self.assertEqual('20220228235859', Convert.format(value, 'date'))
        value = '20220228'
        self.assertEqual('2022-02-28', Convert.format(value, 'date'))
        
        # 日付時刻
        value = '1'
        self.assertEqual('1', Convert.format(value, 'datetime'))
        value = '20220228235859fff'
        self.assertEqual('20220228235859fff', Convert.format(value, 'datetime'))
        value = '20220228235859'
        self.assertEqual('2022-02-28 23:58:59', Convert.format(value, 'datetime'))

    def test_parse(self):

        # 文字列
        value = 'test'
        self.assertEqual('test', Convert.parse(value))
        
        # 数値
        value = 1
        self.assertEqual(1, Convert.parse(value))
        value = '1'
        self.assertEqual(1, Convert.parse(value, 'number'))
        value = '1,000'
        self.assertEqual(1000, Convert.parse(value, 'number'))
        value = '1,000.1234'
        self.assertEqual(1000.1234, Convert.parse(value, 'number'))

        # 日付
        value = '1'
        self.assertEqual('1', Convert.parse(value, 'date'))
        value = '2022-02-28x'
        self.assertEqual('2022-02-28x', Convert.parse(value, 'date'))
        value = '2022-02-28'
        self.assertEqual('20220228', Convert.parse(value, 'date'))
        
        # 日付時刻
        value = '1'
        self.assertEqual('1', Convert.parse(value, 'datetime'))
        value = '2022-02-28 23:58:59x'
        self.assertEqual('2022-02-28 23:58:59x', Convert.parse(value, 'datetime'))
        value = '2022-02-28 23:58:59'
        self.assertEqual('20220228235859', Convert.parse(value, 'datetime'))


class TestDateTimeHelper(unittest.TestCase):
    def test_now(self):

        # エラーが起きないか
        error_occurrerd = False
        try:
            DateTimeHelper.now()
        except:
            error_occurrerd = True
        self.assertEqual(False, error_occurrerd)

    def test_to_yyyy(self):

        d = DateTimeHelper(year=9999, month=12, day=31, hour=23, minute=58, second=59, microsecond=999)
        self.assertEqual('9999', d.to_yyyy())

    def test_to_yyyymm(self):

        d = DateTimeHelper(year=9999, month=12, day=31, hour=23, minute=58, second=59, microsecond=999)

        # セパレータデフォルト
        self.assertEqual('9999-12', d.to_yyyymm())

        # セパレータ指定
        self.assertEqual('9999/12', d.to_yyyymm(monthsep='/'))

        # セパレータなし
        self.assertEqual('999912', d.to_yyyymm(monthsep=''))

    def test_to_yyyymmdd(self):

        d = DateTimeHelper(year=9999, month=12, day=31, hour=23, minute=58, second=59, microsecond=999)

        # セパレータデフォルト
        self.assertEqual('9999-12-31', d.to_yyyymmdd())

        # セパレータ指定
        self.assertEqual('9999/12/31', d.to_yyyymmdd(datesep='/'))

        # セパレータなし
        self.assertEqual('99991231', d.to_yyyymmdd(datesep=''))

    def test_to_yyyymmddhhmiss(self):

        d = DateTimeHelper(year=9999, month=12, day=31, hour=23, minute=58, second=59, microsecond=999)

        # セパレータデフォルト
        self.assertEqual('9999-12-31 23:58:59', d.to_yyyymmddhhmiss())

        # セパレータ指定
        self.assertEqual('9999/12/31_23@58@59', d.to_yyyymmddhhmiss(datesep='/', datetimesep='_', timesep='@'))

        # セパレータなし
        self.assertEqual('99991231235859', d.to_yyyymmddhhmiss(datesep='', datetimesep='', timesep=''))

    def test_add_years(self):

        d = DateTimeHelper(year=9998, month=12, day=31, hour=23)

        # 0年加算
        self.assertEqual(9998, d.add_years(0).year)

        # 1年加算
        self.assertEqual(9999, d.add_years(1).year)

        # 1年減算
        self.assertEqual(9997, d.add_years(-1).year)

    def test_add_months(self):

        d = DateTimeHelper(year=9998, month=12, day=31, hour=23)

        # 0年加算
        self.assertEqual('999812', d.add_months(0).strftime('%Y%m'))

        # 1ヶ月加算
        self.assertEqual('999901', d.add_months(1).strftime('%Y%m'))

        # 1ヶ月減算
        self.assertEqual('999811', d.add_months(-1).strftime('%Y%m'))

    def test_add_days(self):

        d = DateTimeHelper(year=9998, month=12, day=31, hour=23)

        # 0年加算
        self.assertEqual('99981231', d.add_days(0).strftime('%Y%m%d'))

        # 1日加算
        self.assertEqual('99990101', d.add_days(1).strftime('%Y%m%d'))

        # 1日減算
        self.assertEqual('99981230', d.add_days(-1).strftime('%Y%m%d'))

        # うるう年
        d = DateTimeHelper(year=2022, month=2, day=28)
        self.assertEqual('20220301', d.add_days(1).strftime('%Y%m%d'))
        d = DateTimeHelper(year=2022, month=3, day=1)
        self.assertEqual('20220228', d.add_days(-1).strftime('%Y%m%d'))


class TestBatch(unittest.TestCase):
 
    # TODO: テストケースはだいたい以下みたいなヤツで
    # - 設定ファイルがなかったら
    # - 設定ファイルがあっても空／YAMLじゃなかったら
    # - 設定ファイルにあるファイルがなかったら
    # - ファイル出力できない
    # - チャプターファイルがないケース
    # - 置換が使用されないケース
    # 他にもたくさんあると思う

    def test_invalid_parameter(self):
        # TODO: パラメータがない
        # argv = None
        # Batch().execute(argv)
        pass

    def test_invalid_setting_file(self):
        # 設定ファイルがない
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)

        return_code = -1
        try:
            return_code = Batch().execute([
                '-i=' + os.path.join(temp_dir, 'test.yaml'),
                '-o=' + os.path.join(temp_dir, 'test.epub'),
                '-d=1'
            ])
        except:
            pass
        temp.cleanup()

        self.assertEqual(1, return_code)

        # 設定ファイルはあるけど空
        temp = tempfile.TemporaryDirectory(dir=os.path.join(os.path.dirname(__file__), 'data'))
        temp_dir = temp.name
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(temp_dir, 'test.yaml'), 'w', encoding='utf-8') as f:
            f.write('''''')
        return_code = -1
        try:
            Batch().execute([
                '-i=' + os.path.join(temp_dir, 'test.yaml'),
                '-o=' + os.path.join(temp_dir, 'test.epub'),
                '-d=1'
            ])
        except:
            pass
        temp.cleanup()
        
        self.assertEqual(1, return_code)

        # TODO: 設定ファイルはあるけどYAMLフォーマットじゃない
        # TODO: 設定ファイルはあってYAMLフォーマットだけど設定なし
        # TODO: 設定ファイル中のパスが空
        # TODO: 設定ファイル中のパスが無効
        # TODO: 設定ファイル中のパスのファイルが存在しない

if __name__ == '__main__':
    unittest.main()
