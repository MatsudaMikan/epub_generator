# encoding: utf-8
import os
import sys
import re
import html
import shutil
import pathlib
import subprocess
from enum import Enum, IntEnum
import zipfile
import yaml     # NOTE: pyyamlは5.4.1でしか動作確認していない（python -m pip install pyyaml==5.4.1）
import traceback
import mimetypes
import logging
import inspect
from argparse import ArgumentError, ArgumentParser
from uuid import uuid4
from datetime import datetime, timedelta
import xml.dom.minidom
import linecache
import tempfile
import time

SCRIPT_DIR = os.path.split(__file__)[0]
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
LOG_DIR = os.path.join(DATA_DIR, 'log')


class FileSystem(object):
    '''
    ファイルシステムクラス
    '''

    @classmethod
    def collect_filepaths(cls, p, filepatharr, name_filter='', collect_file_func=None):
        '''
        指定されたパス以下の条件にマッチするファイルを収集し、配列で返す
        '''

        if os.path.isdir(p):
            filepatharr.append(p + os.sep)
            for file in os.listdir(path=p):
                FileSystem.collect_filepaths(os.path.join(
                    p, file), filepatharr, name_filter, collect_file_func)
        else:
            can_collect = False
            if name_filter == "":
                can_collect = True
            else:
                can_collect = re.match(name_filter, p)
            if can_collect != None:
                filepatharr.append(p)
                if collect_file_func != None:
                    collect_file_func(p)

        return filepatharr

    @classmethod
    def create_directory(cls, dirpath):
        '''
        ディレクトリ作成
        '''
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(dirpath)

    @classmethod
    def create_directory_tree(cls, dirpath):
        '''
        ディレクトリツリー作成
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


class Convert(object):
    '''
    変換クラス
    '''

    @classmethod
    def format(cls, value, format=''):
        '''
        パラメータ値を適切にフォーマットして返す
        '''
        if format == '':
            return html.escape(str(value))

        if format == 'date':
            if len(value) == 8:
                d = DateTimeHelper(int(value[0:4]), int(
                    value[4:6]), int(value[6:8]))
                return (d.to_yyyymmdd())
            else:
                return value

        elif format == 'datetime':
            if len(value) == 14:
                d = DateTimeHelper(int(value[0:4]), int(value[4:6]), int(
                    value[6:8]), int(value[8:10]), int(value[10:12]), int(value[12:14]))
                return (d.to_yyyymmddhhmmss())
            else:
                return value

        else:
            return html.escape(str(value))

    @classmethod
    def parse(cls, value, format=''):
        '''
        パラメータ値を適切にパースして返す
        '''
        if value == '':
            return value

        if format == 'date':
            if len(value) == 10:
                d = DateTimeHelper(int(value[0:4]), int(
                    value[5:7]), int(value[8:10]))
                return (d.to_yyyymmdd(''))
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

    def to_yyyy(self, monthsep='-'):
        return self.strftime('%Y')

    def to_yyyymm(self, monthsep='-'):
        return self.strftime('%Y' + monthsep + '%m')

    def to_yyyymmdd(self, datesep='-'):
        return self.strftime('%Y' + datesep + '%m' + datesep + '%d')

    def to_yyyymmddhhmiss(self, datesep='-', timesep=':', datetimesep=' '):
        return self.strftime('%Y' + datesep + '%m' + datesep + '%d' + datetimesep + '%H' + timesep + '%M' + timesep + '%S')

    def to_yyyymmddhhmissffffff(self, datesep='-', timesep=':', datetimesep=' ', floatsep='.'):
        return self.strftime('%Y' + datesep + '%m' + datesep + '%d' + datetimesep + '%H' + timesep + '%M' + timesep + '%S' + floatsep + '%f')

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
        if batch_name == '':
            batch_name = 'Unknown batch'
        if description == '':
            description = 'Nothing'
        self.debug = debug

        keys = [
            'short_name','long_name','destination','default_value','help'
        ]
        for argument_setting in argument_settings:
            for key in keys:
                if not key in argument_setting:
                    raise Exception('パラメータ{0}は必須です。'.format(key))

        # バッチ名
        self.batch_name = batch_name

        # パラメータ
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
        if log_file_name == '':
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            log_file_name = os.path.basename(module.__file__) + '.log'
        FileSystem.create_directory_tree(LOG_DIR)
        log_file_path = os.path.join(LOG_DIR, log_file_name)

        # ログ設定
        log_level = logging.INFO
        if self.debug:
            log_level = logging.DEBUG
        log_format = '%(asctime)s- %(name)s - %(levelname)s - %(message)s'
        self.log0 = logging.getLogger(self.parser.prog)
        self.log0.setLevel(log_level)
        sh = logging.StreamHandler()
        sh.setLevel(log_level)
        sh.setFormatter(logging.Formatter(log_format))
        self.log0.addHandler(sh)
        fh = logging.FileHandler(filename=log_file_path, encoding='utf-8')
        fh.setLevel(log_level)
        fh.setFormatter(logging.Formatter(log_format))
        self.log0.addHandler(fh)

    def main(self, args):
        '''
        メイン処理（継承クラスにて実装）
        '''

        raise NotImplementedError()

    def execute(self):
        '''
        バッチ実行
        '''
        self.info_log('{0}'.format('-' * 50))
        self.info_log('{0} 処理開始'.format(self.batch_name))

        try:
            # メイン処理呼び出し
            args = self.parser.parse_args()
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
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        
        return 'Exception in ({0}, line {1} "{2}"): {3}'.format(filename, lineno, line.strip(), exc_obj)

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
    mimetype_filepath = ''
    oebps_dirpath = ''
    oebps_resources_dirpath = ''
    work_dir = ''
    debug = False

    def __init__(self):
        '''
        コンストラクタ
        '''
        batch_name = 'Epub generator'
        description = '設定ファイルに基づいてepubファイルを作成します。'
        set_argument_settings = []
        set_argument_settings.append({'short_name': '-i', 'long_name': '--input_setting_file', 'destination': 'input_setting_file', 'required': True, 'default_value': '', 'help': '設定ファイルのパス'})
        set_argument_settings.append({'short_name': '-o', 'long_name': '--output_file', 'destination': 'output_file', 'required': True, 'default_value': '', 'help': '出力ファイルのパス'})
        set_argument_settings.append({'short_name': '-d', 'long_name': '--debug', 'destination': 'debug', 'default_value': 0, 'help': 'デバッグ'})
        super(Batch, self).__init__(batch_name, description, set_argument_settings)

    def main(self, args):
        '''
        メイン処理
        '''
        self.args = args

        # デバッグ
        if self.args.debug == 1:
            self.debug = True

        # ファイルチェック
        if self.args.input_setting_file == '':
            raise BatchBase.BatchException('設定ファイルを指定してください。')
        if not FileSystem.exists_file(self.args.input_setting_file):
            raise BatchBase.BatchException('設定ファイルが見つかりません。')

        # 一時ディレクトリ作成
        self.work_dir = tempfile.TemporaryDirectory(dir='./data').name
        if FileSystem.exists_file(self.work_dir):
            try:
                FileSystem.remove_directory(self.work_dir)
                self.info_log('出力ディレクトリのファイルを削除しました。 {0}'.format(self.work_dir))
                FileSystem.create_directory_tree(self.work_dir)
            except Exception as e:
                raise BatchBase.BatchException('出力ディレクトリのファイル削除／作成中にエラーが発生しました。 {0}'.format(self.exception_info()))
        FileSystem.create_directory(self.work_dir)

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

        # リソースファイルのコピー
        self.copy_resource_files()

        # チャプターファイルの読み込み
        self.load_chapter_files()

        # OEPBSコンテンツ作成
        self.create_oebps_contents()

        # opfファイル作成
        self.create_oebps_book_opf()

        # epubファイル作成
        self.create_epub()

    def set_chapter_index_in_contents(self):
        '''
        コンテンツを考慮したチャプターのインデックスをセット
        '''
        self.contents_bind_chapter_indexes = {}

        if 'contents' in self.settings:
            if type(self.settings['contents']) is list:
                content_count = 0
                for content in self.settings['contents']:

                    create_by_chapters_count = False
                    if 'createByChaptersCount' in content:
                        create_by_chapters_count = content['createByChaptersCount']
                    use_chapters = []
                    if 'useChapters' in content:
                        if type(content['useChapters']) == list:
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

        # 設定ファイル読み込み
        if not FileSystem.exists_file(self.args.input_setting_file):
            raise BatchBase.BatchException('設定ファイルが見つかりません。 {0}'.format(self.exception_info()))
        try:
            with open(self.args.input_setting_file, 'r', encoding='utf-8') as f:
                self.settings = yaml.load(f)
        except Exception as e:
            raise BatchBase.BatchException('設定ファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.info_log('設定ファイル読み込み')

        self.setting_yaml_dirpath = os.path.dirname(self.args.input_setting_file)

        # コンテンツを考慮したチャプターのインデックスをセット
        self.set_chapter_index_in_contents()

        # 設定ファイル中のファイルパスに相対パスが設定されている場合、setting.yamlのあるディレクトリからのパスに設定しなおす
        self.reclusive_setting_callback(self.settings, self.convert_absolute_filepath)

        # リソースは相対パスを設定データに追加する
        if 'styleSheets' in self.settings['resources']:
            if type(self.settings['resources']['styleSheets']) is list:
                for stylesheet in self.settings['resources']['styleSheets']:
                    stylesheet['absoluteFilePath'] = stylesheet['filePath']
                    stylesheet['filePath'] = './resources/' + os.path.basename(stylesheet['absoluteFilePath'])
        if 'images' in self.settings['resources']:
            if type(self.settings['resources']['images']) is list:
                for image in self.settings['resources']['images']:
                    image['absoluteFilePath'] = image['filePath']
                    image['filePath'] = './resources/' + os.path.basename(image['absoluteFilePath'])

        # チャプターはxhtmlの相対ファイルパスを設定データに追加する
        if 'chapters' in self.settings['resources']:
            if 'files' in self.settings['resources']['chapters']:
                if type(self.settings['resources']['chapters']['files']) is list:
                    chapter_count = 0
                    for chapter in self.settings['resources']['chapters']['files']:
                        chapter_count += 1
                        if chapter_count in self.contents_bind_chapter_indexes:
                            chapter['absoluteFilePath'] = chapter['filePath']
                            chapter['filePath'] = './' + 'contents_{0}.xhtml'.format(self.contents_bind_chapter_indexes[chapter_count])

        # 設定ファイルの内容を一次元配列で持つ
        self.convert_yaml_to_list('setting', self.settings, self.replaces)
        for key in self.replaces:
            self.debug_log('{0} => {1}'.format(key, self.replaces[key]))

    def copy_resource_files(self):
        '''
        リソースファイルコピー（スタイルシート・画像のみ）
        '''
        # スタイルシート
        if 'styleSheets' in self.settings['resources']:
            if type(self.settings['resources']['styleSheets']) is list:
                for stylesheet in self.settings['resources']['styleSheets']:
                    if 'filePath' in stylesheet:
                        if not FileSystem.exists_file(stylesheet['absoluteFilePath']):
                            raise BatchBase.BatchException('指定されたファイルが見つかりません。 {0}'.format(stylesheet['absoluteFilePath']))
                        try:
                            FileSystem.copy_file(stylesheet['absoluteFilePath'], self.oebps_resources_dirpath)
                        except Exception as e:
                            raise BatchBase.BatchException('チャプターファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))
                        self.info_log('リソースファイルの読み込み - {0}'.format(stylesheet['absoluteFilePath']))
                        self.debug_log('リソースファイルのコピー - /OEBPS/resources/{0}'.format(os.path.basename(stylesheet['absoluteFilePath'])))

        # 画像
        if 'images' in self.settings['resources']:
            if type(self.settings['resources']['images']) is list:
                for image in self.settings['resources']['images']:
                    if 'filePath' in image:
                        if not FileSystem.exists_file(image['absoluteFilePath']):
                            raise BatchBase.BatchException('指定されたファイルが見つかりません。 {0}'.format(image['absoluteFilePath']))
                        try:
                            FileSystem.copy_file(image['absoluteFilePath'], self.oebps_resources_dirpath)
                        except Exception as e:
                            raise BatchBase.BatchException('リソースファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))
                        self.info_log('リソースファイルの読み込み - {0}'.format(image['absoluteFilePath']))
                        self.debug_log('リソースファイルのコピー - /OEBPS/resources/{0}'.format(os.path.basename(image['absoluteFilePath'])))

    def load_chapter_files(self):
        '''
        チャプターファイル読み込み
        '''
        chapter_count = 0
        if 'chapters' in self.settings['resources']:
            chapters_replaces = []
            if 'replaces' in self.settings['resources']['chapters']:
                if type(self.settings['resources']['chapters']['replaces']) == list:
                    chapters_replaces = self.settings['resources']['chapters']['replaces']
            if 'files' in self.settings['resources']['chapters']:
                if type(self.settings['resources']['chapters']['files']) == list:
                    for chapter in self.settings['resources']['chapters']['files']:
                        chapter_count += 1

                        if chapter_count in self.contents_bind_chapter_indexes:
                            filepath = ''
                            if 'filePath' in chapter:
                                filepath = chapter['absoluteFilePath']
                            if not FileSystem.exists_file(filepath):
                                raise BatchBase.BatchException('チャプターファイルが見つかりません。: {0}'.format(filepath))

                            title = ''
                            if 'title' in chapter:
                                title = chapter['title']

                            # 本文取得、置換
                            body = ''
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    lines = f.read().splitlines()
                                    for line in lines:
                                        line = line + '\n'
                                        if len(chapters_replaces) > 0:
                                            line = self.content_replace(line, chapters_replaces)
                                        if 'replaces' in chapter:
                                            line = self.content_replace(line, chapter['replaces'])
                                        line = self.content_replace_by_setting(line)
                                        body = body + line
                            except Exception as e:
                                raise BatchBase.BatchException('チャプターファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))

                            # チャプターデータを収集
                            self.chapters.append({
                                'title': title,
                                'body': body,
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
                                        'replaceContent': os.path.join(self.oebps_dirpath, 'contents_{0}.xhtml'.format(self.contents_bind_chapter_indexes[chapter_count]))
                                    },
                                ]
                            })

                            self.info_log('リソースファイルの読み込み - {0}'.format(filepath))

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

        self.debug_log('ファイル作成 - /mimetype')

    def create_meta_inf(self):
        '''
        ディレクトリ作成 - /META-INF
        '''

        self.meta_inf_dirpath = os.path.join(self.work_dir, 'META-INF')

        if FileSystem.exists_file(self.meta_inf_dirpath):
            FileSystem.remove_directory(self.meta_inf_dirpath)

        FileSystem.create_directory(self.meta_inf_dirpath)

        self.debug_log('ディレクトリ作成 - /META-INF')

    def create_meta_inf_container_xml(self):
        '''
        ファイル作成 - /META-INF/container.xml
        '''

        container_xml_filepath = os.path.join(self.meta_inf_dirpath, 'container.xml')

        if FileSystem.exists_file(container_xml_filepath):
            FileSystem.remove_file(container_xml_filepath)

        data = '''
