package de.dieploegers.followup;

import com.zimbra.common.service.ServiceException;
import com.zimbra.common.soap.Element;
import com.zimbra.common.soap.MailConstants;
import com.zimbra.cs.mailbox.MailItem;
import com.zimbra.cs.mailbox.Mailbox;
import com.zimbra.cs.mailbox.OperationContext;
import com.zimbra.soap.ZimbraSoapContext;
import org.dom4j.QName;

import java.util.Map;

/**
 * Change the date of a given mail.
 *
 * <ModifyMailDateRequest xmlns="urn:followup">
 *     <!-- The mail to modify -->
 *     <m id="{item-id}" d="{new date as epoch} />
 * </ModifyMailDateRequest>
 *
 * If everything went fine, you get the same data back:
 *
 * <ModifyMailDateRespone>
 *     <!-- The mail to modify -->
 *     <m id="{item-id}" d="{new date as epoch} />
 * </ModifyMailDateResponse>
 *
 * If the date differed, something went wrong.
 */

public class ModifyMailDateHandler extends FollowupDocumentHandler {

    /**
     * The Request-Name for this handler
     */

    public static final QName REQUEST_QNAME = QName.get(
        "ModifyMailDateRequest",
        FollowupDocumentHandler.REQUEST_NAMESPACE
    );

    /**
     * The Response-Name for this handler
     */

    public static final QName RESPONSE_QNAME = QName.get(
        "ModifyMailDateResponse",
        FollowupDocumentHandler.REQUEST_NAMESPACE
    );

    @Override
    public Element handle(Element request, Map<String,
        Object> context) throws ServiceException {

        Element message = request.getElement(MailConstants.E_MSG);

        Integer messageId = Integer.parseInt(
            message.getAttribute(MailConstants.A_ID)
        );

        Long newDate = Long.parseLong(
            message.getAttribute(MailConstants.A_DATE)
        );

        ZimbraSoapContext zsc = getZimbraSoapContext(context);
        Mailbox mbox = getRequestedMailbox(zsc);

        OperationContext octxt = new OperationContext(mbox);
        mbox.setDate(octxt, messageId, MailItem.Type.MESSAGE, newDate);

        Element response = zsc.createElement(RESPONSE_QNAME);

        Element m = response.addUniqueElement(MailConstants.E_MSG);

        MailItem newItem = mbox.getItemById(octxt, messageId,
            MailItem.Type.MESSAGE);

        m.addAttribute(MailConstants.A_ID, newItem.getId());

        /**
         * Zimbra internally removes the milliseconds. So for the response,
         * we add them back.
         */

        m.addAttribute(MailConstants.A_DATE, newItem.getDate() + newDate %
            1000);

        return response;

    }
}
