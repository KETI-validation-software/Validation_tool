import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import ssl
import json
import cgi

import time
import traceback

from spec.video.videoRequest import videoMessages, videoOutMessage, videoInMessage
from spec.video.videoSchema import videoInSchema, videoOutSchema
from spec.bio.bioRequest import bioMessages, bioOutMessage, bioInMessage
from spec.bio.bioSchema import  bioInSchema, bioOutSchema
from spec.security.securityRequest import securityMessages, securityOutMessage, securityInMessage
from spec.security.securitySchema import securityInSchema, securityOutSchema

from core.functions import resource_path
from requests.auth import HTTPDigestAuth
from config.CONSTANTS import none_request_message


class Server(BaseHTTPRequestHandler):

    message = None
    inMessage = None
    outMessage = None
    inSchema = None
    outSchema = None
    system = ""
    auth_type = "D"
    auth_Info = ['admin', '1234', 'user', 'abcd1234', 'SHA-256', None]
    digest_res = ""
    transProtocolInput = ""

    url_tmp = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = ""
        self.webhook_flag = False


    def _set_headers(self):
        self.send_response(200, None)
        self.send_header('Content-type', 'application/json')
        self.send_header('User-Agent', 'test')
        self.end_headers()

    def _set_digest_headers(self):
        auth = HTTPDigestAuth(self.auth_Info[0], self.auth_Info[1])
        auth.init_per_thread_state()
        auth._thread_local.chal = {'realm': self.auth_Info[2], 'nonce': self.auth_Info[3],
                                   'algorithm': self.auth_Info[4]}
        auth._thread_local.chal['qop'] = None  # 'auth'
        auth._thread_local.chal['opaque'] = 'abcd1234'
        auth_opaque = auth._thread_local.chal.get("opaque")
        self.send_response(401, None)
        self.send_header('Content-type', 'application/json')
        self.send_header('User-Agent', 'test')
        digest_temp = auth.build_digest_header('POST', self.path)
        temp = []
        digest_temp = digest_temp.split(" ")
        for i in digest_temp:
            temp.append(i.split("="))
        for i in temp:
            if i[0] == "response":
                self.auth_Info[-1] = i[1].replace('"', '').replace(',', '')
        if auth_opaque is not None:
            digest_header = 'Digest' + ' ' + 'realm="' + self.auth_Info[2] + '",' + ' ' + 'nonce="' + \
                            self.auth_Info[3] + '",' + ' ' + 'opaque="' + auth_opaque + '",' + 'algorithm="' + \
                            self.auth_Info[4] + '"'

        else:
            digest_header = 'Digest' + ' ' + 'realm="' + self.auth_Info[2] + '",' + ' ' + 'nonce="' + \
                            self.auth_Info[3] + '",' + ' ' + 'algorithm="' + self.auth_Info[4] + '"'

        self.send_header('WWW-Authenticate', digest_header)
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        res_data = json.dumps({'hello': 'world', 'received': 'ok'})
        self._set_headers()
        self.wfile.write(res_data)

    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get_content_type())
        auth = self.headers.get('Authorization')
        auth_pass = False
        message_cnt, data = self.api_res()

        if self.auth_type == "None":
            auth_pass = True
        else:
            try:
                if self.path == "/" + self.message[0]:
                    auth_pass = True
                elif self.auth_type == "B":
                    auth = auth.split(" ")
                    if auth[0] == 'Bearer':  # self.auth_type == "B" and  auth[0] == 'Bearer'
                        token = auth[1].replace('"', "")

                        if token == self.auth_Info[0]:
                            auth_pass = True
                elif self.auth_type == "D":
                    try:
                        auth = auth.split(" ")
                        if auth[0] == 'Digest':
                            temp = []
                            for i in auth:
                                temp.append(i.split("="))
                            auth_res = ""
                            for i in temp:
                                if i[0] == "response":
                                    auth_res = i[1].replace('"', '').replace(',', '')
                            if auth_res == self.auth_Info[-1]:
                                auth_pass = True
                    except Exception as e:
                        #print(e)
                        #print(traceback.format_exc())
                        self._set_digest_headers()
                        return
            except Exception as err:
                # err_msg = traceback.format_exc()
                print(err)
                #print(traceback.format_exc())
                return
        post_data = '{}'
        try:
            content_len = int(self.headers.get('Content-Length'))
            if content_len != 0:
                post_data = self.rfile.read(content_len)  # <--- Gets the data itself
        except:
            post_data = '{}'
        dict_data = json.loads(post_data)  # type(dict_data)는 <class 'dict'>

        with open(resource_path("json0627/"+self.system + "/" + self.path[1:]+".json"), "w", encoding="UTF-8") \
                as out_file:
            json.dump(dict_data, out_file, ensure_ascii=False)
        # with open(self.path[1:]+".json","r", encoding="UTF-8") as out_file:
        #    datas = json.load(out_file)

        #  refuse to receive non-json content
        if ctype == 'text/plain':
            for i in none_request_message:
                if self.path == "/" + i:
                    pass
                # else
        elif ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        self.webhook_flag = False
        message = ""
        url_tmp = ""
        if "Realtime".lower() in self.message[message_cnt].lower():
            trans_protocol = dict_data.get("transProtocol", {})
            if trans_protocol:  # webhook 또는 LongPolloing 일 경우
                trans_protocol_type = trans_protocol.get("transProtocolType", {})
                if "WebHook".lower() in trans_protocol_type.lower():
                    try:
                        url_tmp = dict_data["transProtocol"]["transProtocolDesc"]
                        message = self.outMessage[-1]
                        self.webhook_flag = True

                        if "https".lower() not in url_tmp.lower():
                            message = {
                            "code": "400",
                            "message": "잘못된 요청"
                        }
                        if "longpolling" in str(self.transProtocolInput).lower():
                            # webhook 요청 받았는데 뷰어에서 longpolling 선택한 경우
                            message = {
                                "code": "400",
                                "message": "잘못된 요청"
                            }


                    except:  # webhook인데 desc 없는 경우
                        message = {
                            "code": "400",
                            "message": "잘못된 요청"
                        }

                else:
                    # LongPolloing 인 경우
                    if auth_pass:
                        message = data
                        if "webhook".lower() in str(self.transProtocolInput).lower():
                            message = {
                                "code": "400",
                                "message": "잘못된 요청"
                            }

                    else:
                        message = {
                            "code": "401",
                            "message": "인증 오류"
                        }
            else:
                # webhook, LongPolloing 둘다 아닌 경우
                message = {
                    "code": "400",
                    "message": "잘못된 요청"
                }
        else:  # Realtime 메시지아니면서 Webhook 요청 없는 메시지
            if auth_pass:
                message = data
            else:
                message = {
                    "code": "401",
                    "message": "인증 오류"
                }
        # send the message back
        a = json.dumps(message).encode('utf-8')

        self._set_headers()
        self.wfile.write(a)

        if self.webhook_flag:
            json_data_tmp = json.dumps(data).encode('utf-8')
            if "longpolling" in str(self.transProtocolInput).lower():
                # webhook 요청 받았는데 뷰어에서 longpolling 선택한 경우
                data = {
                    "code": "400",
                    "message": "잘못된 요청"
                }
                json_data_tmp = json.dumps(data).encode('utf-8')
            webhook_thread = threading.Thread(target=self.webhook_req, args=(url_tmp, json_data_tmp, 5))
            webhook_thread.start()

        #print("통플검증sw이 보낸 메시지", a)

    def webhook_req(self, url, json_data_tmp, max_retries=3):
        import requests
        for attempt in range(max_retries):

            try:
                result = requests.post(url, data=json_data_tmp, verify=False)
                #print("webhook response", result.text)
                self.result = result
                with open(resource_path("json0627/" + self.system + "/" + "webhook_" + self.path[1:] + ".json"),
                          "w", encoding="UTF-8") as out_file2:
                    json.dump(json.loads(str(self.result.text)), out_file2, ensure_ascii=False)
                break
                #  self.res.emit(str(self.result.text))
            #except requests.ConnectionError:
            #    print("..")
            #    time.sleep(1)
            except Exception as e:
                print(e)
                #print(traceback.format_exc())
                #  self.res.emit(str("err from WebhookRequest"))

    def api_res(self):
        i, data = None, None
        for i in range(0, len(self.message)):
            data = ""
            if self.path == "/" + self.message[i]:
                data = self.outMessage[i]
                if i == 0 and self.auth_type == "B":
                    try:
                        self.auth_Info = data['accessToken']
                    except:
                        pass
                break
        return i, data


# 확인용
def run(server_class=HTTPServer, handler_class=Server, address='127.0.0.3', port=8008, system="video"):
    server_address = (address, port)

    if system == "video":
        Server.message = videoMessages
        Server.inMessage = videoInMessage
        Server.outMessage = videoOutMessage
        Server.inSchema = videoInSchema
        Server.outSchema = videoOutSchema

    elif system == "bio":
        Server.message = bioMessages
        Server.inMessage = bioInMessage
        Server.outMessage = bioOutMessage
        Server.inSchema = bioInSchema
        Server.outSchema = bioOutSchema

    elif system == "security":
        Server.message = securityMessages
        Server.inMessage = securityInMessage
        Server.outMessage = securityOutMessage
        Server.inSchema = securityInSchema
        Server.outSchema = securityOutSchema

    certificate_private = resource_path('key0627/server.crt')
    certificate_key = resource_path('key0627/server.key')
    httpd = server_class(server_address, handler_class)
    httpd.socket = ssl.wrap_socket(httpd.socket,  certfile=certificate_private,
                                   keyfile=certificate_key, server_side=True)
    print('Starting https on port %d...' % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
