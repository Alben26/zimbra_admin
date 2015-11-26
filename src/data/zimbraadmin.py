# -*- coding: utf-8 -*-

from pythonzimbra.tools import auth
from pythonzimbra.request_xml import RequestXml
from pythonzimbra.response_xml import ResponseXml
from pythonzimbra.communication import Communication
from flask_login import current_user
from pythonzimbra.response_json import ResponseJson
from pythonzimbra.request_json import RequestJson
#import argparse
#import ConfigParser
import time
from ..settings import app_config

class ZimbraManager:

    def __init__(self, *args, **kwargs):
        self.admin = kwargs.get('admin')
        self.password = kwargs.get('password')
        self.url = kwargs.get('url')


    def getToken(self):
        return auth.authenticate(
            self.url,
            self.admin,
            self.password,
            admin_auth=True
        )
    def getTokenUser(self,**kwargs):
        return auth.authenticate(
            self.url,
            #"http://mail.iservery.cz:81/service/soap",
            kwargs.get('user'),
            kwargs.get('password'),
            admin_auth=False,
            use_password=True
        )

    def request(self, name, data, urn):

        comm = Communication(self.url)
        account_request = RequestXml()
        account_request.set_auth_token(self.getToken())
        account_request.add_request(name, data, urn)
        account_response = ResponseXml()
        comm.send_request(account_request, account_response)
        return account_response.get_response()

    def createAccount(self, *args, **kwargs):
        attr = []
        if kwargs.get('quota'):
            attr.append(
                {'_content': kwargs.get('quota') * 1024 * 1024, u'n': u'zimbraMailQuota'})
        if kwargs.get('displayname'):
            attr.append(
                {'_content': kwargs.get('displayname'), u'n': u'displayName'})
        if kwargs.get('status'):
            attr.append(
                {'_content': kwargs.get('status'), 'n': 'zimbraAccountStatus'})
                
        response = self.request(
            'CreateAccountRequest',
            {
                "name": kwargs.get('name'),
                "password": kwargs.get('password'),
                "a": attr
            },
            "urn:zimbraAdmin"
        )
        if 'CreateAccountResponse' in response:
            return True

        return response