<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
	<rootfiles>
		<rootfile full-path="OEBPS/book.opf" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>
'''
        try:
            with open(container_xml_filepath, 'w', encoding='utf-8') as f:
                f.write(Convert.get_pretty_xml(data))
        except Exception as e:
            raise BatchBase.BatchException('/META-INF/container.xmlファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.debug_log('ファイル作成 - /META-INF/container.xml')

    def create_oebps(self):
        '''
        ディレクトリ作成 - /OEBPS
        '''

        self.oebps_dirpath = os.path.join(self.work_dir, 'OEBPS')

        if FileSystem.exists_file(self.oebps_dirpath):
            FileSystem.remove_directory(self.oebps_dirpath)

        FileSystem.create_directory(self.oebps_dirpath)

        self.debug_log('ディレクトリ作成 - /OEBPS')

    def create_oebps_resources(self):
        '''
        ディレクトリ作成 - /META-INF/resources
        '''

        self.oebps_resources_dirpath = os.path.join(
            self.oebps_dirpath, 'resources')

        if FileSystem.exists_file(self.oebps_resources_dirpath):
            FileSystem.remove_directory(self.oebps_resources_dirpath)

        FileSystem.create_directory(self.oebps_resources_dirpath)

        self.debug_log('ディレクトリ作成 - /META-INF/resources')

    def create_oebps_contents(self):
        '''
        コンテンツ作成
        '''
        if 'contents' in self.settings:
            if type(self.settings['contents']) is list:
                self.contents = []
                content_count = 0
                for content in self.settings['contents']:
                    filepath = ''
                    if 'filePath' in content:
                        filepath = content['filePath']
                    create_by_chapters_count = False
                    if 'createByChaptersCount' in content:
                        create_by_chapters_count = content['createByChaptersCount']
                    replaces = []
                    if 'replaces' in content:
                        if type(content['replaces']) == list:
                            replaces = content['replaces']
                    use_chapters = []
                    if 'useChapters' in content:
                        if type(content['useChapters']) == list:
                            use_chapters = content['useChapters']

                    # コンテンツ内データ置換
                    if not FileSystem.exists_file(filepath):
                        raise BatchBase.BatchException(
                            'コンテンツファイルが見つかりません。: {0}'.format(filepath))

                    if create_by_chapters_count and len(use_chapters) > 0:
                        # チャプター分のコンテンツファイル作成
                        for use_chapter in use_chapters:
                            content_count += 1

                            content_data = ''
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    content_data = f.read()
                            except Exception as e:
                                raise BatchBase.BatchException('コンテンツファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))

                            chapter_index = int(use_chapter['chapterIndex'])
                            content_data = self.content_replace(content_data, self.chapters[chapter_index - 1]['replaces'])

                            if 'replaces' in content:
                                content_data = self.content_replace(content_data, content['replaces'])
                            content_data = self.content_replace_by_setting(content_data)

                            oebps_xhtml_filepath = os.path.join(self.oebps_dirpath, 'contents_{0}.xhtml'.format(content_count))
                            try:
                                with open(oebps_xhtml_filepath, 'w', encoding='utf-8') as f:
                                    f.write(content_data)
                            except Exception as e:
                                raise BatchBase.BatchException('コンテンツファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

                            self.contents.append({
                                'filePath': './{0}'.format(os.path.basename(oebps_xhtml_filepath)),
                                'isNavigationContent': content['isNavigationContent'],
                            })

                            self.debug_log('ファイル作成 - /OEBPS/{0}'.format(os.path.basename(oebps_xhtml_filepath)))
                    else:
                        # 単一のコンテンツファイル作成
                        content_count += 1

                        content_data = ''
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content_data = f.read()
                        except Exception as e:
                            raise BatchBase.BatchException('コンテンツファイル読み込み中にエラーが発生しました。 {0}'.format(self.exception_info()))

                        if 'replaces' in content:
                            content_data = self.content_replace(content_data, content['replaces'])
                        content_data = self.content_replace_by_setting(content_data)

                        oebps_xhtml_filepath = os.path.join(self.oebps_dirpath, 'contents_{0}.xhtml'.format(content_count))
                        try:
                            with open(oebps_xhtml_filepath, 'w', encoding='utf-8') as f:
                                f.write(content_data)
                        except Exception as e:
                            raise BatchBase.BatchException('コンテンツファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

                        self.contents.append({
                            'filePath': './{0}'.format(os.path.basename(oebps_xhtml_filepath)),
                            'isNavigationContent': content['isNavigationContent'],
                        })

                        self.debug_log('ファイル作成 - /OEBPS/{0}'.format(os.path.basename(oebps_xhtml_filepath)))

    def create_oebps_book_opf(self):
        '''
        ファイル作成 - /OEBPS/book.opf
        '''

        replace_hash = self.settings

        # UUIDがない場合は作成
        if replace_hash['bookId'] == '':
            replace_hash['bookId'] = uuid4()

        # その他著者を作成
        other_authors = []
        other_author_count = 0
        if 'otherAuthors' in replace_hash and replace_hash['otherAuthors'] != None:
            for other_author in replace_hash['otherAuthors']:
                other_author_count += 1
                other_author['otherAuthorCount'] = str(other_author_count)
                author = '''
		<!-- Other authors -->
		<dc:creator id="creator{otherAuthorCount}">{authorName}</dc:creator>
		<meta refines="#creator{otherAuthorCount}" property="role" scheme="marc:relators" id="role">{authorRole}</meta>
                '''
                author = self.content_replace(author, [
                    {'type': 'simple', 'placeHolder': '{otherAuthorCount}', 'replaceContent': str(other_author_count), },
                    {'type': 'simple', 'placeHolder': '{authorName}', 'replaceContent': other_author['authorName'], },
                    {'type': 'simple', 'placeHolder': '{authorRole}', 'replaceContent': other_author['authorRole'], },
                ])
                author = self.content_replace_by_setting(author)
                other_authors.append(author)
        replace_hash['{otherAuthors}'] = ''
        if other_author_count > 0:
            replace_hash['{otherAuthors}'] = '\n'.join(other_authors)

        manifests = []
        spines = []

        stylesheet_count = 0
        for stylesheet in self.settings['resources']['styleSheets']:
            stylesheet_count += 1
            manifests.append('<item id="css_{0}" href="{1}" media-type="{2}" />'.format(stylesheet_count, stylesheet['filePath'], mimetypes.guess_type(stylesheet['filePath'])[0]))

        image_count = 0
        for image in self.settings['resources']['images']:
            image_count += 1
            properties = ''
            if image['isCover']:
                properties = 'properties="cover-image"'
            manifests.append('<item id="image_{0}" href="{1}" media-type="{2}" {3} />'.format(image_count, image['filePath'], mimetypes.guess_type(image['filePath'])[0], properties))

        content_count = 0
        for content in self.contents:
            content_count += 1

            properties = ''
            if content['isNavigationContent']:
                properties = 'properties="nav"'

            manifests.append('<item id="content_{0}" href="{1}" media-type="{2}" {3} />'.format(content_count, content['filePath'], mimetypes.guess_type(content['filePath'])[0], properties))
            spines.append('<itemref idref="content_{0}" />'.format(content_count))

        replace_hash['{spines}'] = '\n'.join(spines)
        replace_hash['{manifests}'] = '\n'.join(manifests)

        oebps_book_opf_filepath = os.path.join(self.oebps_dirpath, 'book.opf')
        if FileSystem.exists_file(oebps_book_opf_filepath):
            FileSystem.remove_file(oebps_book_opf_filepath)

        # book.opfファイル作成
        book_opf_data = '''
