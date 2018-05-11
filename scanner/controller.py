import utils
import sql_auditing

print("Checking to see if there is an Azure account associated with this session.")
account_list = utils.call("az account list")

if("[]" in account_list) :
    print("No Azure account associated with this session. Please authenticate to continue.")
    utils.call("az login")
    account_list = utils.call("az account list")

print("Your available subscriptions are: \n" + account_list)

current_account = utils.call("az account show")
print("Your Azure account is currently operating under the following context: \n" + current_account)

# subscriptionId = input("If you wish to switch to a different context, then specify the subscription identifier of the context that you wish to switch to. Otherwise, hit enter: \n")
#
# while subscriptionId :
#     if utils.verifySubscriptionIdFormat(subscriptionId) :
#         current_account = utils.call("az account set --subscription "+subscriptionId)
#         print("Your Azure account is currently operating on the following subscription: \n" + current_account)
    #   subscriptionId = input("If you wish to switch to a different context, then specify the subscription identifier of the context that you wish to switch to. Otherwise, hit enter: \n")
    #else :
    #    subscriptionId = input("Invalid subscription ID. Please enter the subscription ID of the context that you wish to switch to. Otherwise, hit enter: \n")

# print("Continuing in the current context!")

sql_auditing.run_tests()