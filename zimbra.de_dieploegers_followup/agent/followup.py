"""

Agent running periodically on a server with installed python-zimbra libs,
that looks on the server for emails, that have reached their followup time,
moves them to the inbox and tags them.

"""

import logging
from optparse import OptionParser
import re
from datetime import datetime

from pythonzimbra.tools import auth
from pythonzimbra.communication import Communication

ZIMBRA_INBOX_ID = 2

if __name__ == "__main__":

    # Interpret arguments

    parser = OptionParser(
        usage="Usage: %prog [options] SERVER USERNAME PREAUTH",
        description="SERVER: Name/IP of Zimbra-Server, "
                    + "USERNAME: Administrative account username, "
                    + "PASSWORD: Password of administrative account"
    )

    parser.add_option(
        "-l",
        "--distlist",
        dest="distlist",
        help="Use members of this distribution list instead of all users"
    )

    parser.add_option(
        "-o",
        "--domain",
        dest="domain",
        help="Use members from this domain instead of all users"
    )

    parser.add_option(
        "-q",
        "--quiet",
        action="store_true",
        dest="quiet",
        help="Be quiet doing things.",
    )

    parser.add_option(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        help="Enable debug logging"
    )

    (options, args) = parser.parse_args()

    if len(args) < 3:
        parser.error("Invalid number of arguments")

    (server_name, admin_account, admin_password) = args

    if options.quiet and options.debug:
        parser.error("Cannot specify debug and quiet at the same time.")

    if options.quiet:
        logging.basicConfig(level=logging.ERROR)
    elif options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug("Starting followup-agent.")

    logging.debug("Authenticating as administrator to get users and domain "
                  "preauth")

    server_url = "https://%s:7071/service/admin/soap" % server_name

    comm = Communication(server_url)

    token = auth.authenticate(server_url,
                              admin_account, admin_password, admin_auth=True)

    users = []

    if options.distlist:

        logging.debug("Retrieving distribution list members from list %s" % (
            options.distlist
        ))

        get_members_request = comm.gen_request(token=token)
        get_members_request.add_request(
            "GetDistributionListRequest",
            {
                "dl": {
                    "_content": options.distlist,
                    "by": "name"
                }
            },
            "urn:zimbraAdmin"
        )
        get_members_response = comm.send_request(get_members_request)

        if get_members_response.is_fault():

            raise Exception(
                "Error loading distribution list members: (%s) %s" % (
                    get_members_response.get_fault_code(),
                    get_members_response.get_fault_message()
                )
            )

        else:

            for user in get_members_response.get_response()[
                    "GetDistributionListResponse"]["dl"]["dlm"]:

                users.append(user["_content"])

    else:

        get_users_request = comm.gen_request(token=token)

        param = {}

        if options.domain:

            logging.debug("Loading users from domain %s" % options.domain)

            param["domain"] = {
                "by": "name",
                "_content": options.domain
            }

        else:

            logging.debug("Fetching all users")

        get_users_request.add_request(
            "GetAllAccountsRequest",
            param,
            "urn:zimbraAdmin"
        )

        get_users_response = comm.send_request(get_users_request)

        if get_users_response.is_fault():

            raise Exception(
                "Error loading users: (%s) %s" % (
                    get_users_response.get_fault_code(),
                    get_users_response.get_fault_message()
                )
            )

        else:

            for user in get_users_response.get_response()[
                    "GetAllAccountsResponse"]["account"]:

                users.append(user["name"])

    preauth_cache = {}

    for user in users:

        logging.debug("Checking user %s" % user)

        (local_part, domain_part) = user.split("@")

        if domain_part not in preauth_cache:

            logging.debug("Fetching preauth key for domain %s" % domain_part)

            get_pak_request = comm.gen_request(token=token)

            get_pak_request.add_request(
                "GetDomainRequest",
                {
                    "domain": {
                        "by": "name",
                        "_content": domain_part
                    }
                },
                "urn:zimbraAdmin"
            )

            get_pak_response = comm.send_request(get_pak_request)

            if get_pak_response.is_fault():

                raise Exception(
                    "Error loading domain preauth "
                    "key for domain %s: (%s) %s" % (
                        domain_part,
                        get_pak_response.get_fault_code(),
                        get_pak_response.get_fault_message()
                    )
                )

            pak = ""

            for parameter in get_pak_response.get_response()[
                    "GetDomainResponse"]["domain"]["a"]:

                if parameter["n"] == "zimbraPreAuthKey":

                    pak = parameter["_content"]

            if pak == "":

                raise Exception(
                    "Cannot find preauth key for domain %s. "
                    "Please use zmprov gdpak %s first." % (
                        domain_part, domain_part
                    )
                )

            preauth_cache[domain_part] = str(pak)

        # Get zimlet properties

        get_account_request = comm.gen_request(token=token)

        get_account_request.add_request(
            "GetAccountRequest",
            {
                "account": {
                    "by": "name",
                    "_content": user
                }
            },
            "urn:zimbraAdmin"
        )

        get_account_response = comm.send_request(get_account_request)

        if get_account_response.is_fault():

            raise Exception(
                "Cannot get account properties for account %s: (%s) %s" % (
                    user,
                    get_account_response.get_fault_code(),
                    get_account_response.get_fault_message()
                )
            )

        zimlet_props = {}

        for prop in get_account_response.get_response()[
                "GetAccountResponse"]["account"]["a"]:

            tmp_prop = re.match(
                "^de_dieploegers_followup:([^:]*):(.*)$",
                prop["_content"]
            )

            if tmp_prop:

                zimlet_props[tmp_prop.group(1)] = tmp_prop.group(2)

        if len(zimlet_props.items()) == 0 or \
            "followupFolderId" not in zimlet_props or \
                "followupTagName" not in zimlet_props:

            # No zimlet properties set. Move on

            logging.debug("User is not using zimlet")

            continue

        logging.debug("Authenticating as user")

        user_token = auth.authenticate(
            "https://%s/service/soap" % server_name,
            user,
            preauth_cache[domain_part]
        )

        # Get mails in followup-folder

        logging.debug("Opening followup folder")

        search_request = comm.gen_request(token=user_token)

        search_request.add_request(
            "SearchRequest",
            {
                "types": "message",
                "fetch": "all",
                "query": {
                    "_content": "inid:%s" % zimlet_props["followupFolderId"]
                }
            },
            "urn:zimbraMail"
        )

        search_response = comm.send_request(search_request)

        if search_response.is_fault():

            raise Exception(
                "Cannot fetch mails in followup folder: (%s) %s" % (
                    search_response.get_fault_code(),
                    search_response.get_fault_message()
                )
            )

        if "m" not in search_response.get_response()["SearchResponse"]:

            # No mails found

            logging.info("No mails found.")

            mails = []

        else:

            mails = search_response.get_response()["SearchResponse"]["m"]

        if isinstance(mails, dict):

            mails = [mails]

        for mail in mails:

            logging.debug("Mail %s (%s)" % (mail["id"], mail["su"]))

            mail_date = datetime.fromtimestamp(long(mail["d"])/1000)

            if mail_date <= datetime.now():

                # Mail is due

                logging.info("Mail %s is due for followup. (%s)" % (
                    mail["id"],
                    mail["su"]
                ))

                logging.debug("Tagging it.")

                tag_request = comm.gen_request(token=user_token)

                tag_request.add_request(
                    "MsgActionRequest",
                    {
                        "action": {
                            "id": mail["id"],
                            "op": "tag",
                            "tn": zimlet_props["followupTagName"]
                        }
                    },
                    "urn:zimbraMail"
                )

                tag_response = comm.send_request(tag_request)

                if tag_response.is_fault():

                    raise Exception(
                        "Cannot tag mail: (%s) %s" % (
                            tag_response.get_fault_code(),
                            tag_response.get_fault_message()
                        )
                    )

                logging.debug("Moving it back to inbox")

                move_request = comm.gen_request(token=user_token)

                move_request.add_request(
                    "MsgActionRequest",
                    {
                        "action": {
                            "id": mail["id"],
                            "op": "move",
                            "l": ZIMBRA_INBOX_ID
                        }
                    },
                    "urn:zimbraMail"
                )

                move_response = comm.send_request(move_request)

                if move_response.is_fault():

                    raise Exception(
                        "Cannot move mail to followup folder: (%s) %s" % (
                            move_response.get_fault_code(),
                            move_response.get_fault_message()
                        )
                    )

                logging.debug("Setting mail to unread")

                unread_request = comm.gen_request(token=user_token)

                unread_request.add_request(
                    "MsgActionRequest",
                    {
                        "action": {
                            "id": mail["id"],
                            "op": "!read"
                        }
                    },
                    "urn:zimbraMail"
                )

                unread_response = comm.send_request(unread_request)

                if unread_response.is_fault():

                    raise Exception(
                        "Cannot set mail to unread: (%s) %s" % (
                            unread_response.get_fault_code(),
                            unread_response.get_fault_message()
                        )
                    )

            else:

                logging.debug("Not due. Skipping")

    logging.debug("Done.")
