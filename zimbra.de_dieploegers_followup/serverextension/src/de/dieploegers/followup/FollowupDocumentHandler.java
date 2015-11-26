package de.dieploegers.followup;

import com.zimbra.common.service.ServiceException;
import com.zimbra.common.soap.Element;
import com.zimbra.common.soap.MailConstants;
import com.zimbra.cs.mailbox.MailItem;
import com.zimbra.cs.mailbox.Mailbox;
import com.zimbra.cs.mailbox.OperationContext;
import com.zimbra.soap.DocumentHandler;
import com.zimbra.soap.ZimbraSoapContext;
import org.dom4j.Namespace;
import org.dom4j.QName;

import java.util.Map;

/**
 * Document handler used in Document service
 *
 * @author Dennis Plöger <dennis.ploeger@getit.de>
 */

public class FollowupDocumentHandler extends DocumentHandler{

    public static final Namespace REQUEST_NAMESPACE = Namespace.get
        ("urn:followup");


    /**
     * Handle our SOAP request (Overridden by real handler)
     *
     * @param request The request XML
     * @param context The context
     * @return
     * @throws ServiceException
     */

    @Override
    public Element handle(Element request, Map<String, Object> context) throws ServiceException {

        return null;

    }
}
