# -*- encoding:utf-8 -*-
import yaml
import requests
from datetime import datetime
try:
    from urllib.parse import quote
except:
    from urllib import quote
import hmac
import hashlib
import base64
import json


class NiftyCloudRequest(object):
    ''' ニフティクラウド mobile backendのREST APIへのリクエスト用モジュール
    APPLICATION_KEYとCLIENT_KEYはyamlファイルとして
    ```
    APPLICATION_KEY: "app_key"
    CLIENT_KEY: "client_key"
    ```
    と書く
    defaultでは~/.nifty.ymlを読み込む
    '''
    API_PROTOCOL = 'https'
    API_DOMAIN = 'mbaas.api.nifcloud.com'
    API_VERSION = '2013-09-01'
    CHARSET = 'UTF-8'
    SIGNATURE_METHOD = 'HmacSHA256'
    SIGNATURE_VERSION = '2'

    def __init__(self, config_file='~/.nifty.yml'):
        ''' KEYの設定
        Args:
            config_file: APPLICATION_KEYとCLIENT_KEYを書いたyamlファイル
        '''
        config = yaml.load(open(config_file, 'r').read())
        self.APP_KEY = config['APPLICATION_KEY']
        self.CLIENT_KEY = config['CLIENT_KEY']

    def get(self, path, query, **kwargs):
        ''' getのalias
        requestを参照
        '''
        return self.request(path, query, 'GET', **kwargs)

    def post(self, path, query, **kwargs):
        ''' postのalias
        requestを参照
        '''
        return self.request(path, query, 'POST', **kwargs)

    def put(self, path, query, **kwargs):
        ''' putのalias
        requestを参照
        '''
        return self.request(path, query, 'PUT', **kwargs)

    def delete(self, path, query, **kwargs):
        ''' deleteのalias
        requestを参照
        '''
        return self.request(path, query, 'DELETE', **kwargs)

    def request(self, path, query, method, **kwargs):
        ''' niftyのmbaasにrequestを送る
        Reference:
            http://mb.cloud.nifty.com/doc/rest/common/format.html
        Args:
            path: 叩くAPIのpath(eg. /classes/TestClass)
            query: 辞書形式のクエリ(eg. {'where': {'key': 'value'}})
            method: 'get' or 'post'
            kwargs: requests.request に追加で渡すパラメータ
        Return:
            response: requestに対するresponse
        '''
        assert type(query) is dict
        method = method.upper()
        # request用のシグネチャ作成
        signature = self.__make_signature(path=path, query=query, method=method)
        # 必要なヘッダを作成
        headers = self.__make_headers(signature)
        # pathからurlを作成する
        url = self.__make_url(path)
        kwargs['headers'] = headers
        if method.upper() == 'GET':
            # getの時はURLパラメータにqueryを足す
            url += '?' + self.__query(query)
        else:
            # get以外ならbodyにqueryを入れる
            kwargs['data'] = json.dumps(query)
        response = requests.request(method, url, **kwargs)
        return response

    def __make_headers(self, signature):
        ''' ヘッダ作成
        '''
        # 先にシグネチャを作ればself._timestamp()でセットされている
        assert self.timestamp is not None
        return {
            # 'X-NCMB-Apps-Session-Token': '',
            'X-NCMB-Application-Key': self.APP_KEY,
            'X-NCMB-Signature': signature,
            'X-NCMB-Timestamp': self.timestamp,
            'Content-Type': 'application/json',
        }

    def __timestamp(self):
        ''' iso8601形式のtimestampを作成する
        '''
        self.timestamp = datetime.utcnow().isoformat()
        return self.timestamp

    def __make_url(self, path):
        ''' pathを使ってurlを構成する
        '''
        return '{protocol}://{domain}/{version}{path}'.format(
            protocol=self.API_PROTOCOL, domain=self.API_DOMAIN,
            version=self.API_VERSION, path=path)

    def __path(self, path):
        ''' ヘッダで必要なpathの形式にする
        '''
        return '/{api_version}{path}'\
                .format(api_version=self.API_VERSION, path=path)

    def __query(self, dict_query):
        ''' 辞書形式のqueryをシグネチャ作成に必要な形に変換する
        urlエンコードしたkey=valueを&でつなぐ
        '''
        encoded_query = self.__encode_query(dict_query)
        return self.__join_query(encoded_query)

    def __join_query(self, encoded_dict_query):
        ''' key=valueにして&でつなぐ
        シグネチャ生成で使うためsortしておく
        '''
        return '&'.join(
            '='.join(e) for e in sorted(encoded_dict_query.items())
        )

    def __encode_query(self, dict_query):
        ''' 辞書をurlエンコードする
        valueがdictの場合はjson文字列に変換してから行う
        '''
        q = lambda x: quote(str(x))
        qj = lambda x: q(json.dumps(x).replace(': ', ':'))
        result = {}
        for k, v in dict_query.items():
            if type(v) is dict:
                # json文字列に変換
                result[q(k)] = qj(v)
            else:
                result[q(k)] = q(v)
        return result

    def __make_signature_str(self, path, query, method='GET'):
        ''' niftyのAPIへrequest送る時に必要なシグネチャの元となる
        文字列を生成する
        Args:
            path: データの保存場所へのpath
            query: 問い合わせ内容のdict
            method: 'GET'とか'POST'
        Return:
            シグネチャ生成元となるstr型
        '''
        # listで順番を保持する
        signature_list = [
            method, self.API_DOMAIN, self.__path(path)
        ]
        # 後でsortするためにdict
        signature_dict = {
            'SignatureMethod': self.SIGNATURE_METHOD,
            'SignatureVersion': self.SIGNATURE_VERSION,
            'X-NCMB-Application-Key': self.APP_KEY,
            'X-NCMB-Timestamp': self.__timestamp(),
        }
        # keyでsortしなければならない
        signature_list.append(
            '&'.join(['='.join(_sd) for _sd in sorted(signature_dict.items())])
        )
        # getの時はurlパラメータ情報も付け足す
        if query and method == 'GET':
            signature_list[-1] += '&' + self.__query(query).strip()

        return '\n'.join(signature_list).strip()

    def __encode_signature(self, signature_str):
        ''' HmacSHA256アルゴリズムでハッシュ文字列を生成する
        秘密鍵としてCLIENT_KEYを使用する
        Args:
            signature_str: シグネチャ用の文字列
        Return:
            bytes型のシグネチャ
        '''
        return base64.b64encode(
            hmac.new(
                self.CLIENT_KEY.encode(self.CHARSET),
                signature_str.encode(self.CHARSET), hashlib.sha256).digest())

    def __make_signature(self, path, query, method):
        ''' requestする情報を使って認証用のシグネチャを作成する
        '''
        signature_str = self.__make_signature_str(path, query, method)
        signature = self.__encode_signature(signature_str)
        return signature.decode(self.CHARSET)
