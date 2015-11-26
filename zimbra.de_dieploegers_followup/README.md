# E-Mail followup-Zimlet for Zimbra Collaboration Server 8.5

## Introduction

This zimlet (and the associated server extension and agent) provide the 
functionality to create followup E-Mails for the Zimbra Collaboration Server 
versions 8.5 and up.

## Prerequisites

* [Zimbra Collaboration Server] [zimbra] versions 8.5 and up
* [Python] [python] 2.7 (currently not Python 3 compatible!)
* [Python zimbra library] [python-zimbra] versions 2.0 and up

## Components

### Zimlet

The zimlet provides the basic user interface, that lets users create followup
 emails at different points of time. 
 
The mail is mvoed to a user defined folder with its date set to the follow-up 
time. When the follow-up time is due, the mail is moved 
back to the inbox, tagged with a user defined tag and set to unread.

Clicking on the mail users can see, that the mail was deferred and can even 
lookup a history.

This zimlet uses parts of the Inbox Zero-Zimlet made by andyc available at 
the [Zimlet gallery] [originalzimlet] 
(more information available at the 
[Inbox Zero Website] [inboxzero])

It also includes the "json"-enabler by Doug Crockford available at its
[Github Repository] [json]. 
 
It relies on the server extension to set the date on followup emails.
 
### Server extension

The server extension provides a SOAP request to set the date on a specific 
mail. 
 
### Agent

The agent is a Python script, that looks periodically for E-Mails that are due
 to followup, moves that mails back into the inbox, flags them as "unread" 
 and tags them.

## Warning

When a followup e-mail is due, the mail moves back into the inbox folder. To 
make the e-mail visible to the user, it moves to the top of the inbox. To 
achieve this, the receive date of that mail is modified inside the Zimbra 
store.
  
The original received date of the e-mail as included in the e-mail's header 
is not modified.

If this goes against your company's compliance is up to you.

## Installation

### Zimlet

The zimlet may be installed as usual, either using the Zimbra Administration 
Console or the zmzimletctl tool.

### Server extension

Create the directory "de.dieploegers.followup" in "/opt/zimbra/lib/ext" under
 the root user and copy the jar file there. Restart the mailbox daemon to 
 activate the extension.
 
### Agent

Copy the files into some directory on your zimbra server (or another server, 
that matches the prerequisites).  
After that, start the agent using

python followup.py <Zimbra-Servername> <Administrative user> <Administrative 
password>

This will check all accounts on the server for followup mails.

You can also specify

* -o <domain>: Only users from this domain
* -l <list>: Only users from this distribution list

## Building

### Server extension

To build the server extension, create a file "build.properties" and configure
 the properties included in build_dist.properties to your liking.
 
Run "ant" to just build the extension's jar-file.

Use "ant deployrestart" to also deploy the jar file to your zimbra server and
 restart the mailbox daemon. (Leave out "restart" if you don't want to restart)
 
## Converting from eu_zedach_emaildefer

This zimlet is a fork of eu_zedach_emaildefer, which is abandoned. If you're
already using that zimlet, you can copy the user properties to the new zimlet
by calling the following lines as zimbra-user on your zimbra server:

    for USER in `zmprov -l gaa`
    do
      zmprov ma $USER `zmprov -z ga $USER | grep eu_zedach_emaildefer | sed -re "s/: / /gi" | sed -re "s/eu_zedach_emaildefer/de_deploegers_followup/gi" | paste -d " " -s`
    done
    
(There may be errors for users, that haven't set up the 
eu_zedach_emaildefer-zimlet!)

If all works and you'd like to remove the old eu_zedach_emaildefer 
properties, run this script:

    for USER in `zmprov -l gaa`
    do
      zmprov ma $USER `zmprov -z ga $USER | grep eu_zedach_emaildefer | sed -re "s/^/-/gi" | sed -re "s/: / /gi" | paste -d " " -s`
    done
    
Again, there may be errors.

[zimbra]: http://www.zimbra.com
[python]: http://www.python.org
[python-zimbra]: https://github.com/Zimbra-Community/python-zimbra
[originalzimlet]: http://gallery.zimbra.com/type/zimlet/inbox-zero-zimbra
[inboxzero]: http://inboxzero.com/inboxzero/
[json]: https://github.com/douglascrockford/JSON-js
