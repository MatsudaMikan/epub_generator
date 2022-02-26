# encoding: utf-8
import os
import sys
import re
import html
import shutil
import pathlib
from enum import Enum, IntEnum
import zipfile
import yaml
import traceback
import mimetypes
import logging
import inspect
from argparse import ArgumentError, ArgumentParser
from uuid import uuid4
from datetime import datetime, timedelta
import xml.dom.minidom
import linecache
import time
import uuid
import xml.etree.ElementTree as ET

SCRIPT_DIR = os.path.split(__file__)[0]
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
LOG_DIR = os.path.join(DATA_DIR, 'log')


class Utility(object):
    '''
    ユーティリティクラス
    '''

    @classmethod
    def is_empty(cls, value):
        '''
        空かどうか
        '''
        if value == '':
            return True
        elif value == None:
            return True
        else:
            return False


class FileSystem(object):
    '''
    ファイルシステムクラス
    '''

    @classmethod
    def collect_filepaths(cls, p, filepatharr, name_filter_regex=''):
        '''
        指定されたパス以下の条件にマッチするファイルを収集し、配列で返す
        '''

        if os.path.isdir(p):
            filepatharr.append(p + os.sep)
            for file in os.listdir(path=p):
                FileSystem.collect_filepaths(os.path.join(p, file), filepatharr, name_filter_regex)
        else:
            can_collect = False
            if Utility.is_empty(name_filter_regex):
                can_collect = True
            else:
                can_collect = re.match(name_filter_regex, p)
            if can_collect != None:
                filepatharr.append(p)

        return filepatharr

    @classmethod
    def create_directory(cls, dirpath):
        '''
        ディレクトリ作成
        '''
        pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)

    @classmethod
    def remove_directory(cls, dirpath):
        '''
        ディレクトリ削除（サブディレクトリ・ファイルも削除）
        '''
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)

    @classmethod
    def move_file(cls, filepath, dirpath):
        '''
        ファイル移動
        '''
        shutil.move(filepath, dirpath)

    @classmethod
    def copy_file(cls, filepath, dirpath):
        '''
        ファイルコピー
        '''
        shutil.copy(filepath, dirpath)

    @classmethod
    def remove_file(cls, filepath):
        '''
        ファイル削除
        '''
        if os.path.exists(filepath):
            os.remove(filepath)

    @classmethod
    def exists_file(cls, filepath):
        '''
        ファイル存在チェック
        '''
        return os.path.exists(filepath)

    @classmethod
    def get_file_size(cls, filepath):
        return os.path.getsize(filepath)

    @classmethod
    def create_temp_directory(cls, base_dir=''):
        if Utility.is_empty(base_dir):
            base_dir = os.path.join(os.path.dirname(__file__), 'data')
        temp_dir = os.path.join(base_dir, str(uuid.uuid4().int))
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)
        return temp_dir

class Convert(object):
    '''
    変換クラス
    '''

    @classmethod
    def format(cls, value, format=''):
        '''
        パラメータ値を適切にフォーマットして返す
        '''
        if Utility.is_empty(format):
            return value

        if not(type(value) is str) and not(type(value) is int) and not(type(value) is float):
            return value

        if type(value) is int:
            value = str(value)

        if format == 'number':
            if type(value) is int or type(value) is float:
                return '{:,}'.format(value)
            elif type(value) is str:
                try:
                    return '{:,}'.format(int(value))
                except:
                    return value                    
            else:
                return value
        elif format == 'date':
            if len(value) == 8:
                try:
                    d = DateTimeHelper(int(value[0:4]), int(value[4:6]), int(value[6:8]))
                    return (d.to_yyyymmdd())
                except:
                    return value
            else:
                return value
        elif format == 'datetime':
            if len(value) == 14:
                try:
                    d = DateTimeHelper(int(value[0:4]), int(value[4:6]), int(value[6:8]), int(value[8:10]), int(value[10:12]), int(value[12:14]))
                    return (d.to_yyyymmddhhmiss())
                except:
                    return value
            else:
                return value
        else:
            return value

    @classmethod
    def parse(cls, value, format=''):
        '''
        パラメータ値を適切にパースして返す
        '''
        if Utility.is_empty(value):
            return value

        if not(type(value) is str) and not(type(value) is int) and not(type(value) is float):
            return value

        if format == 'number':
            if type(value) is str:
                if value.find('.') > -1:
                    return float(value.replace(',', ''))
                else:
                    return int(value.replace(',', ''))
            else:
                return value
        elif format == 'date':
            if len(value) == 10:
                try:
                    d = DateTimeHelper(int(value[0:4]), int(value[5:7]), int(value[8:10]))
                    return (d.to_yyyymmdd(datesep=''))
                except:
                    return value
            else:
                return value
        elif format == 'datetime':
            if len(value) == 19:
                try:
                    d = DateTimeHelper(int(value[0:4]), int(value[5:7]), int(value[8:10]), int(value[11:13]), int(value[14:16]), int(value[17:20]))
                    return (d.to_yyyymmddhhmiss(datesep='', timesep='', datetimesep=''))
                except:
                    return value
            else:
                return value
        else:
            return value

    @classmethod
    def get_pretty_xml(cls, data):
        return '\n'.join([line for line in xml.dom.minidom.parseString(data.strip()).toprettyxml().split('\n') if line.strip()])


