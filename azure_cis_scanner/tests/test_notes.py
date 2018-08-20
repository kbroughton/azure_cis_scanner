
# TODO: Turn these into real tests


def test_incompatible_subscription_and_tenant():
    """
    azscanner(subscription_id, tenant_id) where subscription_id does not belong to tenant_id should fail with useful error
    """
    pass

def test_invalid_subscription_id():
    pass

def test_no_subscription_id():
    pass

def test_empty_azure_config_dir():
    """
    What happens if ~/.azure is empty
    """
    pass

def test_expired_credentials():
    """
    Correct behavior if session tokens have expired
    """
    pass

def test_specify_non_default_tenant():
    """
    If we have multiple tenants and pass the non-default, ensure we target the correct one.
    
    mock the azureProfiles.json and test that we get get_credentials_from_cli is called on the right data.
    create the parser
    azure_cis_scanner.set_credentials_tuples()
    """
    pass

def test_unicode_insert_error():
    """
    Cannot decode byte 0xef in ~/.azure/azureProfile.json
    Find cause of why invisible bytes are inserted.
    Fix is to open the file and delete the invisible bytes before the first '{'
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xef in position 0: ordinal not in range(128)
    """
# In addition, we should use vagrant or azure deployments of the scanner to Ubuntu and Windows virtual machines
# to ensure cross-platform behavior.
    pass