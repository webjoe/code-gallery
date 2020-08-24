# Klaviyo Code Gallery - Submission Process

The Klaviyo Code Gallery is a project built by the Sales Enablement Team. It's meant to house public code snippets for developers to reference when using Klaviyo's APIs or using Django in email templates. The goal of this project is to help enhance Klaviyo's developer experience.

All code examples are contained in this repository and should go in the folder under `entries`

This README.md file will go over who can submit their code snippets, what types of snippets are best suited for the code gallery, and the process of how to submit your code snippets.

## What types of code should be submitted to the code gallery?

There's no real limit to what you can and can't submit to be included in the code gallery. Any one-off scripts you've used in the past, any code you've written that does a particular action in Klaviyo, or any cool logic you've implemented in an email template are all great things that should be publicly documented, rather than having us Klaviyos as a bottleneck.

Examples of code that would fit in well:

1. Sending a custom metric to Klaviyo through the APIs.

2. Front-end code that subscribes somebody to a list upon submission of a custom form.

3. Pulling profile data from Klaviyo on an hourly basis to pump into a data warehouse.

... and many more examples.

## What types of code should _not_ be submitted to the code gallery?

Not many examples would fall outside of the purview of the code gallery, but a couple that come to mind are:

1. Full fledged applications.

2. Scripts that don't necessarily interact with Klaviyo (note: if you have a script that doesn't interact with Klaviyo, but it does something to help get them to a state where the data is then ready to be used in some way, that **should** be included, just please write up a detailed description for what the script does and list use cases).

If you are unsure, submit the code anyway, and we can vet it from there.

## Who can submit code to the code gallery

Anybody! If you have code you've written that could be useful to an external developer, it doesn't matter who submits!

**NOTE:** Please go through the gallery first to determine if this is something that has already been submitted.

## How to submit to the code gallery (for now!)

In the future, we should allow for external developers to contribute to the code gallery. For now, it will just be Klaviyos who have this ability.

The process is as follows:

1. Clone the repository and/or pull down the code from the master branch [here](https://github.com/klaviyo/code-gallery) `git clone git@github.com:klaviyo/code-gallery.git` , or if you already have it locally, `$ git pull origin master`

2. Make a new branch `$ git checkout -b your-branch`

3. Add your files to its **own folder** locally, even if you only have one file. The folders should be grouped by gallery entry so if you plan to contribute, for example, 3 code snippets, please create 3 separate folders with the related files.

4. In your folder(s), include a settings.json file along with the actual code you're committing. More info on formatting below.

5. Commit your changes to github: `$ git add .` then `$ git commit -m "message"`, and finally `git push origin your-branch`

6. Then, create a pull request and tag Connor Barley on Github (`@cbarley10`)

7. The Sales Enablement Team will then review the pull request, add comments, and merge your code.

## File Naming

### Folders

Each submission to the code gallery needs to be in its own folder inside of the `entries` folder. Name the folder something unique and descriptive.

**Example:** `pull-profiles-from-list`.

The folder names should be lowercase and separated by **dashes**, not underscores.

### Files

The file names should be something similar to the folder-name. Given the example above, if I have one file, the name should be something like:

`pull-profiles-from-list.js`

If pushing multiple files, add them to your folder and name those similarly.

## Settings.json

Inside of your `settings.json` file, the following fields should be included:

1.  **title** - a good descriptive name for your snippet.
2.  **platform** - one of the following: **shopify**, **bigcommerce**, **magento**, **magento_two**, **api**, **woocommerce**, **sfcrm**, **sfcc**.
3.  **tags** - an object that accepts two arrays: **platforms**, **product_areas**. **platforms** can be any of the above from #2. **product_areas** can be one of **data-in** **data-out**, or **message-templating**.
4.  **mainLanguage** - the language the snippet was written in. can be any of javascript, **htmlmixed**, **django**, **python**, **react**, **ruby**, **php**, or **java**.
5.  **code_urls** - an array of urls that the code being submitted can be reached at.
6.  **difficulty** - can be one of **difficult**, **easy**, or **medium**.
7.  **description** - a detailed description of what the snippet does and how to implement it.

Here's an example:

    {
        title: "Fetch Leads from Klaviyo and insert into SFDC",
        platform: "sfcrm",
        mainLanguage: "java",
        tags: {
          platforms: ["sfcrm"],
          product_areas: ["data-out"],
        },
        code_urls: [
          "https://github.com/klaviyo/code-gallery/blob/master/apex-klaviyo-fetch-data/FetchLeads.cls",
        ],
        difficulty: "difficult",
        description:
          "Apex script that should be inserted into Salesforce that runs once a day to pull new Klaviyo profiles into Salesforce CRM. This checks to see if the Lead exists, and if it does not, it will create a new one",
    }

# Conclusion

When in doubt, make a PR, and we can decide what to do in the comments! The only way we make this project as strong as possible is if we _all_ contribute. If you have any questions, reach out directly to Connor Barley on Slack (`@connor.barley`), or reach out to the Sales Enablement Team.