class DateTimeHelper(datetime):
    '''
    日付時刻ヘルパクラス
    '''

    @classmethod
    def now(cls):

        now = datetime.now()
        return DateTimeHelper(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond, now.tzinfo)

    def to_yyyy(self):
        return self.strftime('%Y')

    def to_yyyymm(self, monthsep='-'):
        return self.strftime('%Y' + monthsep + '%m')

    def to_yyyymmdd(self, datesep='-'):
        return self.strftime('%Y' + datesep + '%m' + datesep + '%d')

    def to_yyyymmddhhmiss(self, datesep='-', timesep=':', datetimesep=' '):
        return self.strftime('%Y' + datesep + '%m' + datesep + '%d' + datetimesep + '%H' + timesep + '%M' + timesep + '%S')

    # def to_yyyymmddhhmissfffff(self, datesep='-', timesep=':', datetimesep=' ', microsecondsep='.'):
    #     return self.strftime('%Y' + datesep + '%m' + datesep + '%d' + datetimesep + '%H' + timesep + '%M' + timesep + '%S' + microsecondsep + '%f')

    def to_yyyymmddhhmiss_iso8601(self):
        # TODO: ユニットテスト
        return self.strftime('%Y-%m-%dT%H:%M:%SZ')

    def add_years(self, num):
        if type(num) != int:
            raise Exception('parameter is not "int" type.')
        if num == 0:
            return self

        return self.add_months(num * 12)

    def add_months(self, num):
        if type(num) != int:
            raise Exception('parameter is not "int" type.')
        if num == 0:
            return self

        year = self.year
        month = self.month
        day = self.day

        step = 1
        if num < 0:
            step = -1
        for i in range(0, num, step):
            if step == 1:
                if month + 1 > 12:
                    year = year + 1
                    month = 1
                else:
                    month = month + 1
            elif step == -1:
                if month - 1 < 1:
                    year = year - 1
                    month = 12
                else:
                    month = month - 1

        daybuf = day
        for i in range(0, 5, 1):
            if self.is_validdate(year, month, daybuf):
                break
            else:
                daybuf = daybuf - 1

        return self.replace(year=year, month=month, day=daybuf)

    def add_days(self, num):
        if type(num) != int:
            raise Exception('parameter is not "int" type.')
        if num == 0:
            return self

        buf = self + timedelta(days=num)
        return DateTimeHelper(buf.year, buf.month, buf.day, buf.hour, buf.minute, buf.second, buf.microsecond, buf.tzinfo)

    @classmethod
    def is_validdate(cls, year, month, day):
        try:
            DateTimeHelper(year, month, day)
            return True
        except ValueError:
            return False


class BatchBase(object):
    '''
    バッチ基底クラス
    '''

    debug = False

    class BatchException(Exception):
        '''
        バッチ例外
        '''
        pass

    class ReturnCode(IntEnum):
        '''
        戻り値
        '''
        NormalEnd = 0
        WarningEnd = 1
        AbnormalEnd = 2

    def __init__(self, batch_name, description, argument_settings, log_file_name='', debug=False):
        '''
        コンストラクタ
        '''
        # パラメータチェック
        if Utility.is_empty(batch_name):
            batch_name = 'Unknown batch'
        if Utility.is_empty(description):
            description = 'Nothing'
        self.debug = debug

        keys = [
            'short_name',
            'long_name',
            'destination',
            'default_value',
            'help'
        ]
        for argument_setting in argument_settings:
            for key in keys:
                if not key in argument_setting:
                    raise Exception('パラメータ{0}は必須です。'.format(key))

        # バッチ名
        self.batch_name = batch_name

        # パラメータ
        # self.parser = ArgumentParser(description=description, exit_on_error=False)
        self.parser = ArgumentParser(description=description)
        for argument_setting in argument_settings:
            short_name = None
            if 'short_name' in argument_setting:
                short_name = argument_setting['short_name']
            long_name = None
            if 'long_name' in argument_setting:
                long_name = argument_setting['long_name']
            destination = None
            if 'destination' in argument_setting:
                destination = argument_setting['destination']
            required = False
            if 'required' in argument_setting:
                required = argument_setting['required']
            default_value = None
            if 'default_value' in argument_setting:
                default_value = argument_setting['default_value']
            help = None
            if 'help' in argument_setting:
                help = argument_setting['help']
            self.parser.add_argument(short_name, long_name, dest=destination, required=required, default=default_value, help=help)

        # ログファイル名決定
        if Utility.is_empty(log_file_name):
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            log_file_name = os.path.basename(module.__file__) + '.log'
        FileSystem.create_directory(LOG_DIR)
        log_file_path = os.path.join(LOG_DIR, log_file_name)

        # ログ設定
        log_level = logging.INFO
        if self.debug:
            log_level = logging.DEBUG
        log_format = '%(asctime)s- %(name)s - %(levelname)s - %(message)s'
        self.log0 = logging.getLogger(self.parser.prog)
        self.log0.setLevel(log_level)
        self.sh = logging.StreamHandler()
        self.sh.setLevel(log_level)
        self.sh.setFormatter(logging.Formatter(log_format))
        self.log0.addHandler(self.sh)
        self.fh = logging.FileHandler(filename=log_file_path, encoding='utf-8')
        self.fh.setLevel(log_level)
        self.fh.setFormatter(logging.Formatter(log_format))
        self.log0.addHandler(self.fh)

    def main(self, args):
        '''
        メイン処理（継承クラスにて実装）
        '''

        raise NotImplementedError()

    def execute(self, argv=[]):
        '''
        バッチ実行
        '''
        self.info_log('-' * 50)
        self.info_log('{0} 処理開始'.format(self.batch_name))

        try:
            # メイン処理呼び出し
            args = self.parser.parse_args(args=argv)
            self.main(args)
            self.info_log('{0} 正常終了'.format(self.batch_name))

            # 戻り値（正常終了）
            return int(BatchBase.ReturnCode.NormalEnd)

        except BatchBase.BatchException as e:
            # 継承クラスでBatchExceptionがスローされたら警告終了
            self.error_log(e)
            self.info_log('{0} 警告終了'.format(self.batch_name))
            return int(BatchBase.ReturnCode.WarningEnd)

        except Exception as e:
            # 継承クラスでExceptionがスローされたら異常終了
            self.error_log(e)
            self.info_log('{0} 異常終了'.format(self.batch_name))
            self.info_log('{0}'.format(traceback.format_exc()))
            return int(BatchBase.ReturnCode.AbnormalEnd)

    def debug_log(self, message):
        '''
        デバッグログ出力
        '''
        self.log0.debug(message)

    def info_log(self, message):
        '''
        インフォメーションログ出力
        '''
        self.log0.info(message)

    def warning_log(self, message):
        '''
        ワーニングログ出力
        '''
        self.log0.warning(message)

    def error_log(self, message):
        '''
        エラーログ出力
        '''
        self.log0.error(message)

    def critical_log(self, message):
        '''
        クリティカルエラーログ出力
        '''
        self.log0.critical(message)

    def exception_info(self):
        '''
        例外情報取得
        '''
        exc_type, exc_obj, tb = sys.exc_info()
        if tb != None:
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
        
            return 'Exception in ({0}, line {1} "{2}"): {3}'.format(filename, lineno, line.strip(), exc_obj)
        else:
            return 'Exception in unknown'

    def __del__(self):
        if 'sh' in vars(self):
            self.sh.close()
            self.log0.removeHandler(self.sh)
        if 'fh' in vars(self):
            self.fh.close()
            self.log0.removeHandler(self.fh)

