# Contribution Guidelines

Contributions to this Blueprint are very welcome! We follow a fairly standard [pull request 
process](https://help.github.com/articles/about-pull-requests/) for contributions, subject to the following guidelines:
 
1. [File a GitHub issue](#file-a-github-issue)
1. [Update the documentation](#update-the-documentation)
1. [Update the tests](#update-the-tests)
1. [Update the code](#update-the-code)
1. [Create a pull request](#create-a-pull-request)
1. [Merge and release](#merge-and-release)

## File a GitHub issue

Before starting any work, we recommend filing a GitHub issue in this repo. This is your chance to ask questions and
get feedback from the maintainers and the community before you sink a lot of time into writing (possibly the wrong) 
code. If there is anything you're unsure about, just ask!

## Update the documentation

We recommend updating the documentation *before* updating any code (see [Readme Driven 
Development](http://tom.preston-werner.com/2010/08/23/readme-driven-development.html)). This ensures the documentation 
stays up to date and allows you to think through the problem at a high level before you get lost in the weeds of 
coding.

## Update the tests

We also recommend updating the automated tests *before* updating any code (see [Test Driven 
Development](https://en.wikipedia.org/wiki/Test-driven_development)). That means you add or update a test case, 
verify that it's failing with a clear error message, and *then* make the code changes to get that test to pass. This 
ensures the tests stay up to date and verify all the functionality in this Blueprint, including whatever new 
functionality you're adding in your contribution. In this case, this means ensure there are instructions or terraform
modules in sample-deploy/ that generates infrastructure that can be checked by the scanner.  The sample should include
a passing and a failing variant of the infrastructure targeted by the test.  Check out the 
[tests](https://github.com/hashicorp/terraform-azurerm-vault/tree/master/tests) folder for instructions on running the 
automated tests. 

## Update the code

At this point, make your code changes and use your new test case to verify that everything is working. As you work,
keep in mind these things:

1. Backwards compatibility
1. Account independence
1. Sane defaults

### Backwards compatibility

Please make every effort to avoid unnecessary backwards incompatible changes. With Terraform code, this means:

1. Do not delete, rename, or change the type of input variables.
1. If you add an input variable, it should have a `default`.
1. Do not delete, rename, or change the type of output variables.
1. Do not delete or rename a module in the `modules` folder.

If a backwards incompatible change cannot be avoided, please make sure to call that out when you submit a pull request, 
explaining why the change is absolutely necessary. 

### Account independence

Ensure as much as possible that you are wiping clean any resource-group, subscription etc for your tests.

### Sane defaults

Make a best effort to reduce the number of required variables to a minimum by supplying sane (secure) defaults 
whenever possible.

## Create a pull request

[Create a pull request](https://help.github.com/articles/creating-a-pull-request/) with your changes. Please make sure
to include the following:

1. A description of the change, including a link to your GitHub issue.
1. The output of your automated test run, preferably in a [GitHub Gist](https://gist.github.com/). We cannot run 
   automated tests for pull requests automatically due to [security 
   concerns](https://circleci.com/docs/fork-pr-builds/#security-implications), so we need you to manually provide this 
   test output so we can verify that everything is working.
1. Any notes on backwards incompatibility or downtime.

## Merge and release   

The maintainers for this repo will review your code and provide feedback. If everything looks good, they will merge the
code and release a new version, which you'll be able to find in the [releases page](../../releases).