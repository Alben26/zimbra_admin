package de.dieploegers.followup;

import com.zimbra.soap.DocumentDispatcher;
import com.zimbra.soap.DocumentService;

import javax.xml.namespace.QName;

/**
 * Document part of the Zimbra server extension
 *
 * @author Dennis Plöger <dennis.ploeger@getit.de>
 */

public class FollowupDocumentService implements DocumentService{

    /**
     * Register the document handlers to the dispatcher
     *
     * @param dispatcher Zimbra's document dispatcher
     */

    @Override
    public void registerHandlers(DocumentDispatcher dispatcher) {

        dispatcher.registerHandler(ModifyMailDateHandler.REQUEST_QNAME,
            new ModifyMailDateHandler());

    }
}