class Batch(BatchBase):
    '''
    バッチクラス
    '''

    args = None
    setting_yaml_dirpath = ''
    settings = {}
    replaces = {}
    chapters = []
    contents_bind_chapter_indexes = {}
    contents = []
    work_dir_obj = None
    work_dir = ''
    mimetype_filepath = ''
    oebps_dirpath = ''
    oebps_resources_dirpath = ''
    oebps_contents_dirpath = ''

    def __init__(self):
        '''
        コンストラクタ
        '''
        batch_name = 'Epub generator'
        description = '設定ファイルに基づいてepubファイルを作成します。'
        set_argument_settings = []
        set_argument_settings.append({'short_name': '-i', 'long_name': '--input_setting_file', 'destination': 'input_setting_file', 'required': True, 'default_value': '', 'help': '設定ファイルのパス'})
        set_argument_settings.append({'short_name': '-o', 'long_name': '--output_file', 'destination': 'output_file', 'required': True, 'default_value': '', 'help': '出力ファイルのパス'})
        set_argument_settings.append({'short_name': '-d', 'long_name': '--debug', 'destination': 'debug', 'default_value': '0', 'help': 'デバッグ'})
        super(Batch, self).__init__(batch_name, description, set_argument_settings)

    def main(self, args):
        '''
        メイン処理
        '''
        self.args = args

        # パラメータ出力
        self.info_log('設定ファイル: {0}'.format(self.args.input_setting_file))
        self.info_log('出力ファイル: {0}'.format(self.args.output_file))
        if self.args.debug == '1':
            self.info_log('デバッグ: ON')

        # デバッグ
        if self.args.debug == '1':
            self.debug = True

        # ファイルチェック
        if Utility.is_empty(self.args.input_setting_file):
            raise BatchBase.BatchException('設定ファイルを指定してください。')
        if not FileSystem.exists_file(self.args.input_setting_file):
            raise BatchBase.BatchException('設定ファイルが見つかりません。')

        # 作業ディレクトリ作成
        self.work_dir = FileSystem.create_temp_directory()

        try:
            # 設定ファイル読み込み
            self.load_setting_file()

            # mimetypeファイル作成
            self.create_mimetype()

            # META-INFディレクトリ作成
            self.create_meta_inf()
            self.create_meta_inf_container_xml()

            # OEBPSディレクトリ作成
            self.create_oebps()

            # リソースディレクトリ作成
            self.create_oebps_resources()

            # コンテンツディレクトリ作成
            self.create_oebps_contents()

            # リソースファイルの配置
            self.deploy_resource_files()

            # チャプターファイルの読み込み
            self.load_chapter_files()

            # OEPBSコンテンツファイル作成
            self.create_oebps_content_files()

            # opfファイル作成
            self.create_oebps_book_opf()

            # 不要なディレクトリ削除
            paths = [self.oebps_resources_dirpath, self.oebps_contents_dirpath]
            for path in paths:
                files = []
                FileSystem.collect_filepaths(path, files)
                if len(files) == 1:
                    FileSystem.remove_directory(path)

            # epubファイル作成
            self.create_epub()
        except Exception as e:
            self.delete_work_dir()
            raise e
        finally:
            self.delete_work_dir()

    def delete_work_dir(self):
        if not self.debug:
            retry_count = 0
            while (True):
                retry_count += 1
                has_error = False
                try:
                    if FileSystem.exists_file(self.work_dir):
                        FileSystem.remove_directory(self.work_dir)
                except Exception as e:
                    has_error = True
                    self.info_log('一時ファイル／ディレクトリ削除中にエラーが発生しました。リトライします。')
                    if retry_count >= 5:
                        raise BatchBase.BatchException('一時ファイル／ディレクトリ削除中にエラーが発生しました。 {0}'.format(self.exception_info()))
                    time.sleep(5)
                if not has_error:
                    break


    def set_chapter_index_in_contents(self):
        '''
        コンテンツを考慮したチャプターのインデックスをセット
        '''
        self.contents_bind_chapter_indexes = {}

        # OEPBS以下に作成するコンテンツファイルはcontents_1.xhtmlのように1から始まる連番で作成する
        # チャプター分生成するコンテンツを考慮して、生成するコンテンツ×チャプターでの連番をcontents_bind_chapter_indexesにセットしている
        content_count = 0
        for content in self.settings['contents']:

            create_by_chapters_count = content['createByChaptersCount']
            use_chapters = content['useChapters']

            if create_by_chapters_count and len(use_chapters) > 0:
                for use_chapter in use_chapters:
                    content_count += 1
                    self.contents_bind_chapter_indexes[int(use_chapter['chapterIndex'])] = content_count
            else:
                content_count += 1

    def load_setting_file(self):
        '''
        設定ファイル読み込み
        '''
        settings = {}

        # 設定ファイル読み込み
        if not FileSystem.exists_file(self.args.input_setting_file):
            raise BatchBase.BatchException('設定ファイルが見つかりません。 {0}'.format(self.args.input_setting_file))
        if FileSystem.get_file_size(self.args.input_setting_file) == 0:
            raise BatchBase.BatchException('設定ファイルが空です。 {0}'.format(self.args.input_setting_file))
        try:
            with open(self.args.input_setting_file, 'r', encoding='utf-8') as f:
                settings = yaml.load(f, Loader=yaml.SafeLoader)
        except Exception as e:
            raise BatchBase.BatchException('設定ファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.setting_yaml_dirpath = os.path.dirname(self.args.input_setting_file)

        # カレントディレクトリを設定ファイルのディレクトリにする
        # NOTE: 設定ファイル中の相対パスを絶対パス変換するために必要
        os.chdir(self.setting_yaml_dirpath)

        self.info_log('設定ファイル読み込み')

        # ファイルパス補正（相対パス→絶対パス）
        self.reclusive_setting_callback(settings, self.convert_absolute_filepath)

        # ------------------------------
        # ルート設定値補正
        # ------------------------------
        if not 'bookId' in settings or Utility.is_empty(settings['bookId']):
            book_id = uuid4()
            self.warning_log('bookId未指定のためランダムな値を設定します。{0}'.format(book_id))
            settings['bookId'] = book_id
        if not 'language' in settings or Utility.is_empty(settings['language']):
            language = 'ja'
            self.warning_log('language未指定のためデフォルト値を設定します。{0}'.format(language))
            settings['language'] = language
        if not 'modified' in settings or Utility.is_empty(settings['modified']):
            modified = DateTimeHelper.now().to_yyyymmddhhmiss_iso8601()
            self.warning_log('modified未指定のため現在日時を設定します。{0}'.format(modified))
            settings['modified'] = modified
        if not 'title' in settings or Utility.is_empty(settings['title']):
            title = '無題'
            self.warning_log('title未指定のためデフォルト値を設定します。{0}'.format(title))
            settings['title'] = title
        if not 'authorName' in settings or Utility.is_empty(settings['authorName']):
            settings['authorName'] = ''
        if not 'authorRole' in settings or Utility.is_empty(settings['authorRole']):
            settings['authorRole'] = ''
        if not 'authorCopyRight' in settings or Utility.is_empty(settings['authorCopyRight']):
            settings['authorCopyRight'] = ''
        if not 'otherAuthors' in settings or Utility.is_empty(settings['otherAuthors']):
            settings['otherAuthors'] = []
        for other_author in settings['otherAuthors']:
            if not 'authorName' in other_author or Utility.is_empty(settings['authorName']):
                other_author['authorName'] = ''
            if not 'authorRole' in other_author or Utility.is_empty(settings['authorRole']):
                other_author['authorRole'] = ''
            if not 'authorCopyRight' in other_author or Utility.is_empty(settings['authorCopyRight']):
                other_author['authorCopyRight'] = ''
        if not 'pageProgressionDirection' in settings or Utility.is_empty(settings['pageProgressionDirection']):
            settings['pageProgressionDirection'] = ''
        
        # ------------------------------
        # リソース設定値補正
        # ------------------------------
        if not 'resources' in settings or Utility.is_empty(settings['resources']):
            settings['resources'] = {
                'styleSheets': [],
                'images': [],
                'chapters': [],
            }

        # スタイルシート
        stylesheets = []
        if 'styleSheets' in settings['resources']:
            if type(settings['resources']['styleSheets']) is list:
                for stylesheet in settings['resources']['styleSheets']:
                    if 'filePath' in stylesheet and not Utility.is_empty(stylesheet['filePath']):
                        stylesheet['absoluteFilePath'] = stylesheet['filePath']
                        stylesheet['filePath'] = './resources/' + os.path.basename(stylesheet['absoluteFilePath'])
                    stylesheets.append(stylesheet)
        settings['resources']['styleSheets'] = stylesheets

        # 画像
        images = []
        if 'images' in settings['resources']:
            if type(settings['resources']['images']) is list:
                for image in settings['resources']['images']:
                    if 'filePath' in image and not Utility.is_empty(image['filePath']):
                        image['absoluteFilePath'] = image['filePath']
                        image['filePath'] = './resources/' + os.path.basename(image['absoluteFilePath'])
                    images.append(image)
        settings['resources']['images'] = images

        # チャプター
        chapters = {
            'replaces': [],
            'files': [],
        }
        if 'chapters' in settings['resources']:
            replaces = []
            if 'replaces' in settings['resources']['chapters']:
                if type(settings['resources']['chapters']['replaces']) is list:
                    for replace in settings['resources']['chapters']['replaces']:
                        replace_type = ''
                        if 'type' in replace and not Utility.is_empty(replace['type']):
                            replace_type = replace['type']
                        place_holder = ''
                        if 'placeHolder' in replace and not Utility.is_empty(replace['placeHolder']):
                            place_holder = replace['placeHolder']
                        replace_content = ''
                        if 'replaceContent' in replace and not Utility.is_empty(replace['replaceContent']):
                            replace_content = replace['replaceContent']
                        if type != '' and place_holder != '' and replace_content != '':
                            replaces.append({
                                'type': replace_type,
                                'placeHolder': replace_content,
                                'replaceContent': replace_content,
                            })
            chapters['replaces'] = replaces

            files = []
            if 'files' in settings['resources']['chapters']:
                if type(settings['resources']['chapters']['files']) is list:
                    for file in settings['resources']['chapters']['files']:
                        title = ''
                        if 'title' in file:
                            title = file['title']
                        filetype = ''
                        if 'fileType' in file:
                            fileType = file['fileType']
                        absolute_file_path = ''
                        if 'filePath' in file:
                            absolute_file_path = file['filePath']
                        files.append({
                            'title': title,
                            'fileType': filetype,
                            'filePath': '',     # チャプターのファイルパスは後で補正
                            'absoluteFilePath': absolute_file_path,
                        })
            chapters['files'] = files
        settings['resources']['chapters'] = chapters

        # コンテンツ
        contents = []
        if 'contents' in settings:
            files = []
            if type(settings['contents']) is list:
                for file in settings['contents']:
                    absolute_file_path = ''
                    if 'filePath' in file and not Utility.is_empty(file['filePath']):
                        absolute_file_path = file['filePath']
                    is_navigation_content = False
                    if 'isNavigationContent' in file and not Utility.is_empty(file['isNavigationContent']):
                        if type(file['isNavigationContent']) is bool:
                            is_navigation_content = file['isNavigationContent']
                    use_navigation_content = True
                    if 'useNavigationContent' in file and not Utility.is_empty(file['useNavigationContent']):
                        if type(file['useNavigationContent']) is bool:
                            use_navigation_content = file['useNavigationContent']
                    create_by_chapters_count = False
                    if 'createByChaptersCount' in file and not Utility.is_empty(file['createByChaptersCount']):
                        if type(file['createByChaptersCount']) is bool:
                            create_by_chapters_count = file['createByChaptersCount']
                    replaces = []
                    if 'replaces' in file:
                        if type(file['replaces']) is list:
                            for replace in file['replaces']:
                                replace_type = ''
                                if 'type' in replace and not Utility.is_empty(replace['type']):
                                    replace_type = replace['type']
                                place_holder = ''
                                if 'placeHolder' in replace and not Utility.is_empty(replace['placeHolder']):
                                    place_holder = replace['placeHolder']
                                replace_content = ''
                                if 'replaceContent' in replace and not Utility.is_empty(replace['replaceContent']):
                                    replace_content = replace['replaceContent']
                                if type != '' and place_holder != '' and replace_content != '':
                                    replaces.append({
                                        'type': replace_type,
                                        'placeHolder': replace_content,
                                        'replaceContent': replace_content,
                                    })
                    use_chapters = []
                    if 'useChapters' in file:
                        if type(file['useChapters']) is list:
                            for use_chapter in file['useChapters']:
                                if 'chapterIndex' in use_chapter and not Utility.is_empty(use_chapter['chapterIndex']):
                                    try:
                                        chapters['files'][use_chapter['chapterIndex'] - 1]
                                    except IndexError:
                                        raise BatchBase.BatchException('コンテンツのuseChaptersに無効なチャプターが指定されています。コンテンツ: {0}／チャプター: {1}'.format(filepath, use_chapter['chapterIndex']))
                                    use_chapters.append({
                                        'chapterIndex': use_chapter['chapterIndex']
                                    })

                    contents.append({
                        'filePath': '',     # コンテンツのファイルパスは後で補正
                        'absoluteFilePath': absolute_file_path,
                        'isNavigationContent': is_navigation_content,
                        'useNavigationContent': use_navigation_content,
                        'createByChaptersCount': create_by_chapters_count,
                        'useChapters': use_chapters,
                        'replaces': replaces,
                    })

        # ------------------------------
        # 設定ファイルのチェック
        # ------------------------------
        if len(contents) == 0:
            raise BatchBase.BatchException('コンテンツがありません。{0}'.format(self.args.input_setting_file))

        # 目次コンテンツがない場合はダミーの目次コンテンツを自動生成するもmanifestに追記しないようにし、エラーチェックを回避する
        has_navigation_content = False
        for content in contents:
            if content['isNavigationContent']:
                has_navigation_content = True
                break
        if not has_navigation_content:
            self.warning_log('目次コンテンツ未指定のためダミーの目次コンテンツを作成します。')
            navigation_content_file = os.path.join(self.work_dir, str(uuid4().int))
            data = '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2011/epub">
<head>
	<title>Table of contents</title>
	<meta charset="UTF-8" />
</head>
<body>
	<nav xmlns:epub="http://www.idpf.org/2007/ops" epub:type="toc">
        <ol>
            <li><a href="{$setting.contents.1.filePath}">First conetnt</a></li>
        </ol>
	</nav>
</body>
</html>
            '''
            try:
                if FileSystem.exists_file(navigation_content_file):
                    FileSystem.remove_file(navigation_content_file)
                with open(navigation_content_file, 'w', encoding='utf-8') as f:
                    f.write(Convert.get_pretty_xml(data))
            except Exception as e:
                raise BatchBase.BatchException('目次コンテンツファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

            contents.append({
                'filePath': '',
                'absoluteFilePath': navigation_content_file,
                'isNavigationContent': True,
                'useNavigationContent': True,
                'createByChaptersCount': False,
                'useChapters': [],
                'replaces': [],
            })

        settings['contents'] = contents

        # ------------------------------
        # データ変換
        # ------------------------------
        self.settings = settings

        # コンテンツを考慮したチャプターのインデックスをセット
        self.set_chapter_index_in_contents()

        # チャプターのファイルパスは以下のルールで補正
        # - text: ./contents_xxx.xhtmlの相対ファイルパス（コンテンツ数×チャプター数を考慮した連番ファイル）
        # - text以外: ./contentsへの相対ファイルパス
        chapter_count = 0
        for file in self.settings['resources']['chapters']['files']:
            chapter_count += 1
            if chapter_count in self.contents_bind_chapter_indexes:
                if file['fileType'] == 'text':
                    file['filePath'] = './' + 'contents_{0}.xhtml'.format(self.contents_bind_chapter_indexes[chapter_count])
                else:
                    file['filePath'] = './' + 'contents/{0}'.format(os.path.basename(file['absoluteFilePath']))

        # コンテンツのファイルパスを補正
        content_count = 0
        for content in self.settings['contents']:
            content_count += 1
            if len(content['useChapters']) > 0:
                content['filePath'] = './' + 'contents_{0}.xhtml'.format(content_count)

        # 設定ファイルの内容を一次元配列で持つ
        self.convert_yaml_to_list('setting', self.settings, self.replaces)
        for key in self.replaces:
            self.debug_log('{0} => {1}'.format(key, self.replaces[key]))

    def deploy_resource_files(self):
        '''
        リソースファイル配置
        '''

        # スタイルシート: /OEBPS/resources
        for stylesheet in self.settings['resources']['styleSheets']:
            if stylesheet['absoluteFilePath'] != '':
                if not FileSystem.exists_file(stylesheet['absoluteFilePath']):
                    raise BatchBase.BatchException('指定されたファイルが見つかりません。 {0}'.format(stylesheet['absoluteFilePath']))
                try:
                    FileSystem.copy_file(stylesheet['absoluteFilePath'], self.oebps_resources_dirpath)
                except Exception as e:
                    raise BatchBase.BatchException('チャプターファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))
                self.info_log('リソースファイルのコピー - /OEBPS/resources/{0}'.format(os.path.basename(stylesheet['absoluteFilePath'])))

        # 画像: /OEBPS/resources
        for image in self.settings['resources']['images']:
            if stylesheet['absoluteFilePath'] != '':
                if not FileSystem.exists_file(image['absoluteFilePath']):
                    raise BatchBase.BatchException('指定されたファイルが見つかりません。 {0}'.format(image['absoluteFilePath']))
                try:
                    FileSystem.copy_file(image['absoluteFilePath'], self.oebps_resources_dirpath)
                except Exception as e:
                    raise BatchBase.BatchException('リソースファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))
                self.info_log('リソースファイルのコピー - /OEBPS/resources/{0}'.format(os.path.basename(image['absoluteFilePath'])))

        # コンテンツ（画像のみ）: /OEBPS/contents
        for file in self.settings['resources']['chapters']['files']:
            if not file['fileType'] == 'text' and file['absoluteFilePath'] != '':
                if not FileSystem.exists_file(file['absoluteFilePath']):
                    raise BatchBase.BatchException('指定されたファイルが見つかりません。 {0}'.format(file['absoluteFilePath']))
                try:
                    FileSystem.copy_file(file['absoluteFilePath'], self.oebps_contents_dirpath)
                except Exception as e:
                    raise BatchBase.BatchException('リソースファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))
                self.info_log('リソースファイルのコピー - /OEBPS/contents/{0}'.format(os.path.basename(file['absoluteFilePath'])))

    def load_chapter_files(self):
        '''
        チャプターファイル読み込み
        '''

        chapter_count = 0

        chapters_replaces = self.settings['resources']['chapters']['replaces']

        for file in self.settings['resources']['chapters']['files']:
            chapter_count += 1

            if chapter_count in self.contents_bind_chapter_indexes:
                title = file['title']
                filetype = file['fileType']
                filepath = ''
                if filetype == 'text':
                    filepath = file['absoluteFilePath']
                    if not FileSystem.exists_file(filepath):
                        raise BatchBase.BatchException('チャプターファイルが見つかりません。: {0}'.format(filepath))
                else:
                    filepath = file['filePath']
                body = ''
                if filetype == 'text':
                    # テキストの場合は本文データの置換実行
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.read().splitlines()
                            for line in lines:
                                line = line + '\n'
                                if len(chapters_replaces) > 0:
                                    # チャプター共通の置換
                                    line = self.content_replace(line, chapters_replaces)
                                    # 該当チャプターの置換
                                    line = self.content_replace(line, file['replaces'])
                                line = self.content_replace_by_setting(line)
                                body = body + line
                    except Exception as e:
                        raise BatchBase.BatchException('チャプターファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))

                # チャプターデータを収集
                replace_filepath = ''
                if filetype == 'text':
                    replace_filepath = os.path.join(self.oebps_dirpath, 'contents_{0}.xhtml'.format(self.contents_bind_chapter_indexes[chapter_count]))
                else:
                    replace_filepath = filepath
                self.chapters.append({
                    'title': title,
                    'body': body,
                    'fileType': filetype,
                    'filePath': filepath,
                    'replaces': [
                        {
                            'type': 'simple',
                            'placeHolder': '{$chapter.title}',
                            'replaceContent': title,
                        },
                        {
                            'type': 'simple',
                            'placeHolder': '{$chapter.body}',
                            'replaceContent': body,
                        },
                        {
                            'type': 'simple',
                            'placeHolder': '{$chapter.filePath}',
                            'replaceContent': replace_filepath
                        },
                    ]
                })

                self.debug_log('リソースファイルの読み込み - {0}'.format(filepath))

    def create_mimetype(self):
        '''
        ファイル作成 - /mimetype
        '''

        self.mimetype_filepath = os.path.join(self.work_dir, 'mimetype')

        if FileSystem.exists_file(self.mimetype_filepath):
            FileSystem.remove_file(self.mimetype_filepath)

        try:
            with open(self.mimetype_filepath, 'w', encoding='utf-8') as f:
                f.write('application/epub+zip')
        except Exception as e:
            raise BatchBase.BatchException('mimetypeファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('ファイル作成 - /mimetype')

    def create_meta_inf(self):
        '''
        ディレクトリ作成 - /META-INF
        '''

        self.meta_inf_dirpath = os.path.join(self.work_dir, 'META-INF')

        try:
            if FileSystem.exists_file(self.meta_inf_dirpath):
                FileSystem.remove_directory(self.meta_inf_dirpath)
            FileSystem.create_directory(self.meta_inf_dirpath)
        except Exception as e:
            raise BatchBase.BatchException('/META-INFディレクトリ作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('ディレクトリ作成 - /META-INF')

    def create_meta_inf_container_xml(self):
        '''
        ファイル作成 - /META-INF/container.xml
        '''

        container_xml_filepath = os.path.join(self.meta_inf_dirpath, 'container.xml')

        data = '''
<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
	<rootfiles>
		<rootfile full-path="OEBPS/book.opf" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>
'''
        try:
            if FileSystem.exists_file(container_xml_filepath):
                FileSystem.remove_file(container_xml_filepath)
            with open(container_xml_filepath, 'w', encoding='utf-8') as f:
                f.write(Convert.get_pretty_xml(data))
        except Exception as e:
            raise BatchBase.BatchException('/META-INF/container.xmlファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('ファイル作成 - /META-INF/container.xml')

    def create_oebps(self):
        '''
        ディレクトリ作成 - /OEBPS
        '''

        self.oebps_dirpath = os.path.join(self.work_dir, 'OEBPS')

        try:
            if FileSystem.exists_file(self.oebps_dirpath):
                FileSystem.remove_directory(self.oebps_dirpath)
            FileSystem.create_directory(self.oebps_dirpath)
        except Exception as e:
            raise BatchBase.BatchException('/META-INFディレクトリ作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('ディレクトリ作成 - /OEBPS')

    def create_oebps_resources(self):
        '''
        ディレクトリ作成 - /OEBPS/resources
        '''

        self.oebps_resources_dirpath = os.path.join(self.oebps_dirpath, 'resources')

        try:
            if FileSystem.exists_file(self.oebps_resources_dirpath):
                FileSystem.remove_directory(self.oebps_resources_dirpath)
            FileSystem.create_directory(self.oebps_resources_dirpath)
        except Exception as e:
            raise BatchBase.BatchException('/OEBPS/resourcesディレクトリ作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('ディレクトリ作成 - /OEBPS/resources')

    def create_oebps_contents(self):
        '''
        ディレクトリ作成 - /OEBPS/contents
        '''

        self.oebps_contents_dirpath = os.path.join(self.oebps_dirpath, 'contents')

        try:
            if FileSystem.exists_file(self.oebps_contents_dirpath):
                FileSystem.remove_directory(self.oebps_contents_dirpath)
            FileSystem.create_directory(self.oebps_contents_dirpath)
        except Exception as e:
            raise BatchBase.BatchException('/OEBPS/contentsディレクトリ作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('ディレクトリ作成 - /OEBPS/contents')

    def create_oebps_content_files(self):
        '''
        コンテンツファイル作成
        '''
        self.contents = []

        content_count = 0
        for content in self.settings['contents']:
            filepath = content['absoluteFilePath']
            create_by_chapters_count = content['createByChaptersCount']
            use_chapters = content['useChapters']

            if not FileSystem.exists_file(filepath):
                raise BatchBase.BatchException('コンテンツファイルが見つかりません。: {0}'.format(filepath))

            if create_by_chapters_count and len(use_chapters) > 0:
                # ------------------------------
                # チャプター分のコンテンツファイル作成
                # ------------------------------
                for use_chapter in use_chapters:
                    content_count += 1

                    # コンテンツファイル読み込み
                    content_data = ''
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content_data = f.read()
                    except Exception as e:
                        raise BatchBase.BatchException('コンテンツファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))

                    # 置換
                    chapter_index = int(use_chapter['chapterIndex'])
                    chapter = self.chapters[chapter_index - 1]
                    if chapter_index <= len(self.chapters):
                        content_data = self.content_replace(content_data, chapter['replaces'])

                    content_data = self.content_replace(content_data, content['replaces'])
                    content_data = self.content_replace_by_setting(content_data)

                    # コンテンツファイル作成
                    oebps_xhtml_filepath = os.path.join(self.oebps_dirpath, 'contents_{0}.xhtml'.format(content_count))
                    try:
                        with open(oebps_xhtml_filepath, 'w', encoding='utf-8') as f:
                            f.write(content_data)
                    except Exception as e:
                        raise BatchBase.BatchException('コンテンツファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

                    # コンテンツファイルデータ収集
                    self.contents.append({
                        'filePath': chapter['filePath'],
                        'isNavigationContent': content['isNavigationContent'],
                    })

                    self.info_log('ファイル作成 - /OEBPS/{0}'.format(os.path.basename(oebps_xhtml_filepath)))
            else:
                # ------------------------------
                # 単一のコンテンツファイル作成
                # ------------------------------
                content_count += 1

                # コンテンツファイル読み込み
                content_data = ''
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content_data = f.read()
                except Exception as e:
                    raise BatchBase.BatchException('コンテンツファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))

                # 置換
                content_data = self.content_replace(content_data, content['replaces'])
                content_data = self.content_replace_by_setting(content_data)

                # コンテンツファイル作成
                oebps_xhtml_filepath = os.path.join(self.oebps_dirpath, 'contents_{0}.xhtml'.format(content_count))
                try:
                    with open(oebps_xhtml_filepath, 'w', encoding='utf-8') as f:
                        f.write(content_data)
                except Exception as e:
                    raise BatchBase.BatchException('コンテンツファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

                # コンテンツファイルデータ収集
                self.contents.append({
                    'filePath': './{0}'.format(os.path.basename(oebps_xhtml_filepath)),
                    'isNavigationContent': content['isNavigationContent'],
                })

                self.info_log('ファイル作成 - /OEBPS/{0}'.format(os.path.basename(oebps_xhtml_filepath)))

    def create_oebps_book_opf(self):
        '''
        ファイル作成 - /OEBPS/book.opf
        '''
        xml_opf = ET.Element('package', {'xmlns': 'http://www.idpf.org/2007/opf', 'unique-identifier': 'BookID', 'version': '3.0', 'xml:lang': 'ja'})
        xml_opf_metadata = ET.SubElement(xml_opf, 'metadata', {'xmlns:dc': 'http://purl.org/dc/elements/1.1/'})

        replace_hash = self.settings

        # ID
        if not Utility.is_empty(replace_hash['bookId']):
            dc_identifier = ET.SubElement(xml_opf_metadata, 'dc:identifier', {'id': 'BookID'})
            dc_identifier.text = 'urn:uuid:{0}'.format(replace_hash['bookId'])
            meta_identifier = ET.SubElement(xml_opf_metadata, 'meta', {'property': 'dcterms:identifier', 'id': 'uuid'})
            meta_identifier.text = 'urn:uuid:{0}'.format(replace_hash['bookId'])

        # 言語
        if not Utility.is_empty(replace_hash['language']):
            dc_language = ET.SubElement(xml_opf_metadata, 'dc:language')
            dc_language.text = replace_hash['language']
            meta_language = ET.SubElement(xml_opf_metadata, 'meta', {'property': 'dcterms:language', 'id': 'pub-lang'})
            meta_language.text = replace_hash['language']

        # 更新日時
        if not Utility.is_empty(replace_hash['modified']):
            dc_modified = ET.SubElement(xml_opf_metadata, 'dc:date')
            dc_modified.text = replace_hash['modified']
            meta_modified = ET.SubElement(xml_opf_metadata, 'meta', {'property': 'dcterms:modified'})
            meta_modified.text = replace_hash['modified']

        # タイトル
        if not Utility.is_empty(replace_hash['title']):
            dc_title = ET.SubElement(xml_opf_metadata, 'dc:title')
            dc_title.text = replace_hash['title']
            meta_title = ET.SubElement(xml_opf_metadata, 'meta', {'property': 'dcterms:title', 'id': 'dcterm-title'})
            meta_title.text = replace_hash['title']

        # 著者
        if not Utility.is_empty(replace_hash['authorName']):
            dc_author = ET.SubElement(xml_opf_metadata, 'dc:creator', {'id': 'creatorMain'})
            dc_author.text = replace_hash['authorName']
            meta_author = ET.SubElement(xml_opf_metadata, 'meta', {'refines': '#creatorMain', 'property': 'role', 'scheme': 'marc:relators', 'id': 'roleMain'})
            meta_author.text = replace_hash['authorName']

        # 著者／寄与者
        other_author_count = 0
        for other_author in replace_hash['otherAuthors']:
            if not Utility.is_empty(other_author['authorName']):
                other_author_count += 1
                dc_other_author = ET.SubElement(xml_opf_metadata, 'dc:creator', {'id': 'creator{0}'.format(other_author_count)})
                dc_other_author.text = other_author['authorName']
                meta_other_author = ET.SubElement(xml_opf_metadata, 'meta', {'refines': '#creator{0}'.format(other_author_count), 'property': 'role', 'scheme': 'marc:relators', 'id': 'role{0}'.format(other_author_count)})
                meta_other_author.text = other_author['authorName']

        # コピーライト
        if not Utility.is_empty(replace_hash['authorCopyRight']):
            dc_author_copyright = ET.SubElement(xml_opf_metadata, 'dc:rights')
            dc_author_copyright.text = replace_hash['authorCopyRight']
            meta_author_copyright = ET.SubElement(xml_opf_metadata, 'meta', {'property': 'dcterms:rights', 'id': 'rights'})
            meta_author_copyright.text = replace_hash['authorCopyRight']

        # カバー
        for image in self.settings['resources']['images']:
            if image['isCover']:
                meta_cover = ET.SubElement(xml_opf_metadata, 'meta', {'name': 'cover', 'content': 'cover-image'})
                break

        # マニフェスト／スパイン
        xml_manifest = ET.SubElement(xml_opf, 'manifest')
        xml_spine_attributes = {}
        if not Utility.is_empty(replace_hash['pageProgressionDirection']):
            xml_spine_attributes['page-progression-direction'] = replace_hash['pageProgressionDirection']
        xml_spine = ET.SubElement(xml_opf, 'spine', xml_spine_attributes)

        # リソース（スタイルシート）からマニフェスト作成
        stylesheet_count = 0
        for stylesheet in self.settings['resources']['styleSheets']:
            stylesheet_count += 1
            xml_manifest_stylesheet = ET.SubElement(xml_manifest, 'item', {'id': 'css_{0}'.format(stylesheet_count), 'href': stylesheet['filePath'], 'media-type': mimetypes.guess_type(stylesheet['filePath'])[0]})

        # リソース（画像）からマニフェスト作成
        image_count = 0
        setted_cover = False
        for image in self.settings['resources']['images']:
            image_count += 1

            # 表紙がある場合は属性をセット
            properties = {}
            if image['isCover'] and not setted_cover:
                properties['properties'] = 'cover-image'
                setted_cover = True
            properties['id'] = 'image_{0}'.format(image_count)
            properties['href'] = image['filePath']
            properties['media-type'] = mimetypes.guess_type(image['filePath'])[0]

            xml_manifest_image = ET.SubElement(xml_manifest, 'item', properties)

        # コンテンツからマニフェスト・スパイン作成
        content_count = 0
        for content in self.contents:
            content_count += 1

            # 目次がある場合は属性をセット
            properties = {}
            if content['isNavigationContent']:
                properties['properties'] = 'nav'
            properties['id'] = 'content_{0}'.format(content_count)
            properties['href'] = content['filePath']
            properties['media-type'] = mimetypes.guess_type(content['filePath'])[0]

            xml_manifest_content = ET.SubElement(xml_manifest, 'item', properties)
            xml_spine_content = ET.SubElement(xml_spine, 'itemref', {'idref': 'content_{0}'.format(content_count)})

        # book.opfファイル作成
        oebps_book_opf_filepath = os.path.join(self.oebps_dirpath, 'book.opf')
        if FileSystem.exists_file(oebps_book_opf_filepath):
            FileSystem.remove_file(oebps_book_opf_filepath)

        try:
            with open(oebps_book_opf_filepath, 'w', encoding='utf-8') as f:
                f.write(Convert.get_pretty_xml(ET.tostring(xml_opf, encoding='utf-8')))
        except Exception as e:
            raise BatchBase.BatchException('/OEBPS/book.opfファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('ファイル作成 - /OEBPS/book.opf')

    def create_epub(self):
        '''
        epubファイル作成
        '''

        # ------------------------------
        # epubファイル作成
        # ------------------------------
        if FileSystem.exists_file(self.args.output_file):
            FileSystem.remove_file(self.args.output_file)
        try:
            with zipfile.ZipFile(self.args.output_file, 'w', zipfile.ZIP_DEFLATED) as f:
                # mimetypeはzipファイルの先頭に、かつ圧縮なしで登録
                f.write(self.mimetype_filepath, 'mimetype', zipfile.ZIP_STORED)

                # META-INFディレクトリ登録
                filepaths = []
                FileSystem.collect_filepaths(self.meta_inf_dirpath, filepaths)
                for filepath in filepaths:
                    f.write(filepath, filepath.replace(self.work_dir, ''), zipfile.ZIP_DEFLATED)

                # OEBPSディレクトリ登録
                filepaths = []
                FileSystem.collect_filepaths(self.oebps_dirpath, filepaths)
                for filepath in filepaths:
                    f.write(filepath, filepath.replace(self.work_dir, ''), zipfile.ZIP_DEFLATED)
        except Exception as e:
            raise BatchBase.BatchException('epubファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('ファイル作成 - ' + self.args.output_file)

    def reclusive_setting_callback(self, data, callback):
        '''
        設定ファイルの設定値に対して再帰的に処理する
        '''
        if type(data) is list:
            for value in data:
                self.reclusive_setting_callback(value, callback)
        elif type(data) is dict:
            for key in data:
                if not type(data[key]) is list and not type(data[key]) is dict:
                    data[key] = callback(key, data[key])
                self.reclusive_setting_callback(data[key], callback)

    def convert_absolute_filepath(self, key, value):
        '''
        設定ファイル中の設定値filePathに指定された相対パスを絶対パスに補正する
        '''
        if key == 'filePath' and type(value) == str and value != '':
            # if len(value) > 2 and (value[:2] == './' or value[:2] == '.\\'):
            #     return re.sub('^\.', re.sub(r'\\', r'\\\\', self.setting_yaml_dirpath), value)
            return os.path.abspath(value)
        else:
            return value

    def content_replace(self, content, replaces):
        '''
        コンテンツ置換
        '''

        if Utility.is_empty(content):
            return content
        if replaces == None or len(replaces) == 0:
            return content

        simple_replaces = []
        regex_replaces = []

        for replace in replaces:
            if 'type' in replace:
                # YAMLで記載を省略するとNoneになるケースがあるため、置換データを補正する
                if replace['replaceContent'] == None:
                    replace['replaceContent'] = ''

                # シンプル／正規表現タイプの検索／置換セットを追加する
                if replace['type'] == 'simple':
                    simple_replaces.append(replace)
                elif replace['type'] == 'regex':
                    regex_replaces.append(replace)
            else:
                simple_replaces.append(replace)

        # 最初に正規表現での置換を実行
        for replace in regex_replaces:
            content = re.sub(replace['placeHolder'], replace['replaceContent'], content)

        # 単純置換を実行
        for replace in simple_replaces:
            content = content.replace(replace['placeHolder'], replace['replaceContent'])

        return content

    def content_replace_by_setting(self, content):
        for key in self.replaces:
            content = content.replace('{' + key + '}', str(self.replaces[key]))
        return content

    def convert_yaml_to_list(self, parent_data, source, dest):
        '''
        YAMLファイルのデータを全て一次元配列に変換
        '''

        for key in source:
            if type(source[key]) is dict:
                self.convert_yaml_to_list(parent_data + '.' + key, source[key], dest)
            elif type(source[key]) is list:
                counter = 0
                for data in source[key]:
                    counter += 1
                    self.convert_yaml_to_list(parent_data + '.' + key + '.' + str(counter), data, dest)
            else:
                value = ''
                if source[key] != None:
                    value = source[key]
                dest['$' + parent_data + '.' + key] = value


if __name__ == '__main__':
    argv = sys.argv
    del argv[0]
    exit(Batch().execute(argv))