#    def AuthUser(self,url,account,key, **kwargs):




    def deleteAccount(self, *args, **kwargs):
        accountinfo = self.getAccount(*args, **kwargs)
        if 'GetAccountResponse' in accountinfo:
            response = self.request(
                'DeleteAccountRequest',
                {
                    "id": accountinfo['GetAccountResponse']['account']['id'],
                },
                "urn:zimbraAdmin"
            )
            if 'DeleteAccountResponse' in response:
                return True
            return response
        else:
            return accountinfo
 
    def getAccount(self, *args, **kwargs):
        response = self.request(
            'GetAccountRequest',
            {
                "account": {
                    'by': 'id',
                    '_content': kwargs.get('id')
                },
            },
            "urn:zimbraAdmin"
        )
        return response

    def setPassword(self, *args, **kwargs):
        #accountinfo = self.getAccount(*args, **kwargs)
        #if 'GetAccountResponse' in accountinfo:
            response = self.request(
                'SetPasswordRequest',
                {
                    "id": kwargs.get('id'), #accountinfo['GetAccountResponse']['account']['id'],
                    "newPassword": kwargs.get('password')
                },
                "urn:zimbraAdmin"
            )
            if 'SetPasswordResponse' in response:
                return True
            return response
        #else:
         #   return accountinfo


    def getAllAccount(self, *args, **kwargs):
        response = self.request(
            'GetAllAccountsRequest',
            {
            },
            "urn:zimbraAdmin"
        )
        if 'GetAllAccountsResponse' in response:
            account_list = []
            keyfilter = lambda k,l: map(lambda x: x['_content'],filter(lambda x: x['n'] == k,l))
            keyvalue = lambda v: v[0] if v else ''
            for a in response['GetAllAccountsResponse']['account']:
                account_list.append((a['id'],
                                     a['name'],
                                     keyvalue(keyfilter('displayName',a['a'])),
                                     keyvalue(keyfilter('zimbraMailQuota',a['a'])),
                                     keyvalue(keyfilter('zimbraAccountStatus',a['a']))))
            return account_list
        else:
            return response



    def modifyAccount(self, *args, **kwargs):
        attr = []
        accountinfo = self.getAccount(*args, **kwargs)
        if 'GetAccountResponse' in accountinfo:

            if kwargs.get('quota'):
                attr.append(
                    {'_content': kwargs.get('quota') * 1024 * 1024, 'n': 'zimbraMailQuota'})
            if kwargs.get('displayname'):
                attr.append(
                    {'_content': kwargs.get('displayname'), 'n': 'displayName'})
            if kwargs.get('status'):
                attr.append(
                    {'_content': kwargs.get('status'), 'n': 'zimbraAccountStatus'})

            response = self.request(
                'ModifyAccountRequest',
                {
                    "id": accountinfo['GetAccountResponse']['account']['id'],
                     "a": attr
                },
                "urn:zimbraAdmin"
            )
            if 'ModifyAccountResponse' in response:
                return True
            else:
                return response
        else:
            return accountinfo


    def addAccountAlias(self,*args,**kwargs):


            response = self.request(
                'AddAccountAliasRequest',
                {
                    "id": kwargs.get('id'),
                     "alias": kwargs.get('alias')
                },
                "urn:zimbraAdmin"
            )

            if 'AddAccountAliasResponse' in response:
                return True
            return response


    def removeAccountAlias(self,*args,**kwargs):

        accountinfo = self.getAccount(*args, **kwargs)
        if 'GetAccountResponse' in accountinfo:

            response = self.request(
                'RemoveAccountAliasRequest',
                {
                    "id": accountinfo['GetAccountResponse']['account']['id'],
                     "alias": kwargs.get('alias')
                },
                "urn:zimbraAdmin"
            )

            if 'RemoveAccountAliasResponse' in response:
                return True
            return response 
        else:
            return accountinfo

    def createDomain(self, *args, **kwargs):
        response = self.request(
            'CreateDomainRequest',
            {
                "name": kwargs.get('name'),
            },
            "urn:zimbraAdmin"
        )
        if 'CreateDomainResponse' in response:
            return True
        return response


    def getDomain(self, *args, **kwargs):
        response = self.request(
            'GetDomainRequest',
            {
                "domain": {
                    'by': 'id',
                    '_content': kwargs.get('id')
                },
            },
            "urn:zimbraAdmin"
        )
        return response


    def deleteDomain(self, *args, **kwargs):
        domaininfo = self.getDomain(*args, **kwargs)
        if 'GetDomainResponse' in domaininfo:
            response = self.request(
                'DeleteDomainRequest',
                {
                    "id": domaininfo['GetDomainResponse']['domain']['id'],
                },
                "urn:zimbraAdmin"
            )
            if 'DeleteDomainResponse' in response:
                return True
            return response
        else:
            return domaininfo


    def getAllDomain(self,*args,**kwargs):

        response = self.request(
            'GetAllDomainsRequest',
            {
            },
            "urn:zimbraAdmin"
        )
        if 'GetAllDomainsResponse' in response:
            return [ (i['id'],i['name']) for i in response['GetAllDomainsResponse']['domain'] ]
        else:
            return response

    def getQuotaUsage(self, *args, **kwargs):
        if not current_user.email.split("@")[1] == "sspu-opava.local":
           response = self.request(

               'GetQuotaUsageRequest',
               {

                       "domain": kwargs.get('domain')
               },
               "urn:zimbraAdmin"


           )
        else:
            response = self.request(

                   'GetQuotaUsageRequest',
                   {

                           "allServers": kwargs.get('allServers')
                   },
                   "urn:zimbraAdmin"


            )
        return response

    def countAccount(self, *args, **kwargs):
           response = self.request(
               'CountAccountRequest',
               {
                    "domain": {
                    'by': 'name',
                    '_content': kwargs.get('name')
                    }
               },
               "urn:zimbraAdmin"
           )
           return response

#zm=ZimbraManager(url=app_config.ZIMBRA_URL,admin=app_config.ZIMBRA_ADMIN,password=app_config.ZIMBRA_ADMIN_PASSWORD)
zm=ZimbraManager(url="https://192.168.22.110:7071/service/admin/soap",admin="admin",password="Zimbra2015")