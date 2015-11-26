package de.dieploegers.followup;

import com.zimbra.common.service.ServiceException;
import com.zimbra.cs.extension.ExtensionException;
import com.zimbra.cs.extension.ZimbraExtension;
import com.zimbra.soap.SoapServlet;

/**
 * Zimbra Serverextension for the FollowUp-Zimlet
 *
 * @author Dennis Plöger <develop@dieploegers.de> *
 */

public class FollowupExtension implements ZimbraExtension{

    /**
     * Returns the name of this extension
     *
     * @return Name
     */
    @Override
    public String getName() {
        return "FollowupExtension";
    }

    /**
     * Initializes the extension
     *
     * @throws ExtensionException
     * @throws ServiceException
     */
    @Override
    public void init() throws ExtensionException, ServiceException {

        SoapServlet.addService("SoapServlet", new FollowupDocumentService
            ());

    }

    @Override
    public void destroy() {

    }
}