<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="3.0" xml:lang="ja">
	<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
		<!-- BookID -->
		<dc:identifier id="BookID">urn:uuid:{$setting.bookId}</dc:identifier>
		<meta property="dcterms:identifier" id="uuid">urn:uuid:{$setting.bookId}</meta>
		<!-- Language -->
		<dc:language>{$setting.language}</dc:language>
		<meta property="dcterms:language" id="pub-lang">ja</meta>
		<!-- Modified -->
		<dc:date>{$setting.modified}</dc:date>
		<meta property="dcterms:modified">{$setting.modified}</meta>
		<!-- Title -->
		<dc:title>{$setting.title}</dc:title>
		<meta property="dcterms:title" id="dcterm-title">{$setting.title}</meta>
		<!-- Creator -->
		<dc:creator id="creatorMain">{$setting.authorName}</dc:creator>
		<meta refines="#creatorMain" property="role" scheme="marc:relators" id="roleMain">{$setting.authorRole}</meta>
        {otherAuthors}
		<!-- Rights -->
		<dc:rights>{$setting.authorCopyRight}</dc:rights>
		<meta property="dcterms:rights" id="rights">{$setting.authorCopyRight}</meta>
		<!-- Cover -->
		<meta name="cover" content="cover-image" />
	</metadata>
	<manifest>
        {manifests}
	</manifest>
	<spine page-progression-direction="{$setting.pageProgressionDirection}">
        {spines}
	</spine>
</package>
        '''
        book_opf_data = self.content_replace(book_opf_data, [
            {'type': 'simple', 'placeHolder': '{manifests}', 'replaceContent': replace_hash['{manifests}'], },
            {'type': 'simple', 'placeHolder': '{spines}', 'replaceContent': replace_hash['{spines}'], },
            {'type': 'simple', 'placeHolder': '{otherAuthors}', 'replaceContent': replace_hash['{otherAuthors}'], },
        ])
        book_opf_data = self.content_replace_by_setting(book_opf_data)
        book_opf_data = self.content_replace_by_setting(book_opf_data)

        try:
            with open(oebps_book_opf_filepath, 'w', encoding='utf-8') as f:
                f.write(Convert.get_pretty_xml(book_opf_data))
        except Exception as e:
            raise BatchBase.BatchException('/OEBPS/book.opfファイル作成中にエラーが発生しました。 {0}'.format(self.exception_info()))

        self.debug_log('ファイル作成 - /OEBPS/book.opf')

    def create_epub(self):
        '''
        epubファイル作成
        '''

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

        # 一時ファイルディレクトリを削除
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

    def reclusive_setting_callback(self, data, callback):
        if type(data) == list:
            for value in data:
                self.reclusive_setting_callback(value, callback)
        elif type(data) == dict:
            for key in data:
                if not type(data[key]) == list and not type(data[key]) == dict:
                    data[key] = callback(key, data[key])
                self.reclusive_setting_callback(data[key], callback)

    def convert_absolute_filepath(self, key, value):
        if key == 'filePath' and type(value) == str and value != '':
            if len(value) > 2 and (value[:2] == './' or value[:2] == '.\\'):
                return re.sub('^\.', re.sub(r'\\', r'\\\\', self.setting_yaml_dirpath), value)
        else:
            return value

    def content_replace(self, content, replaces):
        '''
        コンテンツ置換
        '''

        simple_replaces = []
        regex_replaces = []

        for replace in replaces:
            if 'type' in replace:
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
            if type(source[key]) == dict:
                self.convert_yaml_to_list(parent_data + '.' + key, source[key], dest)
            elif type(source[key]) == list:
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
    exit(Batch().execute())
